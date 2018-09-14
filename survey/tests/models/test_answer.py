# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from builtins import str

from django.core.exceptions import ValidationError
from future import standard_library

from survey.models import Answer
from survey.tests.models import BaseModelTest

standard_library.install_aliases()


class TestAnswer(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        for answer in self.answers:
            self.assertIsNotNone(str(answer))

    def test_init(self):
        """ We raise validation error if the answer is not a possible choice"""
        self.assertRaises(ValidationError, Answer, response=self.response,
                          question=self.questions[4], body="Dd")

    def test_values(self):
        """ We can have multiple nasty values ans it will be detected. """
        self.assertEqual(self.answers[0].values, ["Mytext"])
        self.assertEqual(self.answers[4].values, ["Yes"])
        self.assertEqual(self.answers[6].values, ["2", "4"])
