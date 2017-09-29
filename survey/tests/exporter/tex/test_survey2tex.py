# -*- coding: utf-8 -*-


from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os

from future import standard_library

from survey.exporter.tex.configuration import Configuration
from survey.exporter.tex.survey2tex import Survey2Tex
from survey.models import Survey
from survey.tests.management.test_management import TestManagement

standard_library.install_aliases()


class TestSurvey2Tex(TestManagement):

    def setUp(self):
        TestManagement.setUp(self)
        self.create_big_ranking_survey()
        conf = Configuration(os.path.join(self.conf_dir, "test_conf.yaml"))
        self.generic = Survey2Tex(self.survey, conf)
        self.test_survey = Survey.objects.get(name="Test survëy")
        self.specific = Survey2Tex(self.test_survey, conf)

    def test_get_survey_as_tex(self):
        """ The content of the tex is correct. """
        generic = self.generic.survey_to_x()
        should_contain = [
            "documentclass[11pt]{article}", "title{My title}",
            "Test management footer.", "Aèbc?", "Bècd?", "Cède?",
            ""
        ]
        for text in should_contain:
            self.assertIn(text, generic)
        specific = self.specific.survey_to_x()
        should_contain = [
            "documentclass[11pt]{report}", "title{My title}",
            "This is the footer.", "{Lorem ipsum dolor sit amët",
            "adipiscing}  elit.'", "with 'K.' standing for 'Yës'",
            "'Nah' standing for 'No' or 'Whatever'"
        ]
        for text in should_contain:
            self.assertIn(text, specific)
