# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from builtins import str
from sys import version_info

from django.core.management.base import BaseCommand
from future import standard_library
from survey.models import Survey

standard_library.install_aliases()


class SurveyCommand(BaseCommand):

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument(
            "--survey-name", nargs='+', type=str,
            help='The name of the survey we want to generate.'
        )
        parser.add_argument(
            "--survey-id", nargs='+', type=int,
            help='The primary key of the survey we want to generate.'
        )

    def raise_value_error(self, value):
        msg = self.clean_error_message_survey(value)
        # Compatibility for python 2/3
        # See: https://stackoverflow.com/questions/46076279/
        if version_info.major == 2:
            raise ValueError(msg.encode('utf-8'))
        else:
            raise ValueError(msg)

    def clean_error_message_survey(self, value):
        """ Return a clean error message if an argument is wrong.

        :param string value: the attempted value. """
        valids = [(survey.pk, survey.name) for survey in Survey.objects.all()]
        msg = "You tried to get '{}' but is does not exists.\n".format(value)
        msg += "Possibles values :\n"
        for pk, name in valids:
            msg += "--survey-id {} / --survey-name '{}'\n".format(pk, name)
        return msg

    def handle(self, *args, **options):
        self.survey = None
        if options['survey_name']:
            survey_name = options['survey_name'][0]
            try:
                self.survey = Survey.objects.get(name=survey_name)
            except Survey.DoesNotExist:
                self.raise_value_error(survey_name)
        elif options['survey_id']:
            survey_id = options['survey_id'][0]
            try:
                self.survey = Survey.objects.get(pk=survey_id)
            except Survey.DoesNotExist:
                self.raise_value_error(survey_id)
