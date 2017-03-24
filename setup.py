import os

from django.conf import settings
from setuptools import find_packages, setup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

install_requires = []
for package in open("requirements.txt", "r"):
    install_requires = package.replace("\n", "").split("#")[0]

setup(
    name="survey",
    version=settings.VERSION,
    author="Jessy Kate Schingler",
    author_email="jessy@jessykate.com",
    license="AGPL",
    url="https://github.com/jessykate/django-survey",
    packages=find_packages(exclude=["survey.tests*", ]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    install_requires=install_requires,
)
