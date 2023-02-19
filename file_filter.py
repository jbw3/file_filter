#!/usr/bin/python3

import argparse
from collections.abc import Iterable
import sys
from typing import Any, Callable, IO

class Row:
    def __init__(self, header_indexes: dict[str, int], values: list[str]) -> None:
        self._header_indexes = header_indexes
        self._values = values

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, key: int|str|slice) -> str|list[str]:
        if type(key) is int:
            idx = key
        elif type(key) is str:
            idx = self._header_indexes[key]
        elif type(key) is slice:
            idx = key
        else:
            raise TypeError('Invalid index type')
        return self._values[idx]

def get_split_str(args: argparse.Namespace) -> str:
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

def filter_file(args: argparse.Namespace, inFile: IO[str], outFile: IO[str]) -> None:
    filter_row: Callable[[str, Row], bool] | None
    if args.filter is None:
        filter_row = None
    else:
        def filter_row_func(l: str, r: Row) -> bool:
            return eval(args.filter)
        filter_row = filter_row_func

    map_row: Callable[[str, Row], Any] | None
    if args.map is None:
        map_row = None
    else:
        def map_row_func(l: str, r: Row) -> Any:
            return eval(args.map)
        map_row = map_row_func

    split_str = get_split_str(args)

    # parse header
    header_indexes: dict[str, int] = {}
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

        if filter_row is not None or map_row is not None:
            split = line.rstrip('\r\n').split(split_str)
            row = Row(header_indexes, split)
        else:
            row = None

        write_row = True
        if filter_row is not None:
            assert row is not None
            write_row = filter_row(line, row)

        if write_row:
            if map_row is not None:
                assert row is not None
                map_out = map_row(line, row)
                if type(map_out) is not str and isinstance(map_out, Iterable):
                    new_line = split_str.join((str(i) for i in map_out))
                else:
                    new_line = str(map_out)
                if not new_line.endswith('\n'):
                    new_line += '\n'
            else:
                new_line = line

            outFile.write(new_line)
            count += 1

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', help='Input file')
    parser.add_argument('-f', '--filter', help='Row filter expression')
    parser.add_argument('-l', '--limit', type=int, help='Max number of rows to output (excluding header)')
    parser.add_argument('-m', '--map', help='Row mapping expression')
    parser.add_argument('--no-header', action='store_true', help='Do not treat first row as header')
    parser.add_argument('-o', '--offset', type=int, help='Starting row to output (excluding header)')
    parser.add_argument('--out', help='Output file')
    parser.add_argument('--split', help='String to split columns')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    inFile: IO[str]|None = None
    outFile: IO[str]|None = None
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
        if inFile is not None and inFile != sys.stdin:
            inFile.close()
        if outFile is not None and outFile != sys.stdout:
            outFile.close()

if __name__ == '__main__':
    main()
