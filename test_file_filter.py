#!/usr/bin/env python3

import file_filter
import unittest

class FileFilterTest(unittest.TestCase):
    def test_split(self):
        tests = [
            ('1,2,3\n', ['1', '2', '3']),
            ('"1","2","3"\n', ['1', '2', '3']),
            ('"1",2,"3"\n', ['1', '2', '3']),
            ('1,"2",3\n', ['1', '2', '3']),
            ('"1,2",3,4\n', ['1,2', '3', '4']),
            ('"1"2,","3"\n', ['1"2,', '3']),
        ]
        for test in tests:
            l = file_filter.split_line(test[0], ',', '"')
            self.assertEqual(l, test[1])

if __name__ == '__main__':
    unittest.main()
