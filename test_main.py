import unittest
import main


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.fixtures = [
            ('(((([{}]))))', True),
            ('[([])((([[[]]])))]{()}', True),
            ('{{[()]}}', True),
            ('}{}', False),
            ('{{[(])]}}', False),
            ('[[{())}]', False)
        ]

    def test_bracket_validator(self):
        for fixture, expected_result in self.fixtures:
            self.assertEqual(main.bracket_validator(fixture), expected_result)
