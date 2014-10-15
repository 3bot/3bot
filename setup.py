# -*- encoding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages
import threebot as app

setup(
    name="threebot",
    version=app.__version__,
    author_email="admin@arteria.ch",
    maintainer_email="renner@arteria.ch",
    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "jsonfield",
        "django-sekizai",
        "pyzmq",
        "threebot_crypto",
    ],

)
