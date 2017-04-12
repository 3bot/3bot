from django.utils import unittest
from threebot.models import Task


class TaskTestCase(unittest.TestCase):
    def setUp(self):
        self.make1 = Task.objects.create(title="make1")
        self.make2 = Task.objects.create(title="make2")

    def test_task_can_extract_inputs(self):
        """"""
        self.assertEqual(self.make1.extract_inputs(), {})
        self.assertEqual(self.make2.extract_inputs(), {})
