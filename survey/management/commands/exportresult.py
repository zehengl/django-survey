# -*- coding: utf-8 -*-

import logging

from django.conf import settings
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
        for survey in Survey.objects.all():
            logging.debug(u"Treating survey '{}'".format(survey))
            try:
                with open(Survey2CSV.file_name(survey), "w") as f:
                    csv = Survey2CSV.survey_to_csv(survey)
                    for line in csv:
                        f.write(line.encode('utf-8'))
                        f.write(u"\n")
            except IOError as exc:
                raise IOError("Must create {}".format(settings.CSV_DIR), exc)
