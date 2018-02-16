# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from datetime import datetime
import logging
import os
import time

from django.conf import settings
from future import standard_library

from survey.exporter.survey2x import Survey2X
from survey.tests.management.test_management import TestManagement


standard_library.install_aliases()

LOGGER = logging.getLogger(__name__)


class TestSurvey2X(TestManagement):

    def setUp(self):
        TestManagement.setUp(self)
        self.s2x = Survey2X(self.survey)

    def test_survey_2_x(self):
        self.assertRaises(NotImplementedError, self.s2x.survey_to_x)

    def test_need_update(self):
        class Survey2Survey(Survey2X):
            def survey_to_x(self):
                file_ = open(self.file_name(), "w")
                file_.write(".")
                file_.close()

        s2xi = Survey2Survey(self.survey)
        expected = os.path.join(settings.ROOT, "survey",
                                "test-management-survey.survey")
        self.assertEqual(s2xi.file_name(), expected)

        # survey output file shouldn't exist but responses are
        # already created
        responses = s2xi.survey.responses.all()
        LOGGER.debug("Number of responses: %s", len(responses))
        lad = s2xi.survey.latest_answer_date()
        LOGGER.debug("latest_answer_date before file creation: %s", lad)
        self.assertTrue(s2xi.need_update())
        time.sleep(1)

        # write dummy survey file
        s2xi.survey_to_x()
        mtime = os.path.getmtime(expected)
        fctime = datetime.fromtimestamp(mtime)
        fcztime = fctime.replace(tzinfo=lad.tzinfo)
        LOGGER.debug("mtime: %s", fcztime)

        # no responses saved Survey2X created need_update and
        # should return False
        lad = s2xi.survey.latest_answer_date()
        LOGGER.debug("latest_answer_date after file creation: %s", lad)
        self.assertFalse(s2xi.need_update())

        # save response
        self.response.save()

        # now need_update should return True
        lad = s2xi.survey.latest_answer_date()
        LOGGER.debug("latest_answer_date after save(): %s", lad)
        self.assertTrue(s2xi.need_update())

        # remove survey file
        if os.path.exists(expected):
            os.remove(expected)
        else:
            LOGGER.error("Error removing '%s'", expected)
