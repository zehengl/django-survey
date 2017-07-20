# -*- coding: utf-8 -*-

import os
from datetime import datetime

from django.conf import settings


class LatexFile(object):

    """ Permit to handle the content of a LatexFile """

    def __init__(self, document_class, document_option="", use="",
                 header="", intro="", footer="", date=None):
        self.text = ""
        if date is None:
            date = datetime.now().strftime("%B %d, %Y")
        self.document_class = document_class
        self.document_option = document_option
        self.use = use
        self._header = header
        self.intro = intro
        self._footer = footer
        self.date = date

    @property
    def header(self):
        """ Return the header of a .tex file.

        :rtype: String """
        header = u"\\documentclass"
        if self.document_option:
            header += u"[{}]".format(self.document_option)
        header += u"{%s}\n" % self.document_class
        header += u"\date{%s}\n" % self.date
        header += u"%s\n" % self.use
        header += u"%s\n" % self._header
        header += u"\\begin{document}\n"
        header += u"%s\n" % self.intro
        return header

    @property
    def footer(self):
        """ Return the footer of a .tex file.

        :rtype: String """
        end = "\n\\end{document}\n"
        if self._footer:
            return self._footer + end
        else:
            return end

    def save(self, path):
        """ Save the document on disk. """
        with open(path, 'wb') as tex_file:
            tex_file.write(self.document.encode("UTF-8"))

    @property
    def document(self):
        """ Return the full text of the LatexFile.

        :rtype: String"""
        return u"{}{}{}".format(self.header, self.text, self.footer)
