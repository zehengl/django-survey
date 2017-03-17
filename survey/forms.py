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
from survey.signals import survey_completed
from survey.widgets import ImageSelectWidget


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    # Blatantly stolen from http://stackoverflow.com/questions/5935546/
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class ResponseForm(models.ModelForm):

    class Meta(object):
        model = Response
        fields = ()

    def add_question(self, question, data):
        kwargs = {"label": question.text,
                  "required": question.required, }
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
            form = forms.CharField(**kwargs)
        elif question.type in [Question.SELECT_MULTIPLE]:
            form = forms.MultipleChoiceField(**kwargs)
        elif question.type in [Question.INTEGER]:
            form = forms.IntegerField(**kwargs)
        else:
            form = forms.ChoiceField(**kwargs)

        # add the category as a css class, and add it as a data attribute
        # as well (this is used in the template to allow sorting the
        # questions by category)
        classes = form.widget.attrs.get("class") or ''
        if question.category:
            form.widget.attrs["class"] = classes + (" cat_%s" % question.category.name)
            form.widget.attrs["category"] = question.category.name
        if question.type == Question.SELECT:
            form.widget.attrs["class"] = classes + (" cs-select cs-skin-boxes")
        if question.type == Question.RADIO:
            form.widget.attrs["class"] = classes + (" fs-radio-group fs-radio-custom clearfix")
        if question.type == Question.SELECT_MULTIPLE:
            form.widget.attrs["class"] = classes

        # initialize the form field with values from a POST request, if any.
        if data:
            form.initial = data.get('question_%d' % question.pk)
        self.fields["question_%d" % question.pk] = form

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
                if question.type in [Question.TEXT, Question.SHORT_TEXT]:
                    a = AnswerText(question=question)
                    a.body = field_value
                elif question.type == Question.RADIO:
                    a = AnswerRadio(question=question)
                    a.body = field_value
                elif question.type == Question.SELECT:
                    a = AnswerSelect(question=question)
                    a.body = field_value
                elif question.type == Question.SELECT_IMAGE:
                    a = AnswerSelect(question=question)
                    value, img_src = field_value.split(":", 1)
                    a.body = value
                elif question.type == Question.SELECT_MULTIPLE:
                    a = AnswerSelectMultiple(question=question)
                    a.body = field_value
                elif question.type == Question.INTEGER:
                    a = AnswerInteger(question=question)
                    a.body = field_value
                data['responses'].append((a.question.id, a.body))
                logging.debug("Creating %s for question %d of type %s",
                              a.question.text, q_id, a.question.type)
                logging.debug('Answer value: %s', field_value)
                a.response = response
                a.save()
        survey_completed.send(sender=Response, instance=response, data=data)
        return response
