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

def get_split_str(args):
    if args.split is not None:
        return args.split

    if args.filename is not None:
        if args.filename.endswith('.csv'):
            return ','
        elif args.filename.endswith('.psv'):
            return '|'
        elif args.filename.endswith('.tsv'):
            return '\t'

    return ','

def filter_file(args, inFile, outFile):
    if args.filter is None:
        filter_row = None
    else:
        filter_row = lambda l, r: eval(args.filter)

    split_str = get_split_str(args)

    # parse header
    header_indexes = {}
    if not args.no_header:
        header = inFile.readline()
        outFile.write(header)
        header_split = header.rstrip('\r\n').split(split_str)
        idx = 0
        for col in header_split:
            header_indexes[col] = idx
            idx += 1

    # skip lines
    if args.offset is not None:
        count = 1
        while count < args.offset:
            inFile.readline()
            count += 1

    # write lines
    count = 0
    for line in inFile:
        if args.limit is not None and count >= args.limit:
            break

        write_row = True
        if filter_row is not None:
            split = line.rstrip('\r\n').split(split_str)
            row = Row(header_indexes, split)
            write_row = filter_row(line, row)

        if write_row:
            outFile.write(line)
            count += 1

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', help='Input file')
    parser.add_argument('-f', '--filter', help='Row filter expression')
    parser.add_argument('-l', '--limit', type=int, help='Max number of rows to output (excluding header)')
    parser.add_argument('--no-header', action='store_true', help='Do not treat first row as header')
    parser.add_argument('-o', '--offset', type=int, help='Starting row to output (excluding header)')
    parser.add_argument('--out', help='Output file')
    parser.add_argument('--split', help='String to split columns')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    try:
        if args.filename is None or args.filename == '-':
            inFile = sys.stdin
        else:
            inFile = open(args.filename, 'r')
        if args.out is None:
            outFile = sys.stdout
        else:
            outFile = open(args.out, 'w')

        filter_file(args, inFile, outFile)

    finally:
        if inFile != sys.stdin:
            inFile.close()
        if outFile != sys.stdout:
            outFile.close()

if __name__ == '__main__':
    main()
