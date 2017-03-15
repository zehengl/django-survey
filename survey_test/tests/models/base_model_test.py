# -*- coding: utf-8 -*-

from survey.models import (AnswerInteger, AnswerRadio, AnswerSelect,
                           AnswerSelectMultiple, AnswerText, Question,
                           Response, Survey)
from survey_test.tests.base_test import BaseTest


class BaseModelTest(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        self.survey = Survey.objects.get(name="Test survey")
        self.response = Response.objects.create(survey=self.survey)
        self.answer_text = "3246753"
        self.answers = []
        self.question = Question.objects.filter(survey=self.survey)[0]
        self.answers.append(AnswerInteger(response=self.response,
                                          body=int(self.answer_text),
                                          question=self.question))
        for i, class_ in enumerate([AnswerText, AnswerRadio, AnswerSelect,
                       AnswerSelectMultiple]):
            body = "{}_{}".format(self.answer_text, i)
            question = Question.objects.filter(survey=self.survey)[i + 1]
            answer = class_.objects.create(response=self.response, body=body,
                                           question=question)
            self.answers.append(answer)
