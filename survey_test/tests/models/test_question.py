# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from survey.models import Question
from survey_test.tests.models.base_model_test import BaseModelTest


class TestQuestion(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        self.assertIsNotNone(str(self.question))

    def test_get_choices(self):
        """ We can get a list of choices for a widget from choices text. """
        self.question.choices = "aa,bb"
        self.assertEqual(self.question.get_choices(),
                         (('Aa', 'Aa'), ('Bb', 'Bb')))
        self.question.choices = "aa,  ,cc"
        self.assertEqual(self.question.get_choices(),
                         (('Aa', 'Aa'), ('Cc', 'Cc')))

    def test_validate_choices(self):
        """  List are validated for comma. """
        question = Question.objects.create(
            text="Q?", choices="a,b,c", order=1, required=True,
            survey=self.survey, question_type=Question.SELECT_MULTIPLE
        )
        question.choices = "a"
        self.assertRaises(ValidationError, question.save)
        question.choices = ",a"
        self.assertRaises(ValidationError, question.save)
        question.choices = "a,"
        self.assertRaises(ValidationError, question.save)
        question.choices = ",a,  ,"
        self.assertRaises(ValidationError, question.save)
