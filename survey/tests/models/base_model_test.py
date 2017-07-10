# -*- coding: utf-8 -*-

from survey.models import Answer, Question, Response, Survey
from survey.tests import BaseTest


class BaseModelTest(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        self.survey = Survey.objects.create(name="Internal Test Survey",
                                            is_published=True,
                                            need_logged_user=False,
                                            display_by_question=False)
        self.response = Response.objects.create(survey=self.survey)
        self.questions = []
        self.answers = []
        self.data = {
            Question.TEXT: [Answer, "Mytext", None],
            Question.SHORT_TEXT: [Answer, "Mytext", None],
            Question.RADIO: [Answer, "Yes", "Yes, No, Maybe"],
            Question.SELECT: [Answer, "No", "Yes, No, Maybe"],
            #  Question.SELECT_IMAGE: [AnswerSelectImage, "TODO" ,None],
            Question.SELECT_MULTIPLE: [Answer, "Yes",
                                       "Yes, No, Maybe"],
            Question.INTEGER: [Answer, 42, None],
        }
        for i, qtype in enumerate(self.data):
            answer_class = self.data[qtype][0]
            answer_body = self.data[qtype][1]
            answer_choices = self.data[qtype][2]
            question = Question.objects.create(
                text="Q? {}".format(qtype), choices=answer_choices,
                order=i + 1, required=True, survey=self.survey,
                type=qtype,
            )
            self.questions.append(question)
            answer = answer_class(
                response=self.response, question=question, body=answer_body
            )
            self.answers.append(answer)
