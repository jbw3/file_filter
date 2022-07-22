#!/usr/bin/python3

import argparse
import sys

class Row:
    def __init__(self, header_indexes, values):
        self._header_indexes = header_indexes
        self._values = values

    def __len__(self):
        return len(self._values)

    def __getitem__(self, key):
        if type(key) == int:
            idx = key
        else:
            idx = self._header_indexes[key]
        return self._values[idx]

def filter_file(args, inFile, outFile):
    if args.filter is None:
        filter_row = lambda l, r: True
    else:
        filter_row = lambda l, r: eval(args.filter)

    split_str = ','

    header_indexes = {}
    if not args.no_header:
        header = inFile.readline()
        outFile.write(header)
        header_split = header.rstrip('\r\n').split(split_str)
        idx = 0
        for col in header_split:
            header_indexes[col] = idx
            idx += 1

    for line in inFile:
        split = line.rstrip('\r\n').split(split_str)
        row = Row(header_indexes, split)
        if filter_row(line, row):
            outFile.write(line)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', help='Input file')
    parser.add_argument('-f', '--filter', help='Row filter expression')
    parser.add_argument('--no-header', action='store_true', help='Do not treat first row as header')
    parser.add_argument('-o', '--output', help='Output file')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    try:
        if args.filename is None or args.filename == '-':
            inFile = sys.stdin
        else:
            inFile = open(args.filename, 'r')
        if args.output is None:
            outFile = sys.stdout
        else:
            outFile = open(args.output, 'w')

        filter_file(args, inFile, outFile)

    finally:
        if inFile != sys.stdin:
            inFile.close()
        if outFile != sys.stdout:
            outFile.close()

if __name__ == '__main__':
    main()
