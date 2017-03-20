# -*- coding: utf-8 -*-

import logging
import uuid

from django import forms
from django.core.urlresolvers import reverse
from django.forms import models
from django.utils.safestring import mark_safe

from survey.models import (AnswerBase, AnswerInteger, AnswerRadio,
                           AnswerSelect, AnswerSelectMultiple, AnswerText,
                           Question, Response)
from survey.models.answer import get_real_type_answer
from survey.signals import survey_completed
from survey.widgets import ImageSelectWidget

LOGGER = logging.getLogger(__name__)


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    # Blatantly stolen from http://stackoverflow.com/questions/5935546/
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class HorizontalCheckboxRenderer(forms.RadioSelect.renderer):
    # Obviously an horrible hack based on HorizontalRadioRenderer.
    def render(self):
        return mark_safe(
            u'\n'.join(
                [u'{}\n'.format(w).replace("radio", "checkbox") for w in self]
            )
        )


class SelectMultipleHorizontal(forms.CheckboxSelectMultiple):
    renderer = HorizontalCheckboxRenderer


class ResponseForm(models.ModelForm):

    class Meta(object):
        model = Response
        fields = ()

    def _get_preexisting_response(self):
        """ Recover a pre-existing response in database.

        The user must be logged.
        :rtype: Response or None"""
        if not self.user.is_authenticated():
            return None
        try:
            return Response.objects.get(user=self.user, survey=self.survey)
        except Response.DoesNotExist:
            LOGGER.debug("No saved response for '%s' for user %s",
                          self.survey, self.user)
            return None

    def _get_preexisting_answer(self, question):
        """ Recover a pre-existing answer in database.

        The user must be logged. A Response containing the Answer must exists.

        :param Question question: The question we want to recover in the
        response.
        :rtype: Answer or None"""
        response = self._get_preexisting_response()
        if response is None:
            return None
        try:
            base_answer = AnswerBase.objects.get(question=question,
                                                 response=response)
            return get_real_type_answer(base_answer)
        except AnswerBase.DoesNotExist:
            return None

    def add_question(self, question, data):
        """ Add a question to the form.

        :param Question question: The question to add.
        :param dict data: The pre-existing values from a post request. """
        kwargs = {"label": question.text,
                  "required": question.required, }
        answer = self._get_preexisting_answer(question)
        if answer:
            # Initialize the field with values from the database if any
            if answer is AnswerSelectMultiple:
                kwargs["initial"] = list(answer.body)
            else:
                kwargs["initial"] = answer.body
        if question.choices:
            qchoices = question.get_choices()
            # add an empty option at the top so that the user has to explicitly
            # select one of the options
            if question.type in [Question.SELECT, Question.SELECT_IMAGE]:
                qchoices = tuple([('', '-------------')]) + qchoices
            kwargs["choices"] = qchoices
        if question.type == Question.TEXT:
            kwargs["widget"] = forms.Textarea
        elif question.type == Question.SHORT_TEXT:
            kwargs["widget"] = forms.TextInput
        elif question.type == Question.RADIO:
            kwargs["widget"] = forms.RadioSelect(
                                    renderer=HorizontalRadioRenderer
                                )
        elif question.type == Question.SELECT:
            kwargs["widget"] = forms.Select
        elif question.type == Question.SELECT_IMAGE:
            kwargs["widget"] = ImageSelectWidget
        elif question.type == Question.SELECT_MULTIPLE:
            kwargs["widget"] = forms.CheckboxSelectMultiple

        if question.type in [Question.TEXT, Question.SHORT_TEXT]:
            field = forms.CharField(**kwargs)
        elif question.type in [Question.SELECT_MULTIPLE]:
            field = forms.MultipleChoiceField(**kwargs)
        elif question.type in [Question.INTEGER]:
            field = forms.IntegerField(**kwargs)
        else:
            field = forms.ChoiceField(**kwargs)

        # add the category as a css class, and add it as a data attribute
        # as well (this is used in the template to allow sorting the
        # questions by category)
        classes = field.widget.attrs.get("class") or ''
        if question.category:
            field.widget.attrs["class"] = classes + (" cat_%s" % question.category.name)
            field.widget.attrs["category"] = question.category.name
        if question.type == Question.SELECT:
            field.widget.attrs["class"] = classes + (" cs-select cs-skin-boxes")
        if question.type == Question.RADIO:
            field.widget.attrs["class"] = classes + (" fs-radio-group fs-radio-custom clearfix")
        if question.type == Question.SELECT_MULTIPLE:
            field.widget.attrs["class"] = classes

        # initialize the field field with values from a POST request, if any.
        if data:
            field.initial = data.get('question_%d' % question.pk)
        self.fields["question_%d" % question.pk] = field

    def __init__(self, *args, **kwargs):
        """ Expects a survey object to be passed in initially """
        self.survey = kwargs.pop('survey')
        self.user = kwargs.pop('user')
        try:
            self.step = int(kwargs.pop('step'))
        except KeyError:
            self.step = None
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex
        self.steps_count = len(self.survey.questions())
        # add a field for each survey question, corresponding to the question
        # type as appropriate.
        data = kwargs.get('data')
        for i, question in enumerate(self.survey.questions()):
            if (self.survey.display_by_question and
               i != self.step and
               self.step is not None):
                continue
            else:
                self.add_question(question, data)

    def has_next_step(self):
        if self.survey.display_by_question:
            if self.step < self.steps_count - 1:
                return True
        return False

    def next_step_url(self):
        if self.has_next_step():
            context = {'id': self.survey.id, 'step': self.step + 1}
            return reverse('survey-detail-step', kwargs=context)
        else:
            return None

    def current_step_url(self):
        return reverse('survey-detail-step',
                       kwargs={'id': self.survey.id, 'step': self.step})

    def save(self, commit=True):
        """ Save the response object """
        # Recover an existing response from the database if any
        # There is only one response by logged user.
        response = self._get_preexisting_response()
        if response is None:
            response = super(ResponseForm, self).save(commit=False)
        response.survey = self.survey
        response.interview_uuid = self.uuid
        if self.user.is_authenticated():
            response.user = self.user
        response.save()
        # response "raw" data as dict (for signal)
        data = {
            'survey_id': response.survey.id,
            'interview_uuid': response.interview_uuid,
            'responses': []
        }
        # create an answer object for each question and associate it with this
        # response.
        for field_name, field_value in self.cleaned_data.iteritems():
            if field_name.startswith("question_"):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in the
                # field name in the __init__ method of this form class.
                q_id = int(field_name.split("_")[1])
                question = Question.objects.get(pk=q_id)
                answer = self._get_preexisting_answer(question)
                if answer is None:
                    if question.type in [Question.TEXT, Question.SHORT_TEXT]:
                        answer = AnswerText(question=question)
                    elif question.type == Question.RADIO:
                        answer = AnswerRadio(question=question)
                    elif question.type == Question.SELECT:
                        answer = AnswerSelect(question=question)
                    elif question.type == Question.SELECT_IMAGE:
                        answer = AnswerSelect(question=question)
                    elif question.type == Question.SELECT_MULTIPLE:
                        answer = AnswerSelectMultiple(question=question)
                    elif question.type == Question.INTEGER:
                        answer = AnswerInteger(question=question)
                if question.type == Question.SELECT_IMAGE:
                    value, img_src = field_value.split(":", 1)
                    # TODO
                answer.body = field_value
                data['responses'].append((answer.question.id, answer.body))
                LOGGER.debug(
                    "Creating %s for question %d of type %s : %s",
                     answer.question.text, q_id, answer.question.type,
                     field_value
                 )
                answer.response = response
                answer.save()
        survey_completed.send(sender=Response, instance=response, data=data)
        return response
