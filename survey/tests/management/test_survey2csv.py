# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from survey.management.survey2csv import Survey2CSV
from survey.models.answer import AnswerText
from survey.models.question import Question
from survey.models.response import Response
from survey.models.survey import Survey
from survey.tests import BaseTest


class TestSurvey2CSV(BaseTest):

    """ Permit to check if export result is working as intended. """

    def setUp(self):
        BaseTest.setUp(self)
        self.survey = Survey.objects.create(
            name="TestSurvey", is_published=True, need_logged_user=True,
            display_by_question=True,
        )
        self.q1 = Question.objects.create(text="A?", order=1, required=True,
                                          survey=self.survey)
        self.q2 = Question.objects.create(text="B?", order=2, required=False,
                                          survey=self.survey)
        self.q3 = Question.objects.create(text="C?", order=3, required=True,
                                          survey=self.survey)
        self.response = Response.objects.create(survey=self.survey,
                                                user=User.objects.all()[0])
        self.a1 = AnswerText.objects.create(response=self.response,
                                            question=self.q1,
                                            body=u"1")
        self.a2 = AnswerText.objects.create(response=self.response,
                                            question=self.q2,
                                            body=u"2")
        self.a3 = AnswerText.objects.create(response=self.response,
                                            question=self.q3,
                                            body=u"3")
        self.response_null = Response.objects.create(survey=self.survey,
                                                     user=User.objects.all()[1])
        self.empty3 = AnswerText.objects.create(response=self.response_null,
                                                question=self.q3,
                                                body="")

    def test_get_header_and_order(self):
        header, order = Survey2CSV.get_header_and_order(self.survey)
        self.assertEqual(header, [u'user', u'A?', u'B?', u'C?'])
        self.assertEqual(len(order), 4)

    def test_get_survey_as_csv(self):
        self.assertEqual(
            Survey2CSV.survey_to_csv(self.survey),
            [u'user,A?,B?,C?',
             u'ps250112,1,2,3',
             u'pierre,NAA,NAA,']
        )
