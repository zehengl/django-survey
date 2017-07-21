# -*- coding: utf-8 -*-


from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os

from django.conf import settings
from future import standard_library

from survey.management.exporter.tex.survey2tex import Survey2Tex
from survey.models import Survey
from survey.tests.management.test_management import TestManagement

standard_library.install_aliases()


class TestSurvey2Tex(TestManagement):

    def setUp(self):
        TestManagement.setUp(self)
        conf = os.path.join(settings.ROOT, "survey", "tests", "management",
                            "latex_conf.yaml")
        self.generic = Survey2Tex(self.survey, conf)
        self.specific = Survey2Tex(Survey.objects.get(name="Test survëy"),
                                   conf)

    def test_get_survey_as_tex(self):
        """ The content of the tex is correct. """
        generic = self.generic.survey_to_x()
        should_contain = [
            "documentclass[11pt]{article}", "title{My title}",
            "Test management survey footer.", "Aèbc?", "Bècd?", "Cède?",
        ]
        for text in should_contain:
            self.assertIn(text, generic)
        specific = self.specific.survey_to_x()
        should_contain = [
            "documentclass[11pt]{report}", "title{My title}",
            "This is the footer.", "{Lorem ipsum dolor sit amët",
        ]
        for text in should_contain:
            self.assertIn(text, specific)
