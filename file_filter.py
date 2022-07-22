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
    parser.add_argument('-o', '--output', help='Output file')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    try:
        if args.filename is None:
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
