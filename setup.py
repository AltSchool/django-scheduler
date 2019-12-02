#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from setuptools import setup



setup(
    name='django-scheduler',
    version='10.7.15',
    description='A calendaring app for Django.',
    author='Leonardo Lazzaro',
    author_email='lazzaroleonardo@gmail.com',
    url='https://github.com/llazzaro/django-scheduler',
    packages=[
        'schedule',
        'schedule.conf',
        'schedule.feeds',
        'schedule.management',
        'schedule.management.commands',
        'schedule.models',
        'schedule.migrations',
        'schedule.templatetags',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    install_requires=[
        'python-dateutil>=2.1.post20140303',
        'Django>=1.8,<=2.0',
        'argparse>=1.1',
        'pytz>=2013.9',
        'six>=1.3.0',
        'icalendar>=3.8.4',
        'django-annoying>=0.7.9',
        'coverage>=3.6',
        'pyyaml>=3.11',
    ],
    dependency_links = ['http://github.com/AltSchool/dateutil/tarball/master#egg=python-dateutil-2.1.post20140303'],
    license='BSD',
    test_suite='runtests.runtests',
)
