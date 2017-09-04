# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import logging

from future import standard_library

from survey.exporter.csv import Survey2Csv
from survey.exporter.tex.configuration import Configuration
from survey.exporter.tex.survey2tex import Survey2Tex
from survey.management.survey_command import SurveyCommand
from survey.models import Survey

standard_library.install_aliases()

LOGGER = logging.getLogger()


class Command(SurveyCommand):

    """
        See the "help" var.
    """

    help = u"""This command permit to export all survey in the database as csv
               and tex."""

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
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
        super(Command, self).handle(*args, **options)
        configuration = Configuration(options["configuration_file"][0])
        if not options["csv"] and not options["tex"]:
            exit("Nothing to do : add option --tex, --csv, or both.")
        if self.survey is None:
            surveys = Survey.objects.all()
        else:
            surveys = [self.survey]
        for survey in surveys:
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
                    LOGGER.info("\t- %s's %s were already generated use the\
 --force (-f) option to generate anyway.", survey, exporter._get_X())
