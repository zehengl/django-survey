# -*- coding: utf-8 -*-

from survey.models import AnswerBase, get_real_type_answer, Question, Survey, Response
from survey_test.tests.models.base_model_test import BaseModelTest
from survey.models.answer import AnswerText, AnswerSelectMultiple
from django.core.exceptions import ValidationError


class TestAnswer(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        for answer in self.answers:
            self.assertIsNotNone(str(answer))
            self.assertIn(answer.__class__.__name__, str(answer))
        for answer in AnswerBase.objects.all():
            self.assertIn(answer.__class__.__name__, str(answer))

    def test_get_real_type(self):
        """ We can recover the real type of an AnswerBase """
        for baseanswer in AnswerBase.objects.all():
            answer = get_real_type_answer(baseanswer)
            self.assertNotEqual(answer.__class__, AnswerBase)
        baseanswer = AnswerBase.objects.create(response=self.response,
                                               question=self.questions[0])
        answer = get_real_type_answer(baseanswer)
        self.assertEqual(answer.__class__, AnswerBase)

    def test_init(self):
        self.assertRaises(ValidationError, AnswerSelectMultiple,
                          response=self.response,
                          question=self.questions[5], body="Dd")
