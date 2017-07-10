# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from survey.models import Answer
from survey.tests.models import BaseModelTest


class TestAnswer(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        for answer in self.answers:
            self.assertIsNotNone(str(answer))
            self.assertIn(answer.__class__.__name__, str(answer))
        for answer in Answer.objects.all():
            self.assertIn(answer.__class__.__name__, str(answer))

    def test_init(self):
        self.assertRaises(ValidationError, Answer, response=self.response,
                          question=self.questions[5], body="Dd")
