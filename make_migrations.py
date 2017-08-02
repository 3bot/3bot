import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")
    from django.core.management import execute_from_command_line
    args = sys.argv + ["makemigrations", "threebot"]
    execute_from_command_line(args)
