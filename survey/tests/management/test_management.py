# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from survey.models.answer import AnswerText
from survey.models.question import Question
from survey.models.response import Response
from survey.models.survey import Survey
from survey.tests import BaseTest


class TestManagement(BaseTest):

    """ Permit to check if export result is working as intended. """

    def setUp(self):
        BaseTest.setUp(self)
        self.survey = Survey.objects.create(
            name="TestManagementSurvey", is_published=True,
            need_logged_user=True, display_by_question=True,
        )
        self.q1 = Question.objects.create(text="Aè?", order=1, required=True,
                                          survey=self.survey)
        self.q2 = Question.objects.create(text="Bè?", order=2, required=False,
                                          survey=self.survey)
        self.q3 = Question.objects.create(text="Cè?", order=3, required=True,
                                          survey=self.survey)
        self.response = Response.objects.create(survey=self.survey,
                                                user=User.objects.all()[0])
        self.response_null = Response.objects.create(
            survey=self.survey, user=User.objects.all()[1]
        )
        self.a2 = AnswerText.objects.create(response=self.response,
                                            question=self.q2,
                                            body=u"2é")
        self.empty3 = AnswerText.objects.create(response=self.response_null,
                                                question=self.q3,
                                                body="")
        self.a1 = AnswerText.objects.create(response=self.response,
                                            question=self.q1,
                                            body=u"1é")
        self.a3 = AnswerText.objects.create(response=self.response,
                                            question=self.q3,
                                            body=u"3é")

        self.expected_content = [
            u'user,Aè?,Bè?,Cè?',
            u'ps250112,1é,2é,3é',
            u'pierre,NAA,NAA,'
        ]
        self.expected_header = [u'user', u'Aè?', u'Bè?', u'Cè?']
