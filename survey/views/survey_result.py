# -*- coding: utf-8 -*-

import codecs
import cStringIO
import csv

from django.http.response import HttpResponse
from django.views.generic.base import View

from survey.management.survey2csv import Survey2CSV
from survey.models import Survey


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class SurveyResult(View):

    template_name = 'survey/result.html'

    def get(self, request, pk):
        survey = Survey.objects.get(pk=pk)
        """        try:
            current_csv = self.csv[pk]
        except AttributeError:
            self.csv = {}
            self.csv[pk] = Survey2CSV.survey_to_csv(survey)
            current_csv = self.csv[pk]"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = u'attachment; filename="{}.csv"'.format(survey.name)
        writer = UnicodeWriter(response)
        header, question_order = Survey2CSV.get_header_and_order(survey)
        writer.writerow(header)
        for response in survey.responses.all():
            row = Survey2CSV.get_user_line(question_order, response)
            writer.writerow(row)
        return response
