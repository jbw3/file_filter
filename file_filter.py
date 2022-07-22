#!/usr/bin/python3

import argparse
import sys

class Row:
    def __init__(self, values):
        self._values = values

    def __len__(self):
        return len(self._values)

    def __getitem__(self, key):
        return self._values[key]

def filter_file(args, inFile, outFile):
    if args.filter is None:
        filter_row = lambda l, r: True
    else:
        filter_row = lambda l, r: eval(args.filter)

    header = inFile.readline()
    outFile.write(header)

    for line in inFile:
        split = line.rstrip('\r\n').split(',')
        row = Row(split)
        if filter_row(line, row):
            outFile.write(line)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-f', '--filter', help='Row filter expression')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    if args.filename is None:
        filter_file(args, sys.stdin, sys.stdout)
    else:
        with open(args.filename, 'r') as inFile:
            filter_file(args, inFile, sys.stdout)

if __name__ == '__main__':
    main()
