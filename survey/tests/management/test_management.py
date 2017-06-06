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
        self.test_managament_survey_name = u"TestManagementSurvëy"
        self.survey = Survey.objects.create(
            name=self.test_managament_survey_name, is_published=True,
            need_logged_user=True, display_by_question=True,
        )
        self.qst1 = Question.objects.create(text="Aè?", order=1, required=True,
                                            survey=self.survey)
        self.qst2 = Question.objects.create(text="Bè?", order=2, required=False,
                                            survey=self.survey)
        self.qst3 = Question.objects.create(text="Cè?", order=3, required=True,
                                            survey=self.survey)
        self.response = Response.objects.create(survey=self.survey,
                                                user=User.objects.all()[0])
        self.response_null = Response.objects.create(
            survey=self.survey, user=User.objects.all()[1]
        )
        self.ans2 = AnswerText.objects.create(response=self.response,
                                              question=self.qst2,
                                              body=u"2é")
        self.empty3 = AnswerText.objects.create(response=self.response_null,
                                                question=self.qst3,
                                                body="")
        self.ans1 = AnswerText.objects.create(response=self.response,
                                              question=self.qst1,
                                              body=u"1é")
        self.ans3 = AnswerText.objects.create(response=self.response,
                                              question=self.qst3,
                                              body=u"3é")

        self.expected_content = [
            u'user,Aè?,Bè?,Cè?',
            u'ps250112,1é,2é,3é',
            u'pierre,NAA,NAA,'
        ]
        self.expected_header = [u'user', u'Aè?', u'Bè?', u'Cè?']
