# -*- coding: utf-8 -*-

"""
    Permit to import everything from survey.models without knowing the details.
"""

import sys

from .answer import (AnswerBase, AnswerInteger, AnswerRadio,
    AnswerSelect, AnswerSelectMultiple, AnswerText, get_real_type_answer)
from .category import Category
from .question import Question
from .response import Response
from .survey import Survey


__all__ = ["Category", "AnswerBase", "AnswerInteger", "AnswerRadio",
           "AnswerSelect", "AnswerSelectMultiple", "AnswerText", "Category",
           "Response", "Survey", "Question", "get_real_type_answer"]
