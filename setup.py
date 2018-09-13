
import sys

from setuptools import find_packages, setup


if sys.version_info < (3, 0):
    sys.exit('Sorry, Python < 3.0 is not supported')


def add_package(package_list, package):
    package = package.replace("\n", "").split("#")[0]
    if package:
        package_list.append(package)

setup(
    name="django-survey-and-report",
    version="1.3.0",
    description="A django survey app, based on and compatible with "
                "'django-survey'",
    long_description="A django survey app, based on and compatible with \"django-survey\"."
"You will be able to migrate your data from an ancient version of "
"django-survey, but it has been ported to python 3 and you can export results"
" as CSV or PDF using your native language.",
    author="Pierre SASSOULAS",
    author_email="pierre.sassoulas@gmail.com",
    license="AGPL",
    url="https://github.com/Pierre-Sassoulas/django-survey",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Natural Language :: French",
        "Natural Language :: Japanese",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        "Framework :: Django",
    ],
    install_requires=[
        "Django", "django-bootstrap-form", "django-tastypie",
        "django-registration", "pytz", "future", "ordereddict", "PyYAML",
        "matplotlib", "seaborn", "numpy"
    ],
    extras_require={
        'dev': ["django-rosetta", "pylint", "coverage", "mock"],
    },
)
