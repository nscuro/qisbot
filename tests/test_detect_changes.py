import unittest
from qisbot import detect_changes


class TestDetectAdditions(unittest.TestCase):

    def setUp(self):
        self.grades_old = [{'exam_id': 0}, {'exam_id': 1}, {'exam_id': 2}]
        self.grades_new = [{'exam_id': 4}, {'exam_id': 2}, {'exam_id': 1}, {'exam_id': 0}]

    def test_detect_additions(self):
        diff = detect_changes(self.grades_old, self.grades_new)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0]['exam_id'], 4)


class TestDetectChanges(unittest.TestCase):

    def setUp(self):
        self.grades_old = [{'exam_id': 0, 'grade': 2.0}, {'exam_id': 1, 'grade': 4.5}]
        self.grades_new = [{'exam_id': 1, 'grade': 2.0}, {'exam_id': 0, 'grade': 4.5}]

    def test_detect_changes(self):
        diff = detect_changes(self.grades_old, self.grades_new)
        self.assertEqual(len(diff), 2)
