# -*- coding: utf-8 -*-

from django.urls.base import reverse

from survey.tests.management.test_management import TestManagement


class TestSurveyResult(TestManagement):

    def test_survey_result(self):
        response = self.client.get(reverse("survey-result", args=(3,)),
                                   follow=True)
        self.assertEqual(response.status_code, 404)
        self.login()
        response = self.client.get(reverse("survey-result", args=(3,)),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
