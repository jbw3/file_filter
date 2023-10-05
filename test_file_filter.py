#!/usr/bin/env python3

import file_filter
import unittest

class FileFilterTest(unittest.TestCase):
    def test_split(self):
        tests: list[tuple[str, tuple[list[str], list[bool]]]] = [
            ('1,2,3\n', (['1', '2', '3'], [False, False, False])),
            ('"1","2","3"\n', (['1', '2', '3'], [True, True, True])),
            ('"1",2,"3"\n', (['1', '2', '3'], [True, False, True])),
            ('1,"2",3\n', (['1', '2', '3'], [False, True, False])),
            ('"1,2",3,4\n', (['1,2', '3', '4'], [True, False, False])),
            ('"1"2,","3"\n', (['1"2,', '3'], [True, True])),
        ]
        for test_str, expected in tests:
            l = file_filter.split_line(test_str, ',', '"')
            self.assertEqual(expected, l)

if __name__ == '__main__':
    unittest.main()
