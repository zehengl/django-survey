# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from survey.views.confirm_view import ConfirmView
from survey.views.index_view import IndexView
from survey.views.survey_completed import SurveyCompleted
from survey.views.survey_detail import SurveyDetail


__all__ = ["SurveyCompleted", "IndexView", "ConfirmView", "SurveyResult",
           "SurveyDetail"]
