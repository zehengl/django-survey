# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.core.management import call_command
from django.utils.text import slugify

from survey.tests.management.test_management import TestManagement


class TestExportresult(TestManagement):

    """ Permit to check if export result is working as intended. """

    def get_csv_path(self, survey_name):
        csv_name = u'{}.csv'.format(slugify(survey_name))
        return os.path.join(settings.CSV_DIR, csv_name)

    def get_file_content(self, path):
        file_ = open(path)
        content = file_.read()
        file_.close()
        return content

    def test_handle(self):
        """ The custom command export result create the right csv file. """
        self.maxDiff = None
        first_csv = self.get_csv_path(self.test_managament_survey_name)
        second_csv = self.get_csv_path('Test survëy')
        # Force to regenerate the csv, we want to test something not optimize
        # computing time.
        os.remove(first_csv)
        os.remove(second_csv)
        call_command("exportresult")
        self.assertMultiLineEqual(self.expected_content.encode("utf8"),
                                  self.get_file_content(first_csv))
        expected = u"""\
user,Lorem ipsum dolor sit amët; <strong> consectetur </strong> adipiscing \
elit.,Ipsum dolor sit amët; <strong> consectetur </strong> adipiscing elit.,\
Dolor sit amët; <strong> consectetur</strong> adipiscing elit.,Lorem ipsum\
 dolor sit amët; consectetur<strong> adipiscing </strong> elit.,Ipsum dolor \
sit amët; consectetur <strong> adipiscing </strong> elit.,Dolor sit amët; \
consectetur<strong> adipiscing</strong> elit.
pierre,Yës|Maybe,,Text for a response,,1,No|Whatever
ps250112,Yës,,,,1,Yës"""
        self.assertMultiLineEqual(expected.encode("utf8"),
                                  self.get_file_content(second_csv))
