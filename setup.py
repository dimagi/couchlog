#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='couchlog',
    version='0.0.1',
    description='Dimagi Couch Log for Django',
    author='Dimagi',
    author_email='information@dimagi.com',
    url='http://www.dimagi.com/',
    install_requires=[
        "couchdbkit",
        "django==1.7.10",
        "dimagi-utils==1.2.2",
        "requests",
    ],
    packages=find_packages(exclude=['*.pyc']),
    include_package_data=True,
    dependency_links=[
        'git+git://github.com/dimagi/dimagi-utils.git@2533a1aa96fd91a855b153e7bb9c15275ef844e7#egg=dimagi-utils-1.3usec',
    ],
)
