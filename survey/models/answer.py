# -*- coding: utf-8 -*-

"""
    These type-specific answer models use a text field to allow for flexible
    field sizes depending on the actual question this answer corresponds to any
    "required" attribute will be enforced by the form.
"""

import logging

from django.core.exceptions import ValidationError
from django.db import models

from .question import Question
from .response import Response

LOGGER = logging.getLogger(__name__)


class Answer(models.Model):

    question = models.ForeignKey(Question, related_name="answers")
    response = models.ForeignKey(Response, related_name="answers")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    body = models.TextField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        try:
            question = Question.objects.get(pk=kwargs["question_id"])
        except KeyError:
            question = kwargs.get("question")
        body = kwargs.get("body")
        if question and body:
            self.check_answer_body(question, body)
        super(Answer, self).__init__(*args, **kwargs)

    def check_answer_body(self, question, body):
        if question.type in [Question.RADIO, Question.SELECT,
                             Question.SELECT_MULTIPLE]:
            choices = question.get_clean_choices()
            if body:
                if body[0] == "[":
                    answers = []
                    for i, part in enumerate(body.split("'")):
                        if i % 2 == 1:
                            answers.append(part)
                else:
                    answers = [body]
            for answer in answers:
                if answer not in choices:
                    msg = "Impossible answer '{}'".format(body)
                    msg += " should be in {} ".format(choices)
                    raise ValidationError(msg)

    def __unicode__(self):
        return u"{} to question '{}' : '{}'".format(
            self.__class__.__name__, self.question, self.body
        )
