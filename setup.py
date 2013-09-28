#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='couchlog',
    version='0.0.1',
    description='Dimagi Couch Log for Django',
    author='Dimagi',
    author_email='information@dimagi.com',
    url='http://www.dimagi.com/',
    install_requires = [
        "couchdbkit",
        "django",
        "dimagi-utils",
        "requests",
    ],
    packages = find_packages(exclude=['*.pyc']),
    include_package_data=True
)

