# -*- coding: utf-8 -*-

import logging
import os

from django.core.management.base import BaseCommand

from survey.models import Survey
from survey.models.answer import get_real_type_answer

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):

    """
        See the "help" var.
    """

    requires_system_checks = False

    help = u"This command permit to load the test database"

    def handle(self, *args, **options):
        dir_ = "csv"
        if not os.path.exists(dir_):
            os.mkdir(dir_)
        for survey in Survey.objects.all():
            logging.debug("Treating answer to {}".format(survey))
            file_ = open(os.path.join(dir_, "{}.csv".format(survey.name)), "w")
            fw = file_.write
            fw(u"user,")
            # fw("entity")
            for question in survey.questions():
                fw(u"{},".format(question.text))
            fw(u"\n")
            for response in survey.responses.all():
                logging.debug("\tTreating answer from {}".format(response.user))
                fw(u"{},".format(response.user))
                # response.user.entity
                for answer_base in response.answers.all():
                    answer = get_real_type_answer(answer_base)
                    logging.debug("\t\t{} : {}".format(answer.pk, answer.body))
                    if answer.body:
                        if "[" in unicode(answer.body):
                            # Its a select multiple ( [u"Yes", u"Maybe"] )
                            answers = eval(answer.body)
                            for i, ans in enumerate(answers):
                                if i < len(answers) - 1:
                                    # Separate by a space if its not the last
                                    fw(u"{} ".format(ans))
                                else:
                                    fw(u"{}".format(ans))
                        else:
                            fw(u"{}".format(answer.body))
                    else:
                        fw(u"NAA")
                    fw(u",")
                fw(u"\n")
            file_.close()
