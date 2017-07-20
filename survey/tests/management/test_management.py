# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from django.contrib.auth.models import User
from future import standard_library

from survey.models import Answer, Question, Response, Survey
from survey.tests import BaseTest

standard_library.install_aliases()


class TestManagement(BaseTest):

    """ Permit to check if export result is working as intended. """

    def setUp(self):
        BaseTest.setUp(self)
        self.test_managament_survey_name = u"TestManagementSurvëy"
        self.survey = Survey.objects.create(
            name=self.test_managament_survey_name, is_published=True,
            need_logged_user=True, display_by_question=True,
        )
        self.qst1 = Question.objects.create(text="Aèbc?", order=1,
                                            required=True, survey=self.survey)
        self.qst2 = Question.objects.create(text="Bècd?", order=2,
                                            required=False, survey=self.survey)
        self.qst3 = Question.objects.create(text="Cède?", order=3,
                                            required=True, survey=self.survey)
        self.response = Response.objects.create(survey=self.survey,
                                                user=User.objects.all()[0])
        self.ans1 = Answer.objects.create(
            response=self.response, question=self.qst1, body=u"1é"
        )
        self.ans2 = Answer.objects.create(
            response=self.response, question=self.qst2, body=u"2é"
        )
        self.ans3 = Answer.objects.create(
            response=self.response, question=self.qst3, body=u"3é"
        )
        self.response_null = Response.objects.create(
            survey=self.survey, user=User.objects.all()[1]
        )
        self.empty = Answer.objects.create(
            response=self.response_null, question=self.qst3, body=""
        )
        self.other_response = Response.objects.create(
            survey=self.survey, user=User.objects.create(username="SlctMltipl")
        )
        Answer.objects.create(response=self.other_response, question=self.qst1,
                              body="""[u'1', u'1a', u'1b']""")
        Answer.objects.create(response=self.other_response, question=self.qst2,
                              body="""[u'2', u'2a', u'2b']""")
        Answer.objects.create(response=self.other_response, question=self.qst3,
                              body="""[u'3', u'3a', u'3b']""")
        self.expected_content = u"""\
user,Aèbc?,Bècd?,Cède?
ps250112,1é,2é,3é
pierre,,,
SlctMltipl,1|1a|1b,2|2a|2b,3|3a|3b"""
        self.expected_header = [u'user', u'Aèbc?', u'Bècd?', u'Cède?']
