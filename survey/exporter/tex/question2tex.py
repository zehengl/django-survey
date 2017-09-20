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
    def _sorted_cardinality(cardinality, sort_answer=None):
        """ Mostly to have reliable tests, but marginally nicer too...

        The ordering is reversed for same cardinality value so we have aa
        before zz. """
        if sort_answer is None or sort_answer == "alphanumeric":
            return sorted(cardinality.items())
        if type(sort_answer) is dict:
            # User defined dict
            return sorted(cardinality.items(),
                          key=lambda x: sort_answer.get(x[0]))
        if sort_answer == "cardinal":
            return sorted(cardinality.items(), key=lambda x: (-x[1], x[0]))
        LOGGER.warning(
            "Unrecognized option '%s' for 'sort_answer': %s", sort_answer,
            "use nothing, a dict (answer: rank), 'alphanumeric' or 'cardinal'."
            " We used the default alphanumeric sorting."
        )
        return sorted(cardinality.items())

    @staticmethod
    def get_colors(cardinality, colors_dict, sort_answer=None):
        """ Return a formated string for a tikz pgf-pie chart.

        TODO : Right now color are all or nothing, so you can't set up just
        one color in the generic configuration (for example white for empty
        answer and undefined for everything else).

        :param Question question: The question..
        :param Dict colors_dict: Color to use (String answer: String color)
        """
        colors = []
        for answer in Question2Tex._sorted_cardinality(cardinality, sort_answer):
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
    def get_results(cardinality, sort_answer=None):
        """ Return a formated string for a tikz pgf-pie chart.

        :param Question question: The question..
        :param Dict colors_dict: Color to use (String answer: String color)
        """
        pie = u""
        for answer in Question2Tex._sorted_cardinality(cardinality, sort_answer):
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
    def get_caption(question, min_cardinality, filter, group_together):
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
            for excluded in filter:
                caption += "'{}', ".format(excluded)
            caption = "{} ".format(caption[:-2])
        caption += "%s '%s' " % (
            _("for the question"), Question2Tex.html2latex(question.text)
        )
        if group_together:
            for key, values in group_together.items():
                # We duplicate the translations so makemessage find it
                caption += "with '{}' standing for ".format(key)
                for value in values:
                    caption += "'{}' {} ".format(value, _("or"))
                caption = caption[:-len("{} ".format(_("or")))]
                caption += "{} ".format(_("and"))
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
        cardinality = question.answers_cardinality(
            min_cardinality=min_cardinality, group_together=group_together,
            group_by_letter_case=group_by_letter_case,
            group_by_slugify=group_by_slugify, filter=filter
        )
        if type == "raw":
            return Question2Tex.raw(cardinality.keys())
        if color:
            # We must remove color that are not used in the chart.
            color = Question2Tex.get_colors(cardinality, color, sort_answer)
        options = Question2Tex.get_pie_options(
            pos, rotate, radius, color, explode, sum, after_number,
            before_number, scale_font, text, style, type
        )
        results = Question2Tex.get_results(cardinality, sort_answer)
        if not results:
            return str(_("No answers for this question."))
        caption = Question2Tex.get_caption(question, min_cardinality, filter,
                                           group_together)
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
