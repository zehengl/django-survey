# -*- coding: utf-8 -*-


from survey.management.exporter.tex.question2tex import Question2Tex
from survey.tests.management.test_management import TestManagement


class TestQuestion2Tex(TestManagement):

    def test_get_chart(self):
        """ The header and order of the question is correct. """
        question = self.survey.questions.get(pk=9)
        self.assertIsNotNone(Question2Tex.chart(question))
        colors = {u"1b": "red!80",
                  u"1a": "cyan!50",
                  u"1é": "red!80"}
        self.assertRaises(ValueError, Question2Tex.chart, question,
                          colors=colors)
        colors[u"1"] = "yellow!70"
        chart = Question2Tex.chart(question, colors=colors)
        self.assertIn("{red!80, yellow!70, red!80, cyan!50}", chart)
        self.assertIn("""1/1e,
            1/1,
            1/1b,
            1/1a""", chart)

    def test_cloud_chart(self):
        """ We can create a cloud chart. """
        question = self.survey.questions.get(pk=9)
        self.assertIsNotNone(Question2Tex.chart(question, cloud=True))
        self.assertRaises(ValueError, Question2Tex.chart, question, cloud=True,
                          pie=True)

    def test_no_results(self):
        """ We manage having no result at all. """
        question = self.survey.questions.get(pk=9)
        print Question2Tex.chart(question, min_cardinality=2)
        self.assertIn("No answers for this question.",
                      Question2Tex.chart(question, min_cardinality=2))
