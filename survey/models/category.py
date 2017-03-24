# -*- coding: utf-8 -*-

from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from .survey import Survey


class Category(models.Model):
    name = models.CharField(max_length=400)
    survey = models.ForeignKey(Survey)
    order = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)

    class Meta(object):
        # pylint: disable=too-few-public-methods
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __unicode__(self):
        return self.name

    def slug(self):
        return slugify(unicode(self))
