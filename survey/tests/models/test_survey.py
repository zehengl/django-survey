# -*- coding: utf-8 -*-

from survey.tests.models import BaseModelTest


class TestSurvey(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        self.assertIsNotNone(str(self.survey))

    def test_questions(self):
        """ Recovering a list of questions from a survey. """
        questions = self.survey.questions()
        self.assertEqual(len(questions), len(self.data))

    def test_absolute_url(self):
        """ Absoulte url is not None and do not raise error. """
        self.assertIsNotNone(self.survey.get_absolute_url())
