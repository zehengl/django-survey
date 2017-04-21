# -*- coding: utf-8 -*-


from survey.management.survey2csv import Survey2CSV
from survey.tests.management.test_management import TestManagement


class TestSurvey2CSV(TestManagement):

    """ Permit to check if export result is working as intended. """

    def test_get_header_and_order(self):
        """ The header and order of the question is correct. """
        header, order = Survey2CSV.get_header_and_order(self.survey)
        self.assertEqual(header, self.expected_header)
        self.assertEqual(len(order), 4)

    def test_get_survey_as_csv(self):
        """ The content of the CSV is correct. """
        self.assertEqual(Survey2CSV.survey_to_csv(self.survey),
                         self.expected_content)
