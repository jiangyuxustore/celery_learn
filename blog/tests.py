from django.test import TestCase

from tasks import function_base_add, ClassBaseAdd
import unittest
from dxflearn.celery import app
# Create your tests here.


class TestFunctionBaseAdd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # app.conf.update(CELERY_ALWAYS_EAGER=True)
        cls.task = app.send_task("blog.function_base_debug", args=(2, 3))

    def test_task_state(self):
        self.assertEqual(self.task.state, 'success')

    def test_task_result(self):
        result = self.task.get(timeout=10)
        self.assertEqual(result, 5)


class TestClassBaseAdd(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # app.conf.update(CELERY_ALWAYS_EAGER=True)
        cls.task = app.send_task("blog.ClassBaseAdd", args=(3, 3))

    def test_task_state(self):
        self.assertEqual(self.task.state, 'success')

    def test_task_result(self):
        result = self.task.get(timeout=10)
        self.assertEqual(result, 6)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    test = [
        TestFunctionBaseAdd('test_task_result'),
        TestFunctionBaseAdd('test_task_state'),
        TestClassBaseAdd('test_task_result'),
        TestClassBaseAdd('test_task_state'),
    ]
    suite.addTests(test)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
