#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages
from os.path import join, dirname
import threebot as app


def long_description():
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return "LONG_DESCRIPTION Error"

setup(
    name="threebot",
    version=app.__version__,
    description="3bot is an open-source software platform to build, configure and perform your repetitive tasks.",
    long_description=long_description(),
    author='arteria GmbH',
    author_email="admin@arteria.ch",
    maintainer_email="renner@arteria.ch",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements.txt').read().split('\n'),
)
