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
    def _sorted_cardinality(cardinality):
        """ Mostly to have reliable tests, but marginally nicer too...

        The ordering is reversed for same cardinality value so we have aa
        before zz. """
        return sorted(cardinality.items(), key=lambda x: (-x[1], x[0]))

    @staticmethod
    def get_colors(cardinality, colors_dict):
        """ Return a formated string for a tikz pgf-pie chart.

        TODO : Right now color are all or nothing, so you can't set up just
        one color in the generic configuration (for example white for empty
        answer and undefined for everything else).

        :param Question question: The question..
        :param Dict colors_dict: Color to use (String answer: String color)
        """
        colors = u""
        for answer in Question2Tex._sorted_cardinality(cardinality):
            try:
                colors += u"{},".format(colors_dict[answer[0]])
            except (KeyError, ValueError):
                msg = u"Color for '%s' not provided. You could " % answer[0]
                msg += "add '%s: \"red!50\"', in your dictionary." % answer[0]
                raise ValueError(msg)
        final_colors = []
        for color in colors.split(","):
            if color:
                final_colors.append(color)
        return u", ".join(final_colors)

    @staticmethod
    def get_results(cardinality):
        """ Return a formated string for a tikz pgf-pie chart.

        :param Question question: The question..
        :param Dict colors_dict: Color to use (String answer: String color)
        """
        pie = u""
        for ans, c in Question2Tex._sorted_cardinality(cardinality):
            if not ans:
                ans = _("Left blank")
            pie += "{}/{},".format(c, ans)
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
    def chart(question, min_cardinality=0, group_by_letter_case=None,
              group_by_slugify=None, group_together=None,
              pos=None, rotate=None, radius=None, color=None,
              explode=None, sum=None, after_number=None,
              before_number=None, scale_font=None, text=None, style=None,
              type=None):
        """ Return a pfg-pie pie chart of a question.

        You must use pgf-pie in your latex file for this to works ::

            \\usepackage{pgf-pie}

        See http://pgf-pie.googlecode.com/ for detail and arguments doc.

        :param Question question: The question we want to plot """
        cardinality = question.answers_cardinality(
            min_cardinality=min_cardinality, group_together=group_together,
            group_by_letter_case=group_by_letter_case,
            group_by_slugify=group_by_slugify,
        )
        if color:
            # We must remove color that are not used in the chart.
            color = "{%s}" % Question2Tex.get_colors(cardinality, color)
        options = Question2Tex.get_pie_options(
            pos, rotate, radius, color, explode, sum, after_number,
            before_number, scale_font, text, style, type
        )
        results = Question2Tex.get_results(cardinality)
        if not results:
            return _("No answers for this question.")
        chart = """\\pie%s{
%s
        }
""" % (options, results)
        caption = "\label{figure:q%d} %s '%s'" % (
            question.pk, _("Answers to the question"),
            Question2Tex.html2latex(question.text)
        )
        return """
\\begin{figure}[h!]
    \\begin{tikzpicture}
        %s
    \\end{tikzpicture}
    \\caption{%s}
\\end{figure}
""" % (chart, caption)
