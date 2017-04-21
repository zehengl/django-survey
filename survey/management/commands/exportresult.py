# -*- coding: utf-8 -*-

import logging
import os

from django.core.management.base import BaseCommand

from survey.management.survey2csv import Survey2CSV
from survey.models import Survey

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):

    """
        See the "help" var.
    """

    requires_system_checks = False

    help = u"This command permit to export all survey in the database as csv."

    def handle(self, *args, **options):
        dir_ = "csv"
        if not os.path.exists(dir_):
            os.mkdir(dir_)
        for survey in Survey.objects.all():
            logging.debug(u"Treating survey '{}'".format(survey))
            file_ = open(os.path.join(dir_, u"{}.csv".format(survey.name)), "w")
            csv = Survey2CSV.survey_to_csv(survey)
            for line in csv:
                file_.write(line.encode('utf-8'))
                file_.write(u"\n")
            file_.close()
