# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from django.core.management.base import BaseCommand
from future import standard_library

from survey.management.exporter.csv import Survey2Csv
from survey.management.exporter.tex.survey2tex import Survey2Tex
from survey.models import Survey

standard_library.install_aliases()


class Command(BaseCommand):

    """
        See the "help" var.
    """

    requires_system_checks = False

    help = u"""This command permit to export all survey in the database as csv
               and tex."""

    def handle(self, *args, **options):
        for survey in Survey.objects.all():
            exporters = [Survey2Csv(survey), Survey2Tex(survey)]
            for exporter in exporters:
                if exporter.need_update():
                    exporter.generate_file()
