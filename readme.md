# Django survey

Using the admin interface you can create surveys, add questions, give questions
categories, and mark them as required or not. The front-end survey view then
automatically populates based on the questions that have been defined and
published in the admin interface.

Submitted responses can also be viewed via the admin backend. 


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
