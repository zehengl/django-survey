# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import logging
from builtins import object

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from future import standard_library

from survey.models.question import Question

standard_library.install_aliases()


LOGGER = logging.getLogger(__name__)


class Question2Tex(object):

    """
        This class permit to generate latex code directly from the Question
        object.
    """

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
    def get_colors(cardinality, colors_dict):
        """ Return a formated string for a tikz pgf-pie chart.

        :param Question question: The question..
        :param Dict colors_dict: Color to use (String answer: String color)
        """
        colors = []
        for answer in cardinality:
            answer = Question2Tex.get_clean_answer(answer[0])
            try:
                colors.append(colors_dict[answer])
            except (KeyError, ValueError):
                msg = u"Color for '%s' not provided. You could " % answer
                msg += "add '%s: \"red!50\"', in your color config." % answer
                LOGGER.warning(msg)
                colors.append(settings.SURVEY_DEFAULT_PIE_COLOR)
        return "{%s}" % ", ".join(colors)

    @staticmethod
    def get_clean_answer(answer):
        if not answer or answer == "[]":
            answer = _("Left blank")
        else:
            replace_list = [",", "\n", "\r", "/", " "]
            for char in replace_list:
                answer = answer.replace(char, " ")
        return answer

    @staticmethod
    def get_results(cardinality):
        """ Return a formated string for a tikz pgf-pie chart. """
        pie = u""
        for answer in cardinality:
            if not answer[0]:
                ans = _("Left blank")
            ans = Question2Tex.get_clean_answer(answer[0])
            pie += "{}/{},".format(answer[1], ans)
        if not pie:
            return u""
        final_answers = []
        for answer in pie.split(","):
            if answer:
                final_answers.append(answer)
        return u"            {}".format(u",\n            ".join(final_answers))

    @staticmethod
    def get_pie_options(pos=None, rotate=None, radius=None, color=None,
                        explode=None, sum=None, after_number=None,
                        before_number=None, scale_font=None, text=None,
                        style=None, type=None):
        """ Return the options of the pie for this: \pie[options]{data}"""
        options = ""
        if pos:
            value = "{%s}" % pos
            options += "pos={},".format(value)
        if rotate:
            options += "rotate={},".format(rotate)
        if radius:
            options += "radius={},".format(radius)
        if color:
            options += "color={},".format(color)
        if explode:
            options += "explode={%s}," % explode
        if sum:
            options += "sum={},".format(sum)
        if after_number:
            options += "after number={},".format(after_number)
        if before_number:
            options += "before number={},".format(before_number)
        if scale_font:
            options += "scale font, "
        if text:
            options += "text={},".format(text)
        if style:
            options += "style={},".format(style)
        if type and type != "pie":
            options += "{},".format(type)
        # Removing last ','
        options = options[:-1]
        if options:
            return "[{}]".format(options)
        else:
            return ""

    @staticmethod
    def raw(answers):
        """ Return all the answer as quote in latex. """
        raw_answers = ""
        for i, answer in enumerate(answers):
            if answer:
                raw_answers += """
\\begin{quote}
%s
\\end{quote} \hfill (%s n\\textsuperscript{o}%s)
            """ % (answer, _("Participant"), i)
        return raw_answers

    @staticmethod
    def get_caption(question, min_cardinality, filter, group_together,
                    cardinality=None, group_by_letter_case=None,
                    group_by_slugify=None,):
        """ Return a caption with an appropriate description of the chart. """
        caption = "{} ".format(_("Repartition of answers"))
        if min_cardinality > 0:
            caption += "{} {} ".format(_("with"), ungettext(
                "%(min_cardinality)d respondants or more",
                "%(min_cardinality)d respondant or more",
                min_cardinality) % {'min_cardinality': min_cardinality, }
            )
        if filter:
            caption += "{} ".format(_("excluding"))
            for i, excluded in enumerate(filter):
                excluded = Question2Tex.get_clean_answer(excluded)
                caption += "'{}', ".format(excluded)
                if len(filter) >= 2 and i == len(filter) - 2:
                    caption += "{} ".format(_("and"))
            caption = "{} ".format(caption[:-2])
        caption += "%s '%s' " % (
            _("for the question"), Question2Tex.html2latex(question.text)
        )
        if group_together:
            if cardinality is None:
                loop_dict = group_together
            else:
                # Looping only on the value really used in the answers
                loop_dict = cardinality
            has_and = False
            for key in loop_dict:
                values = group_together.get(key)
                if values is None:
                    # group_together does not contain every answers
                    continue
                standardized_values = Question.standardize_list(
                    values, group_by_letter_case, group_by_slugify
                )
                standardized_key = Question.standardize(
                    key, group_by_letter_case, group_by_slugify
                )
                relevant_values = [v for v in standardized_values
                                   if v != standardized_key]
                if not relevant_values:
                    # If there is no relevant value the group_together was just
                    # a placeholder ex Yes for [yes Yës yEs]
                    continue
                # We duplicate the translations so makemessage find it
                caption += "with '{}' standing for ".format(key)
                for value in values:
                    caption += "'{}' {} ".format(value, _("or"))
                caption = caption[:-len("{} ".format(_("or")))]
                has_and = True
                caption += "{} ".format(_("and"))
            if has_and:
                # We remove the final "and " if there is one
                caption = caption[:-len("{} ".format(_("and")))]
        return "{}.".format(caption[:-1])

    @staticmethod
    def chart(question, min_cardinality=0, group_by_letter_case=None,
              group_by_slugify=None, group_together=None, sort_answer=None,
              pos=None, rotate=None, radius=None, color=None,
              explode=None, sum=None, after_number=None,
              before_number=None, scale_font=None, text=None, style=None,
              type=None, filter=None, latex_label=1):
        """ Return a pfg-pie pie chart of a question.

        You must use pgf-pie in your latex file for this to works ::

            \\usepackage{pgf-pie}

        See http://pgf-pie.googlecode.com/ for detail and arguments doc.

        :param Question question: The question we want to plot """
        cardinality = question.sorted_answers_cardinality(
            min_cardinality=min_cardinality, group_together=group_together,
            group_by_letter_case=group_by_letter_case, sort_answer=sort_answer,
            group_by_slugify=group_by_slugify, filter=filter
        )
        if type == "raw":
            answers = [c[0] for c in cardinality]
            return Question2Tex.raw(answers)
        if color:
            # We must remove color that are not used in the chart.
            color = Question2Tex.get_colors(cardinality, color)
        options = Question2Tex.get_pie_options(
            pos, rotate, radius, color, explode, sum, after_number,
            before_number, scale_font, text, style, type
        )
        results = Question2Tex.get_results(cardinality)
        if not results:
            return str(_("No answers for this question."))
        caption = Question2Tex.get_caption(
            question, min_cardinality, filter, group_together, cardinality,
            group_by_letter_case, group_by_slugify
        )
        return """
\\begin{figure}[h!]
    \\begin{tikzpicture}
        \\pie%s{
%s
        }
    \\end{tikzpicture}
    \\caption{\label{figure:q%d-%d}%s}
\\end{figure}
""" % (options, results, question.pk, latex_label, caption)
