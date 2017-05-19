# -*- coding: utf-8 -*-

import datetime
import os

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from survey.management.survey2csv import Survey2CSV
from survey.models import Survey


def serve_unprotected_result_csv(survey):
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
    with open(Survey2CSV.file_name(survey), 'r') as f:
        response = HttpResponse(f.read(), content_type='text/csv')
    cd = u'attachment; filename="{}.csv"'.format(survey.name)
    response['Content-Disposition'] = cd
    return response


@login_required
def serve_protected_result(request, survey):
    return serve_unprotected_result_csv(survey)


def serve_result_csv(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    print survey.need_logged_user
    if survey.need_logged_user:
        return serve_protected_result(request, survey)
    else:
        return serve_unprotected_result_csv(survey)
