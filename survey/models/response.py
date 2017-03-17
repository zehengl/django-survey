# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .survey import Survey

class Response(models.Model):

    """
        A Response object is a collection of questions and answers with a
        unique interview uuid.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey)
    user = models.ForeignKey(User, null=True, blank=True)
    interview_uuid = models.CharField(_(u"Interview unique identifier"),
                                      max_length=36)

    class Meta(object):
        verbose_name = _('response')
        verbose_name_plural = _('responses')

    def __unicode__(self):
        try:
            # Survey can be None if we did not save it yet.
            survey = self.survey
        except:
            survey = ""
        msg = u"Response to {} by {}".format(survey, self.user)
        msg += u" on {}".format(self.created)
        return msg
