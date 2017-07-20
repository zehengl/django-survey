import os

from django.conf import settings
from setuptools import find_packages, setup

import sys
if sys.version_info < (2, 6):
    sys.exit('Sorry, Python < 2.6 is not supported')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

install_requires = []
for package in open("requirements.txt", "r"):
    install_requires = package.replace("\n", "").split("#")[0]

setup(
    name="survey",
    version=settings.VERSION,
    author="Pierre SASSOULAS",
    author_email="pierre.sassoulas@gmail.com",
    license="AGPL",
    url="https://github.com/Pierre-Sassoulas/django-survey",
    packages=find_packages(exclude=["survey.tests*", ]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language  :: Python :: 3",
        "Framework :: Django",
    ],
    install_requires=install_requires,
)
