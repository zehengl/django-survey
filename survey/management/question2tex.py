# -*- coding: utf-8 -*-

import logging

from django.utils.translation import ugettext_lazy as _

LOGGER = logging.getLogger(__name__)


class Question2Tex(object):

    """
        This class permit to generate latex code directly from the Question
        object.
    """

    @staticmethod
    def get_colors(question, min_cardinality, colors_dict):
        """ Return a formated string for a tikz pgf-pie chart.

        :param Question question: The question..
        :param Dict colors_dict: Color to use (String answer: String color)
        """
        colors = u""
        for answer, cardinality in question.answers_cardinality:
            if cardinality >= min_cardinality:
                try:
                    colors += u"{},".format(colors_dict[answer])
                except KeyError:
                    raise ValueError("Color for '%s' not provided" % answer)
        final_colors = []
        for color in colors.split(","):
            if color:
                final_colors.append(color)
        return u", ".join(final_colors)

    @staticmethod
    def get_results(question, min_cardinality):
        """ Return a formated string for a tikz pgf-pie chart.

        :param Question question: The question..
        :param Dict colors_dict: Color to use (String answer: String color)
        """
        pie = u""
        for answer, cardinality in question.answers_cardinality.iteritems():
            if cardinality >= min_cardinality:
                pie += u"{}/{},".format(cardinality, answer)
        final_answers = []
        for answer in pie.split(","):
            if answer:
                final_answers.append(answer)
        return u"            {}".format(u",\n            ".join(final_answers))

    @staticmethod
    def cloud(cloud, pie):
        """ Return the value expected in pgf-pie option for cloud. """
        if cloud and pie:
            raise ValueError("force_cloud and force_pie cannot both be true.")
        if cloud:
            return "cloud, "
        elif pie:
            return ""

    @staticmethod
    def chart(question, min_cardinality=0, radius=4, colors="", cloud=False,
              pie=True):
        """ Return a pfg-pie pie chart of a question.

        You must use pgf-pie for this to works ::

            \usepackage{pgf-pie}

        See : http://pgf-pie.googlecode.com/

        :param Question question: The question we want to plot
        :param int min_cardinality: Minimum cardinality that we display.
        :param int radius: Radius of the chart
        :param dict colors: A dict of colors value for answers (answers:color)
        :param boolean cloud: Is this chart a cloud chart ?
        :param boolean pie: Is this chart a pie chart ? """
        if colors:
            colors = "color={}" % Question2Tex.get_colors(
                question, min_cardinality, colors
            )
        results = Question2Tex.get_results(question, min_cardinality)
        if not results:
            return _("No answers for this question.")
        return """
\\begin{figure}
    \\begin{tikzpicture}
        \\pie[radius=%d, sum=auto,%s%s text=inside]{
%s
        }
    \\end{tikzpicture}
    \\caption{\label{figure:q%d} %s '%s'}
\\end{figure}
""" % (radius, Question2Tex.cloud(cloud, pie), colors, results, question.pk,
       _("Answers to the question"), question.text)
