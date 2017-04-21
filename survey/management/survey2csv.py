# -*- coding: utf-8 -*-

import logging

from survey.models.answer import get_real_type_answer
from survey.models.survey import Survey

LOGGER = logging.getLogger(__name__)


class Survey2CSV(object):

    @staticmethod
    def line_list_to_string(line):
        """ Write a line in the CSV """
        new_line = u""
        for i, cell in enumerate(line):
            cell = " ".join(cell.split())
            cell = cell.encode("utf8").replace(",", ";")
            new_line += cell
            if i != len(line) - 1:
                new_line += ","
        return new_line

    @staticmethod
    def get_user_line(question_order, response):
        """ Creating a line for a user """
        not_an_answer = "NAA"
        logging.debug(u"\tTreating answer from {}".format(response.user))
        user_answers = {}
        user_answers[-2] = str(response.user)
        # user_answers[-1] = response.user.entity
        for answer_base in response.answers.all():
            answer = get_real_type_answer(answer_base)
            cell = not_an_answer
            answer_body = " ".join(str(answer.body).split())
            if "[" in answer_body:
                # Its a select multiple ( [u"Yes", u"Maybe"] )
                answers = eval(answer_body)
                cell = u""
                for i, ans in enumerate(answers):
                    if i < len(answers) - 1:
                        # Separate by a space if its not the last
                        cell += ans + u" | "
                    else:
                        cell += ans
            else:
                cell = answer_body
            logging.debug(u"\t\t{} : {}".format(answer.question.pk, cell))
            user_answers[answer.question.pk] = cell
        user_line = []
        question_keys = question_order.keys()
        question_keys.sort()
        for i in question_keys:
            try:
                user_line.append(user_answers[i])
            except KeyError:
                user_line.append(not_an_answer)
        return user_line

    @staticmethod
    def get_header_and_order(survey):
        """ Creating header """
        header = []
        question_order = {}
        header.append(u"user")
        question_order[-2] = 0
        # header.append(u"entity")
        # question_order[-1] = "entity"
        other_field = len(question_order)
        for i, question in enumerate(survey.questions()):
            header.append(question.text)
            question_order[question.pk] = i + other_field
        return header, question_order

    @staticmethod
    def survey_to_csv(survey):
        """ Export a csv for a survey. """
        if not isinstance(survey, Survey):
            msg = "Expected 'Survey' not '{}'".format(survey.__class__.__name__)
            raise TypeError(msg)
        csv = []
        header, question_order = Survey2CSV.get_header_and_order(survey)
        csv.append(Survey2CSV.line_list_to_string(header))
        for response in survey.responses.all():
            line = Survey2CSV.get_user_line(question_order, response)
            csv.append(Survey2CSV.line_list_to_string(line))
        return csv
