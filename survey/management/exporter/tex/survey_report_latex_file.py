# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from survey.management.exporter.tex.latex_file import LatexFile


class SurveyReportLatexFile(LatexFile):

    """ Permit to handle the content of a LatexFile """

    USE = """
\usepackage{pgf-pie}
\usepackage{pgfplots}
\usepackage{pgfplotstable}
\usetikzlibrary{patterns}
"""

    def __init__(self):
        try:
            document_class = settings.TEX_DOCUMENT_CLASS
        except AttributeError:
            msg = "Please give a value for TEX_DOCUMENT_CLASS in the settings."
            raise ImproperlyConfigured(msg)
        document_option = self.__get_optional_setting("TEX_DOCUMENT_OPTION")
        header = self.__get_optional_setting("TEX_HEADER")
        intro = self.__get_optional_setting("TEX_INTRO")
        date = self.__get_optional_setting("TEX_DATE")
        footer = self.__get_optional_setting("TEX_FOOTER")
        super(SurveyReportLatexFile, self).__init__(
            document_class, document_option, SurveyReportLatexFile.USE, header,
            intro, footer, date
        )

    def __get_optional_setting(self, name):
        """ Try to get an optional settings. """
        try:
            return getattr(settings, name)
        except AttributeError:
            return ""
