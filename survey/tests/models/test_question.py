# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from survey.models import Question
from survey.tests.models import BaseModelTest


class TestQuestion(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        self.assertIsNotNone(str(self.questions[0]))

    def test_get_choices(self):
        """ We can get a list of choices for a widget from choices text. """
        self.questions[0].choices = "aa,bb"
        self.assertEqual(self.questions[0].get_choices(),
                         (('Aa', 'Aa'), ('Bb', 'Bb')))
        self.questions[0].choices = "aa,  ,cc"
        self.assertEqual(self.questions[0].get_choices(),
                         (('Aa', 'Aa'), ('Cc', 'Cc')))

    def test_validate_choices(self):
        """  List are validated for comma. """
        question = Question.objects.create(
            text="Q?", choices="a,b,c", order=1, required=True,
            survey=self.survey, type=Question.SELECT_MULTIPLE
        )
        question.choices = "a"
        self.assertRaises(ValidationError, question.save)
        question.choices = ",a"
        self.assertRaises(ValidationError, question.save)
        question.choices = "a,"
        self.assertRaises(ValidationError, question.save)
        question.choices = ",a,  ,"
        self.assertRaises(ValidationError, question.save)
