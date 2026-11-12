import io
import unittest

from csv_check import validate


class ValidationTests(unittest.TestCase):
    def test_physical_line_after_multiline_field(self):
        source = io.StringIO('id,note\n1,"a\nb"\n1,c\n')
        self.assertEqual(validate(source, [], [], [], ["id"])[0]["line"], 4)

    def test_missing_header_is_reported_before_rows(self):
        source = io.StringIO("id\n1\n")
        self.assertEqual(validate(source, ["email"], [], [], [])[0]["columns"], ["email"])

    def test_duplicate_composite_key(self):
        source = io.StringIO("account,order\n1,1\n2,1\n1,1\n")
        errors = validate(source, [], [], [], ["account", "order"])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["line"], 4)
