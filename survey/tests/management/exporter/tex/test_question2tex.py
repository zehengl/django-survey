# -*- coding: utf-8 -*-


from survey.management.exporter.tex.question2tex import Question2Tex
from survey.tests.management.test_management import TestManagement


class TestQuestion2Tex(TestManagement):

    """ Permit to check if export result is working as intended. """

    def test_get_chart(self):
        """ The header and order of the question is correct. """
        for question in self.survey.questions.all():
            pass
            Question2Tex.chart(question)
