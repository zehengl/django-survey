#!/bin/bash
coverage run --source=survey --omit=survey/migrations/* ./manage.py test
coverage html
