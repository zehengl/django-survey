# -*- coding: utf-8 -*-

import datetime
import os

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from survey.management.survey2csv import Survey2CSV
from survey.models import Survey


def serve_unprotected_result_csv(survey):
    """ Return the csv corresponding to a survey. """
    try:
        latest_answer = survey.latest_answer_date()
        csv_modification_time = os.path.getmtime(Survey2CSV.file_name(survey))
        csv_time = datetime.datetime.fromtimestamp(csv_modification_time)
        csv_time = csv_time.replace(tzinfo=latest_answer.tzinfo)
        if latest_answer > csv_time:
            # If the file was generated before the last answer, generate it.
            Survey2CSV.generate_file(survey)
    except OSError:
        # If the file do not exist, generate it.
        Survey2CSV.generate_file(survey)
    with open(Survey2CSV.file_name(survey), 'r') as csv_file:
        response = HttpResponse(csv_file.read(), content_type='text/csv')
    content_disposition = u'attachment; filename="{}.csv"'.format(survey.name)
    response['Content-Disposition'] = content_disposition
    return response


@login_required
def serve_protected_result(request, survey):
    """ Return the csv only if the user is logged. """
    return serve_unprotected_result_csv(survey)


def serve_result_csv(request, pk):
    """ ... only if the survey does not require login or the user is logged.

    :param int pk: The primary key of the survey. """
    survey = get_object_or_404(Survey, pk=pk)
    if survey.need_logged_user:
        return serve_protected_result(request, survey)
    else:
        return serve_unprotected_result_csv(survey)
