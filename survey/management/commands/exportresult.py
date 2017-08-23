# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import logging

from django.core.management.base import BaseCommand
from future import standard_library

from survey.management.exporter.csv import Survey2Csv
from survey.management.exporter.tex.configuration import Configuration
from survey.management.exporter.tex.survey2tex import Survey2Tex
from survey.models import Survey

standard_library.install_aliases()

LOGGER = logging.getLogger()


class Command(BaseCommand):

    """
        See the "help" var.
    """

    requires_system_checks = False

    help = u"""This command permit to export all survey in the database as csv
               and tex."""

    def add_arguments(self, parser):
        parser.add_argument('configuration_file', nargs='+', type=str,
                            help='Path to the tex configuration file.')
        parser.add_argument(
            '--force', "-f", action="store_true",
            help='Force the generation, even if the file already exists.'
        )
        parser.add_argument(
            '--csv', action="store_true",
            help='Force the generation, even if the file already exists.'
        )
        parser.add_argument(
            '--tex', action="store_true",
            help='Force the generation, even if the file already exists.'
        )

    def handle(self, *args, **options):
        configuration = Configuration(options["configuration_file"][0])
        if not options["csv"] and not options["tex"]:
            exit("Nothing to do : add option --tex, --csv, or both.")
        for survey in Survey.objects.all():
            LOGGER.info("Generating results for '%s'", survey)
            exporters = []
            if options["csv"]:
                exporters.append(Survey2Csv(survey))
            if options["tex"]:
                exporters.append(Survey2Tex(survey, configuration))
            for exporter in exporters:
                if options["force"] or exporter.need_update():
                    exporter.generate_file()
                else:
                    LOGGER.info("\t- %s's %s were already generated.", survey,
                                exporter._get_X())
