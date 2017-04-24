# -*- coding: utf-8 -*-

import logging
import os

from django.conf import settings

from survey.models.answer import get_real_type_answer
from survey.models.survey import Survey

LOGGER = logging.getLogger(__name__)


class Survey2CSV(object):

    @staticmethod
    def file_name(survey):
        return os.path.join(settings.CSV_DIR, u"{}.csv".format(survey.name))

    @staticmethod
    def line_list_to_string(line):
        """ Write a line in the CSV """
        new_line = u""
        for i, cell in enumerate(line):
            cell = u" ".join(cell.split())
            try:
                cell = unicode(cell)
            except UnicodeDecodeError:
                cell = unicode(cell.decode("utf8"))
            new_line += cell.replace(u",", u";")
            if i != len(line) - 1:
                new_line += u","
        return new_line

    @staticmethod
    def get_user_line(question_order, response):
        """ Creating a line for a user """
        not_an_answer = u"NAA"
        logging.debug(u"\tTreating answer from {}".format(response.user))
        user_answers = {}
        user_answers[u"user"] = unicode(response.user)
        # user_answers[u"entity"] = response.user.entity
        for answer_base in response.answers.all():
            answer = get_real_type_answer(answer_base)
            cell = not_an_answer
            # remove double space, tab, \n...
            answer_body = " ".join(unicode(answer.body).split())
            if "[" in answer_body:
                # Its a select multiple ( [u"Yes", u"Maybe"] )
                answers = eval(answer_body)
                cell = u""
                for i, ans in enumerate(answers):
                    if i < len(answers) - 1:
                        # Separate by a pipe if its not the last
                        cell += ans + u" | "
                    else:
                        cell += ans
            else:
                cell = answer_body
            logging.debug(u"\t\t{} : {}".format(answer.question.pk, cell))
            user_answers[answer.question.pk] = cell
        user_line = []
        for key_ in question_order:
            try:
                user_line.append(user_answers[key_])
            except KeyError:
                user_line.append(not_an_answer)
        return user_line

    @staticmethod
    def get_header_and_order(survey):
        """ Creating header """
        header = [u"user"]  # , u"entity"]
        question_order = [u"user"]  # , u"entity" ]
        for question in survey.questions():
            header.append(unicode(question.text))
            question_order.append(question.pk)
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
