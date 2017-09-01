# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import copy
import logging
import os

import yaml
from django.conf import settings
from future import standard_library

from survey.models.survey import Survey

standard_library.install_aliases()


LOGGER = logging.getLogger(__name__)


class Configuration(object):

    DEFAULT_PATH = os.path.join(settings.ROOT, "survey", "management",
                                "exporter", "tex", "default_conf.yaml")

    def __init__(self, configuration_file=None):
        self._default = self._init_from_file(self.DEFAULT_PATH)
        if configuration_file is not None:
            self._conf = self._init_from_file(configuration_file)
        else:
            self._conf = {}

    def __str__(self, *args, **kwargs):
        # Default flow style prevent
        # b:
        #   c: 3
        #   d: 4
        # To become the ugly :
        # b: {c: 3, d: 4}
        return yaml.safe_dump(
            self._conf, default_flow_style=False, encoding=None,
            allow_unicode=True
        )

    @property
    def valid_survey_names(self):
        """ Return a list of the valid name for a survey. """
        vsn = [survey.name for survey in Survey.objects.all()]
        vsn.append("generic")
        return vsn

    def check_survey_exists(self, survey_name):
        """ Check if the survey name exists.

        :param String survey_name: The name of a survey. """
        if type(survey_name) == Survey:
            msg = "Expecting a string for 'survey_name' and got a Survey "
            msg += " ('{}').".format(survey_name)
            raise TypeError(msg)
        if survey_name not in self.valid_survey_names:
            msg = "'{}' is not an existing survey in the ".format(survey_name)
            msg += "database.\nPossible values are :\n"
            for name in self.valid_survey_names:
                msg += "- '{}'\n".format(name)
            # Remove the last "\n"
            msg = msg[:-1]
            LOGGER.warning(msg)

    def __getitem__(self, survey_name):
        return self.get(survey_name=survey_name)

    def _init_from_file(self, filepath):
        """ Return a configuration from a filepath.

        :param String filepath: The path of the yaml configuration file.
        :rtype: Dict """
        with open(filepath, 'r') as f:
            configuration = yaml.load(f)
        for survey_name in configuration.keys():
            self.check_survey_exists(survey_name)
            if not configuration[survey_name]:
                raise ValueError("Nothing in %s's configuration" % survey_name)
        return configuration

    def optional_update(self, dict_, update_dict, key):
        """ Update a dict with another one if optional key exists. """
        try:
            self.recursive_update(dict_, update_dict[key])
        except KeyError:
            # There is not configuration file for key, only the default one
            pass

    def recursive_update(self, d, u):
        """ Update a dict recursively. It permit to keep the default value by
        default and to be able to replace them by dictionaries.
        """
        import collections
        # print("d", d, "u", u)
        if d is None:
            return u
        for k, v in u.items():
            # print("k", k, "v", v)
            if isinstance(v, collections.Mapping):
                r = self.recursive_update(d.get(k, {}), v)
                # print("Recursive value for {} :{}".format(k, v))
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def get_default_question_conf(self, conf):
        return {"chart": copy.deepcopy(conf["chart"]), }

    def get(self, key=None, survey_name=None, question_text=None):
        """ Get a configuration file for a survey or a specific question.

        :param String key: The key we want to get.
        :param String survey_name: The name of a specific survey.
        :param String question_text: The text of a specific question.
        :param String category_name """
        LOGGER.debug(
            "Configuration.get(key=%s, survey_name=%s, question_text=%s",
            key, survey_name, question_text
        )
        conf = copy.deepcopy(self._default["generic"])
        self.optional_update(conf, self._conf, "generic")
        if survey_name is not None:
            self.check_survey_exists(survey_name)
            if type(survey_name) is Survey:
                survey_name = survey_name.name
            self.recursive_update(conf, self._conf.get(survey_name, {}))
        if conf.get("questions"):
            for question in conf.get("questions"):
                qdc = self.get_default_question_conf(conf)
                self.recursive_update(qdc, conf["questions"][question])
                conf["questions"][question] = qdc
        if question_text:
            qconf = False
            if conf.get("questions"):
                try:
                    conf = conf["questions"][question_text]
                    qconf = True
                except KeyError:
                    LOGGER.warning("No configuration for question '%s'",
                                   question_text)
            if not qconf:
                conf = self.get_default_question_conf(conf)
        if key is None:
            return conf
        try:
            return conf[key]
        except KeyError:
            msg = "{} does not exists. ".format(key)
            msg += "Possible values : {}".format(conf.keys())
            raise ValueError(msg)
