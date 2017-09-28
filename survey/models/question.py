# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import logging
from builtins import object, super

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from future import standard_library

from .category import Category
from .survey import Survey

LOGGER = logging.getLogger(__name__)

standard_library.install_aliases()

try:
    from _collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


CHOICES_HELP_TEXT = _(u"""The choices field is only used if the question type
if the question type is 'radio', 'select', or
'select multiple' provide a comma-separated list of
options for this question .""")


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
    category = models.ForeignKey(Category, blank=True, null=True,
                                 related_name="questions")
    survey = models.ForeignKey(Survey, related_name="questions")
    type = models.CharField(max_length=200, choices=QUESTION_TYPES,
                            default=TEXT)
    choices = models.TextField(blank=True, null=True,
                               help_text=CHOICES_HELP_TEXT)

    class Meta(object):
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ('survey', 'order')

    def save(self, *args, **kwargs):
        if self.type in [Question.RADIO, Question.SELECT,
                         Question.SELECT_MULTIPLE]:
            validate_choices(self.choices)
        super(Question, self).save(*args, **kwargs)

    def get_clean_choices(self):
        """ Return split and stripped list of choices with no null values. """
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(','):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    @property
    def answers_as_text(self):
        """ Return answers as a list of text.

        :rtype: List """
        answers_as_text = []
        for answer in self.answers.all():
            for value in answer.values:
                answers_as_text.append(value)
        return answers_as_text

    def _cardinality_plus_n(self, cardinality, value, n):
        try:
            cardinality[value] += n
        except KeyError:
            cardinality[value] = n

    @staticmethod
    def standardize(value, group_by_letter_case=None, group_by_slugify=None):
        """ Standardize a value in order to group by slugify or letter case """
        if group_by_slugify:
            value = slugify(value)
        if group_by_letter_case:
            value = value.lower()
        return value

    @staticmethod
    def standardize_list(string_list, group_by_letter_case=None,
                         group_by_slugify=None):
        """ Return a list of standardized string from a csv string.."""
        return [
            Question.standardize(strng, group_by_letter_case, group_by_slugify)
            for strng in string_list
        ]

    def answers_cardinality(self, min_cardinality=None, group_together=None,
                            group_by_letter_case=None, group_by_slugify=None,
                            filter=None):
        """ Return a dictionary with answers as key and cardinality as value

        :rtype: Dict """
        if min_cardinality is None:
            min_cardinality = 0
        if group_together is None:
            group_together = {}
        if filter is None:
            filter = []
            standardized_filter = []
        else:
            standardized_filter = Question.standardize_list(
                filter, group_by_letter_case, group_by_slugify
            )
        cardinality = OrderedDict()
        for answer in self.answers.all():
            for value in answer.values:
                value = Question.standardize(value, group_by_letter_case,
                                             group_by_slugify)
                for key, values in group_together.items():
                    grouped_values = Question.standardize_list(
                        values, group_by_letter_case, group_by_slugify
                    )
                    if value in grouped_values:
                        value = key

                if value not in filter and value not in standardized_filter:
                    self._cardinality_plus_n(cardinality, value, 1)
        if min_cardinality != 0:
            temp = {}
            for value in cardinality:
                if cardinality[value] < min_cardinality:
                    self._cardinality_plus_n(temp, "Other", cardinality[value])
                else:
                    temp[value] = cardinality[value]
            cardinality = temp
        return cardinality

    def sorted_answers_cardinality(self, min_cardinality=None,
                                   group_together=None,
                                   group_by_letter_case=None,
                                   group_by_slugify=None, filter=None,
                                   sort_answer=None):
        """ Mostly to have reliable tests, but marginally nicer too...

        The ordering is reversed for same cardinality value so we have aa
        before zz. """
        cardinality = self.answers_cardinality(
            min_cardinality, group_together, group_by_letter_case,
            group_by_slugify, filter
        )
        if sort_answer is None or sort_answer == "alphanumeric":
            return sorted(cardinality.items())
        if type(sort_answer) is dict:
            # User defined dict
            return sorted(cardinality.items(),
                          key=lambda x: sort_answer.get(x[0]))
        if sort_answer == "cardinal":
            return sorted(cardinality.items(), key=lambda x: (-x[1], x[0]))
        LOGGER.warning(
            "Unrecognized option '%s' for 'sort_answer': %s", sort_answer,
            "use nothing, a dict (answer: rank), 'alphanumeric' or 'cardinal'."
            " We used the default alphanumeric sorting."
        )
        return sorted(cardinality.items())

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        msg = u"Question '{}' ".format(self.text)
        if self.required:
            msg += u"(*) "
        msg += u"{}".format(self.get_clean_choices())
        return msg
