# -*- coding: utf-8 -*-


from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from future import standard_library

from survey.management.exporter.tex.question2tex import Question2Tex
from survey.tests.management.test_management import TestManagement

standard_library.install_aliases()
try:
    from _collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class TestQuestion2Tex(TestManagement):

    def test_get_chart(self):
        """ The header and order of the question is correct. """
        question = self.survey.questions.get(text="Aèbc?")
        self.assertIsNotNone(Question2Tex.chart(question))
        colors = OrderedDict()
        colors["1b"] = "green!80"
        colors["1a"] = "cyan!50"
        colors["1é"] = "red!80"
        self.assertRaises(ValueError, Question2Tex.chart, question,
                          colors=colors)
        colors["1"] = "yellow!70"
        chart = Question2Tex.chart(question, colors=colors)
        self.assertIn("{red!80, yellow!70, cyan!50, green!80}", chart)
        self.assertIn("""1/1é,
            1/1,
            1/1a,
            1/1b""", chart)

    def test_cloud_chart(self):
        """ We can create a cloud chart. """
        question = self.survey.questions.get(text="Aèbc?")
        self.assertIsNotNone(Question2Tex.chart(question, cloud=True))
        self.assertRaises(ValueError, Question2Tex.chart, question, cloud=True,
                          pie=True)

    def test_no_results(self):
        """ We manage having no result at all. """
        question = self.survey.questions.get(text="Aèbc?")
        self.assertIn("No answers for this question.",
                      Question2Tex.chart(question, min_cardinality=2))

    def test_html2latex(self):
        """ We correctly translate a question to the latex equivalent. """
        translation = Question2Tex.html2latex("&lt;filetype&gt; ?")
        self.assertEqual("<filetype> ?", translation)
        translation = Question2Tex.html2latex("Is <strong>42</strong> true ?")
        self.assertEqual("Is \\textbf{42} true ?", translation)
        translation = Question2Tex.html2latex("<code>is(this).sparta</code>?")
        self.assertEqual("$is(this).sparta$?", translation)
