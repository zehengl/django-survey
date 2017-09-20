# -*- coding: utf-8 -*-


from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from django.conf import settings
from future import standard_library

from survey.exporter.tex.question2tex import Question2Tex
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
        color = OrderedDict()
        groups = {'1é': ['1e', '1é', '1ë'], '2é': ['2e', '2é', '2ë'],
                  '3é': ['3e', '3é', '3ë'], }
        color["1b"] = "green!80"
        color["1a"] = "cyan!50"
        color["1é"] = "red!80"
        chart = Question2Tex.chart(question, color=color, group_together=groups)
        expected_color = settings.SURVEY_DEFAULT_PIE_COLOR
        self.assertIn(expected_color, chart)
        color["1"] = "yellow!70"
        chart = Question2Tex.chart(
            question, color=color, group_together=groups,
            sort_answer={"1b": 1, "1a": 2, "1": 3, "1é": 4}
        )
        expected_colors = ["red!80", "yellow!70", "cyan!50", "green!80"]
        for expected_color in expected_colors:
            self.assertIn(expected_color, chart)
        self.assertIn(
            "1/1b,\n            1/1a,\n            1/1,\n            4/1é",
            chart
        )
        chart = Question2Tex.chart(question, color=color, group_together=groups,
                                   sort_answer="cardinal")
        self.assertIn(
            "4/1\xe9,\n            1/1,\n            1/1a,\n            1/1b",
            chart
        )
        chart = Question2Tex.chart(
            question, color=color, group_together=groups,
            sort_answer="alphanumeric"
        )
        self.assertIn(
            "1/1,\n            1/1a,\n            1/1b,\n            4/1é",
            chart
        )
        chart = Question2Tex.chart(question, group_together=groups,
                                   sort_answer="unknown_option")
        self.assertIn(
            "1/1,\n            1/1a,\n            1/1b,\n            4/1é",
            chart
        )

    def test_cloud_chart(self):
        """ We can create a cloud chart. """
        question = self.survey.questions.get(text="Aèbc?")
        self.assertIsNotNone(Question2Tex.chart(question, type="cloud"))

    def test_get_caption(self):
        """ We can create a filtered chart with a proper caption. """
        qst = self.survey.questions.get(text="Cède?")
        mc = 0
        flt = {}
        gt = {}
        self.assertIn("2 respondant or more",
                      Question2Tex.get_caption(qst, 2, flt, gt))
        self.assertIn("excluding 'Toto' ",
                      Question2Tex.get_caption(qst, mc, ["Toto"], gt))
        self.assertIn(
            "excluding 'Toto', and 'Titi' ",
            Question2Tex.get_caption(qst, mc, ["Toto", "Titi"], gt)
        )
        self.assertIn(
            "excluding 'Toto', 'Titi', and 'Tutu' ",
            Question2Tex.get_caption(qst, mc, ["Toto", "Titi", "Tutu"], gt)
        )
        self.assertIn(
            "with 'No' standing for 'No' or 'Maybe'.",
            Question2Tex.get_caption(qst, mc, flt,
                                     {"No": ["No", "Maybe"], "Yes": ["Kay"]},
                                     {"No": 2})
        )
        # We do not signal if group_together is just a placeholder.
        self.assertIn(
            "Repartition of answers for the question 'Cède?'.",
            Question2Tex.get_caption(qst, mc, flt,
                                     {"No": ["No", "Nö", "NO"]},
                                     {"No": 2}, True, True)
        )
        self.assertIn(
            "Repartition of answers for the question 'Cède?'.",
            Question2Tex.get_caption(qst, mc, flt, {"Yes": ["Kay"]}, {"No": 2})
        )

    def test_raw_chart(self):
        """ We can create a raw chart. """
        question = self.survey.questions.get(text="Aèbc?")
        self.assertIsNotNone(Question2Tex.chart(question, type="raw"))

    def test_no_results(self):
        """ We manage having no result at all. """
        question = self.survey.questions.get(text="Dèef?")
        self.assertIn("No answers for this question.",
                      Question2Tex.chart(question))

    def test_html2latex(self):
        """ We correctly translate a question to the latex equivalent. """
        translation = Question2Tex.html2latex("&lt;filetype&gt; ?")
        self.assertEqual("<filetype> ?", translation)
        translation = Question2Tex.html2latex("Is <strong>42</strong> true ?")
        self.assertEqual("Is \\textbf{42} true ?", translation)
        translation = Question2Tex.html2latex("<code>is(this).sparta</code>?")
        self.assertEqual("$is(this).sparta$?", translation)
