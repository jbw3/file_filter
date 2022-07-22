#!/usr/bin/python3

import argparse
import sys

def filter_file(args, inFile, outFile):
    if args.filter is None:
        filter_row = lambda l: True
    else:
        filter_row = lambda l: eval(args.filter)

    for line in inFile:
        if filter_row(line):
            print(line, end='', file=outFile)

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
