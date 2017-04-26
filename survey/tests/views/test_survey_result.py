# -*- coding: utf-8 -*-


from survey.tests.management.test_management import TestManagement
from survey.views.survey_result import serve_result_csv


class TestSurveyResult(TestManagement):

    def test_survey_result(self):
        serve_result_csv("request", 3)
