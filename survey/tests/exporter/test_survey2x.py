# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from future import standard_library

from survey.exporter.survey2x import Survey2X
from survey.tests.management.test_management import TestManagement


standard_library.install_aliases()


class TestSurvey2X(TestManagement):

    def setUp(self):
        TestManagement.setUp(self)
        self.s2x = Survey2X(self.survey)

    def test_survey_2_x(self):
        self.assertRaises(NotImplementedError, self.s2x.survey_to_x)
