# -*- coding: utf-8 -*-

import logging

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
            Survey2CSV.generate_file(survey)
