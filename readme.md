# Django survey

This is a django survey app, its based on and compatible with "django-survey".
This means you will be able to migrate from an ancient version of django-survey.

This has been refactored, ported to python 3, and test has been added as well as
exports as csv and pdf for the survey's results.

## Create survey

Using the admin interface you can create surveys, add questions, give questions
categories, and mark them as required or not. You can define choices for answers
using comma separated words.

![Creating of a question](doc/creating_questions.png "Creating of a question")

The front-end survey view then automatically populates based on the questions
that have been defined and published in the admin interface. We use bootstrap3
to render them.

![Answering a survey](doc/answering_questions.png "Answering a survey")

## Handling the results

Submitted responses can be viewed via the admin backend, in an exported csv
or in a pdf generated with latex. The way the pdf is generated is
configurable in a yaml file, globally, survey by survey, or question by
question. You can also limit the answers shown by cardinality or group them
together. This is an example of a configuration file

~~~~
generic:
    document_option: 11pt

Test survëy:
    document_class: report
    questions:
  Lorem ipsum dolor sit amët, <strong> consectetur </strong> adipiscing elit.:
      pie:
          type: polar
          text: pin
  Dolor sit amët, consectetur<strong>  adipiscing</strong>  elit.:
      pie:
          type: cloud
          text: inside
~~~~

The pdf is then generated using the very good pgf-pie library.

![The generated pdf for the polar and pin options](doc/report.png "The generated pdf for the polar and pin options")

![The generated pdf for the cloud and inside options](doc/report_2.png "The generated pdf for the cloud and inside options")

For a full example of a configuration file look at `example_conf.yaml`, you can
also generate your configuration file with the `generate_tex_configuration`
command, it will create the default skeleton for every survey and question.

## Getting started


In order to get started, install the requirements, create the database, create
a superuser, launch the server, then create your survey in the django admin :

  pip install -r requirements.txt
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver
  # Create survey in interface

You will have to change the settings in order to suit your need.

## Getting started as a contributor

You may want to use a virtualenv for python 2.7 or 3+ :

  python3.5 -m venv .3env/
  # Resp. for python 2.7 : virtualenv .env
  source .3env/bin/activate
  # Resp. for python 2.7 : source .env/bin/activate

In order to get started, install the dev requirements, create the database,
create a superuser, load the test dump, then launch the server :

  pip install -r requirements_dev.txt
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py loaddata survey/tests/testdump.json
  python manage.py runserver


### Test :

  python manage.py test survey

### Coverage :

  coverage run --source=survey ./manage.py test;coverage html
  xdg-open htmlcov/index.html

### Internationalisation :

  python manage.py makemessages --no-obsolete --no-wrap
  python manage.py runserver
  # Access http://localhost:8000/rosetta

### Lint :

  pylint survey

### Build the package :

    python setup.py build

# Credits

some inspiration came from an older
[django-survey](https://github.com/flynnguy/django-survey) app, but this app
uses a different model architecture and different mechanism for dynamic form
generation.
