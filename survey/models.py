from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


def validate_choices(choices):
    """  Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    values = choices.split(',')
    empty = 0
    for value in values:
        if value.replace(" ", '') == '':
            empty += 1
    if len(values) < 2 + empty:
        msg = "The selected field requires an associated list of choices."
        msg += " Choices must contain more than one item."
        raise ValidationError(msg)


class Survey(models.Model):
    name = models.CharField(max_length=400)
    description = models.TextField()
    is_published = models.BooleanField()
    need_logged_user = models.BooleanField()
    display_by_question = models.BooleanField()
    template = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _('survey')
        verbose_name_plural = _('surveys')

    def __unicode__(self):
        return (self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('survey-detail', [self.id])

    def questions(self):
        if self.pk:
            return Question.objects.filter(survey=self.pk).order_by('category__order', 'order')
        else:
            return Question.objects.none()


class Category(models.Model):
    name = models.CharField(max_length=400)
    survey = models.ForeignKey(Survey)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __unicode__(self):
        return (self.name)


class Question(models.Model):
    TEXT = 'text'
    SHORT_TEXT = 'short-text'
    RADIO = 'radio'
    SELECT = 'select'
    SELECT_IMAGE = 'select_image'
    SELECT_MULTIPLE = 'select-multiple'
    INTEGER = 'integer'

    QUESTION_TYPES = (
        (TEXT, _(u'text (multiple line)')),
        (SHORT_TEXT, _(u'short text (one line)')),
        (RADIO, _(u'radio')),
        (SELECT, _(u'select')),
        (SELECT_MULTIPLE, _(u'Select Multiple')),
        (SELECT_IMAGE, _(u'Select Image')),
        (INTEGER, _(u'integer')),
    )

    text = models.TextField()
    order = models.IntegerField()
    required = models.BooleanField()
    category = models.ForeignKey(Category, blank=True, null=True,) 
    survey = models.ForeignKey(Survey)
    question_type = models.CharField(max_length=200, choices=QUESTION_TYPES, default=TEXT)
    # the choices field is only used if the question type 
    choices = models.TextField(
        blank=True, null=True, help_text=_(u"""If the question type is 'radio',
'select', or 'select multiple' provide a
comma-separated list of options for this question .""")
    )

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ('survey', 'order')

    def save(self, *args, **kwargs):
        if (self.question_type == Question.RADIO or self.question_type == Question.SELECT 
            or self.question_type == Question.SELECT_MULTIPLE):
            validate_choices(self.choices)
        super(Question, self).save(*args, **kwargs)

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices = self.choices.split(',')
        choices_list = []
        for choice in choices:
            choice = choice.strip().capitalize()
            if choice != "":
                choices_list.append((choice, choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __unicode__(self):
        return (self.text)


class Response(models.Model):
    """
    A Response object is just a collection of questions and answers with a
    unique interview uuid
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey)
    user = models.ForeignKey(User, null=True, blank=True)
    interview_uuid = models.CharField(_(u"Interview unique identifier"), max_length=36)

    class Meta:
        verbose_name = _('response')
        verbose_name_plural = _('responses')

    def __unicode__(self):
        return ("response %s" % self.interview_uuid)


class AnswerBase(models.Model):

    question = models.ForeignKey(Question, related_name="answers")
    response = models.ForeignKey(Response, related_name="answers")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        try:
            return u"{} to question '{}' : '{}'".format(
                self.__class__.__name__, self.question, self.body
            )
        except AttributeError:
            return u"AnswerBase to question '{}'".format(self.question)


class AnswerText(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerRadio(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerSelect(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerSelectMultiple(AnswerBase):
    body = models.TextField(blank=True, null=True)


class AnswerInteger(AnswerBase):
    body = models.IntegerField(blank=True, null=True)


def get_real_type_answer(answer):
    """ Permit to recover a child answer class from the AnswerBase object.
    :param AnswerBase answer: The AnswerBase to convert to its real type. """
    for class_ in [AnswerText, AnswerRadio, AnswerSelect, AnswerSelectMultiple,
                   AnswerInteger]:
        try:
            return class_.objects.get(response=answer.response,
                                      question=answer.question)
        except class_.DoesNotExist:
            continue
    # Probably a real AnswerBase
    return answer
