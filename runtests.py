#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def main(argv):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))

if __name__ == "__main__":
    main(argv=sys.argv[1:])
