# -*- coding: utf-8 -*-

from survey_test.tests.models.base_model_test import BaseModelTest


class TestResponse(BaseModelTest):

    def test_unicode(self):
        """ Unicode generation. """
        self.assertIsNotNone(str(self.response))
