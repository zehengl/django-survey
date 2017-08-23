# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from builtins import str

from django.core.exceptions import ValidationError
from future import standard_library

from survey.models import Question
from survey.tests.models import BaseModelTest

standard_library.install_aliases()


class TestQuestion(BaseModelTest):

    def setUp(self):
        BaseModelTest.setUp(self)
        text = "Lorem ipsum dolor sit amët, <strong> consectetur </strong> \
adipiscing elit."
        self.question = Question.objects.get(text=text)

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
        qat = self.question.answers_as_text
        self.assertEqual(3, len(qat))
        expected = [u"Yës", u'Maybe', u"Yës"]
        expected.sort()
        qat.sort()
        self.assertEqual(qat, expected)

    def test_answers_cardinality(self):
        """ We can get the cardinality of each answers. """
        self.assertEqual(self.question.answers_cardinality(),
                         {u"Maybe": 1, u"Yës": 2})
        self.assertEqual(self.question.answers_cardinality(min_cardinality=2),
                         {"Other": 1, u"Yës": 2})
        question = Question.objects.get(text="Ipsum dolor sit amët, <strong> \
consectetur </strong>  adipiscing elit.")
        self.assertEqual({u'No': 1, "Yës": 1},
                         question.answers_cardinality())
        question = Question.objects.get(text="Dolor sit amët, <strong> \
consectetur</strong>  adipiscing elit.")
        self.assertEqual({u'': 1, u'Text for a response': 1},
                         question.answers_cardinality())
        question = Question.objects.get(text="Ipsum dolor sit amët, consectetur\
 <strong> adipiscing </strong> elit.")
        self.assertEqual({u'1': 1, "2": 1}, question.answers_cardinality())
        question = Question.objects.get(text="Dolor sit amët, consectetur<stron\
g>  adipiscing</strong>  elit.")
        self.assertEqual({u'No': 1, u'Whatever': 1, u'Yës': 1},
                         question.answers_cardinality())
        self.assertEqual(
            {u'Näh': 2, u'Yës': 1},
            question.answers_cardinality(
                group_together={"Näh": "No, Whatever"}
            )
        )
