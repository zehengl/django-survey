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
        self.questions[0].choices = "A éa,B éb"
        self.assertEqual(self.questions[0].get_choices(),
                         ((u'a-ea', u'A éa'), (u'b-eb', u'B éb')))
        self.questions[0].choices = "A()a,  ,C()c"
        self.assertEqual(self.questions[0].get_choices(),
                         ((u'aa', u'A()a'), (u'cc', u'C()c')))

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

    def test_answers_as_text(self):
        """ We can get a list of answers to this question. """
        question = Question.objects.get(pk=1)
        qat = question.answers_as_text
        self.assertEqual(3, len(qat))
        expected = [u"Yës", u'Maybe', u"Yës"]
        expected.sort()
        qat.sort()
        self.assertEqual(qat, expected)

    def test_answers_cardinality(self):
        """ We can get the cardinality of each answers. """
        question = Question.objects.get(pk=1)
        self.assertEqual(question.answers_cardinality,
                         {u"Maybe": 1, u"Yës": 2})
        question = Question.objects.get(pk=2)
        self.assertEqual({u'': 2},
                         question.answers_cardinality)
        question = Question.objects.get(pk=3)
        self.assertEqual({u'': 1, u'Text for a response': 1},
                         question.answers_cardinality)
        question = Question.objects.get(pk=5)
        self.assertEqual({u'1': 2}, question.answers_cardinality)
        question = Question.objects.get(pk=6)
        self.assertEqual({u'No': 1, u'Whatever': 1, u'Yës': 1},
                         question.answers_cardinality)
