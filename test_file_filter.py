#!/usr/bin/env python3

import file_filter
import unittest

class FileFilterTest(unittest.TestCase):
    def test_split(self):
        tests: list[tuple[str, list[str]]] = [
            ('1,2,3\n', ['1', '2', '3']),
            ('"1","2","3"\n', ['1', '2', '3']),
            ('"1",2,"3"\n', ['1', '2', '3']),
            ('1,"2",3\n', ['1', '2', '3']),
            ('"1,2",3,4\n', ['1,2', '3', '4']),
            ('"1"2,","3"\n', ['1"2,', '3']),
        ]
        for test_str, expected in tests:
            l = file_filter.split_line(test_str, ',', '"')
            self.assertEqual(expected, l)

if __name__ == '__main__':
    unittest.main()
