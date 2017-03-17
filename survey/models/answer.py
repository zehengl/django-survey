# -*- coding: utf-8 -*-

from django.db import models

from .question import Question
from .response import Response


"""
    These type-specific answer models use a text field to allow for flexible
    field sizes depending on the actual question this answer corresponds to any
    "required" attribute will be enforced by the form.
"""


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
