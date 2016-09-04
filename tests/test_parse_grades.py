import gzip
import unittest
from qisbot import parse_grades
from qisbot import GRADE_MAPPING


class TestParseGrades(unittest.TestCase):

    def setUp(self):
        with gzip.open('grade_overview.html.gz', 'r') as source_file:
            self.source = source_file.read()

    def test_parse_grades(self):
        result = parse_grades(self.source)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 7)
        for grade in result:
            self.assertTrue(type(grade) is dict)
            for key in GRADE_MAPPING:
                # Mapping should work completely
                self.assertIn(key, grade.keys())
