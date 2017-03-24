# -*- coding: utf-8 -*-

from survey.tests.models import BaseModelTest


class TestSurvey(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        self.assertIsNotNone(str(self.survey))
