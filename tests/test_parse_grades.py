import gzip
import unittest
from qisbot import parse_grades


class TestParseGrades(unittest.TestCase):

    def setUp(self):
        with gzip.open('grade_overview.html.gz', 'r') as source_file:
            self.source = source_file.read()

    def test_parse_grades(self):
        result = parse_grades(self.source)
        self.assertIsNotNone(result)
