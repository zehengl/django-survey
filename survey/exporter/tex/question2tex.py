# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import logging
from builtins import object

from django.utils.translation import ugettext_lazy as _
from future import standard_library

standard_library.install_aliases()


LOGGER = logging.getLogger(__name__)


class Question2Tex(object):

    """
        This class permit to generate latex code directly from the Question
        object after overriding the tex() function.
    """

    TEX_SKELETON = ""

    def __init__(self, question, **options):
        self.question = question
        self.min_cardinality = options.get("min_cardinality", 0)
        self.group_by_letter_case = options.get("group_by_letter_case")
        self.group_by_slugify = options.get("group_by_slugify")
        self.group_together = options.get("group_together")
        self.sort_answer = options.get("sort_answer")
        self.filter = options.get("filter")
        self.cardinality = self.question.sorted_answers_cardinality(
            self.min_cardinality, self.group_together,
            self.group_by_letter_case, self.group_by_slugify, self.filter,
            self.sort_answer
        )

    @staticmethod
    def html2latex(html_text):
        """ Convert some html text to something latex can compile.

        About the implementation : I added only what I used in my own questions
        here, because html2latex (https://pypi.python.org/pypi/html2latex/) is
        adding more than 12 Mo to the virtualenv size and 8 dependencies !
            (Jinja (378kB), Pillow (7.5MB), lxml (3.5MB), pyenchant (60kB),
             redis (62kB), selenium (2.6MB), ipython (2.8MB) nose (154kB)

        :param String html_text: Some html text. """
        html_text = html_text.replace("<strong>", "\\textbf{")
        html_text = html_text.replace("</strong>", "}")
        html_text = html_text.replace("<code>", "$")
        html_text = html_text.replace("</code>", "$")
        html_text = html_text.replace("&lt;", "<")
        html_text = html_text.replace("&gt;", ">")
        return html_text

    @staticmethod
    def get_clean_answer(answer):
        if not answer or answer == "[]":
            answer = _("Left blank")
        else:
            replace_list = [",", "\n", "\r", "/", " "]
            for char in replace_list:
                answer = answer.replace(char, " ")
        return answer

    def tex(self):
        raise NotImplementedError("Question2Tex.tex() is abstract.")
