# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from builtins import str

from django.core.management.base import BaseCommand
from future import standard_library

from survey.management.exporter.tex import ConfigurationBuilder
from survey.models import Survey

standard_library.install_aliases()


class Command(BaseCommand):

    """
        See the "help" var.
    """

    requires_system_checks = False

    help = u"""This command permit to generate the latex configuration in order
    to manage the survey report generation. """

    def add_arguments(self, parser):
        parser.add_argument('output', nargs='+', type=str, help='Output file.')
        parser.add_argument(
            "--survey-name", nargs='+', type=str,
            help='The name of the survey we want to generate.'
        )
        parser.add_argument(
            "--survey-id", nargs='+', type=int,
            help='The primary key of the survey we want to generate.'
        )

    def clean_error_message(self, value):
        """ Return a clean error message

        :param string value: the attempted value. """
        valids = [(survey.pk, survey.name) for survey in Survey.objects.all()]
        msg = "You tried to get '{}' but is does not exists.\n".format(value)
        msg += "Possibles values :\n"
        for pk, name in valids:
            msg += "--survey-id {} / --survey-name '{}'\n".format(pk, name)
        return msg

    def handle(self, *args, **options):
        output = options["output"][0]
        if options['survey_name']:
            survey_name = options['survey_name'][0]
            try:
                survey = Survey.objects.get(name=survey_name)
            except Survey.DoesNotExist:
                raise ValueError(self.clean_error_message(survey_name))
            conf = ConfigurationBuilder(survey)
        elif options['survey_id']:
            survey_id = options['survey_id'][0]
            try:
                survey = Survey.objects.get(pk=survey_id)
            except Survey.DoesNotExist:
                raise ValueError(self.clean_error_message(survey_id))
            conf = ConfigurationBuilder(survey)
        else:
            conf = ConfigurationBuilder()
        file_ = open(output, "w")
        file_.write(str(conf))
        file_.close()
