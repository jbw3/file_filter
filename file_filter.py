#!/usr/bin/env python3

import argparse
from collections.abc import Iterable
import sys
from typing import Any, Callable, IO

class Schema:
    def __init__(self, delimiter: str, qualifier: str|None) -> None:
        self.header_indexes: dict[str, int] = {}
        self.delimiter = delimiter
        self.qualifier = qualifier

class Row:
    def __init__(self, schema: Schema, values: list[str], qualified: list[bool]|None) -> None:
        self._schema = schema
        self._values = values
        self._qualified = qualified

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, key: int|str|slice) -> str|list[str]:
        if type(key) is int:
            idx = key
        elif type(key) is str:
            idx = self._schema.header_indexes[key]
        elif type(key) is slice:
            idx = key
        else:
            raise TypeError('Invalid index type')
        return self._values[idx]

    def __iter__(self) -> Iterable[str]:
        return iter(self._values)

    def to_line_str(self, delimiter: str, qualifier: str|None) -> str:
        if qualifier is None or self._qualified is None:
            line = delimiter.join(self._values)
        else:
            # TODO: make this more efficient
            str_values: list[str] = []
            for i, v in enumerate(self._values):
                if self._qualified[i]:
                    str_values.append(qualifier + v + qualifier)
                else:
                    str_values.append(v)

            line = delimiter.join(str_values)

        return line

    def get_index(self, key: int|str) -> int:
        if type(key) is int:
            idx = key
        elif type(key) is str:
            idx = self._schema.header_indexes[key]
        else:
            raise TypeError('Invalid index type')
        return idx

    def append(self, *args: Any) -> 'Row':
        self._values.extend(args)
        if self._qualified is not None and self._schema.qualifier is not None:
            for arg in args:
                needs_qual = self._schema.delimiter in str(arg)
                self._qualified.append(needs_qual)

        return self

    def remove(self, *keys: int|str) -> 'Row':
        indexes: list[int] = []
        for key in keys:
            idx = self.get_index(key)
            indexes.append(idx)

        # remove items from greatest to least index to prevent the indexes
        # from getting off as items are removed
        indexes.sort(reverse=True)
        for i in indexes:
            self._values.pop(i)
            if self._qualified is not None and self._schema.qualifier is not None:
                self._qualified.pop(i)

        return self

    def insert(self, key: int|str, value: Any) -> 'Row':
        idx = self.get_index(key)
        self._values.insert(idx, value)
        if self._qualified is not None and self._schema.qualifier is not None:
            needs_qual = self._schema.delimiter in str(value)
            self._qualified.insert(idx, needs_qual)
        return self

    def replace(self, key: int|str, value: Any) -> 'Row':
        idx = self.get_index(key)
        self._values[idx] = value
        if self._qualified is not None and self._schema.qualifier is not None:
            needs_qual = self._schema.delimiter in str(value)
            self._qualified.insert(idx, needs_qual)

        return self

    def replace_if(self, condition: bool, key: int|str, value: Any) -> 'Row':
        if condition:
            self.replace(key, value)
        return self

def get_delimiter(args: argparse.Namespace) -> str:
    if args.delimiter is not None:
        return args.delimiter

    if args.filename is not None:
        if args.filename.endswith('.csv'):
            return ','
        elif args.filename.endswith('.psv'):
            return '|'
        elif args.filename.endswith('.tsv'):
            return '\t'

    return ','

def split_line_qualifier(line: str, delimiter: str, qualifier: str) -> tuple[list[str], list[bool]]:
    items: list[str] = []
    qualified: list[bool] = []
    start = 0
    line_end = len(line)
    q_len = len(qualifier)
    qual_del = qualifier + delimiter
    qual_del_len = len(qual_del)
    while start < line_end:
        if line[start:start+q_len] == qualifier:
            in_qual = True
            start += 1
            end = line.find(qualifier, start + 1)
            while end < line_end - 1 and line[end + 1] != delimiter:
                end = line.find(qualifier, end + 1)
            inc = qual_del_len
        else:
            in_qual = False
            end = line.find(delimiter, start + 1)
            inc = len(delimiter)
        if end < 0:
            end = line_end

        items.append(line[start:end])
        qualified.append(in_qual)
        start = end + inc

    return items, qualified

def split_line(line: str, delimiter: str, qualifier: str|None) -> tuple[list[str], list[bool]|None]:
    line = line.rstrip('\r\n')
    if qualifier is None:
        values = line.split(delimiter)
        qualified = None
    else:
        values, qualified = split_line_qualifier(line, delimiter, qualifier)

    return values, qualified

def to_line(object: Any, delimiter: str, qualifier: str|None) -> str:
    if type(object) is Row:
        line = object.to_line_str(delimiter, qualifier)
    elif type(object) is not str and isinstance(object, Iterable):
        line = delimiter.join((str(i) for i in object))
    else:
        line = str(object)
    if not line.endswith('\n'):
        line += '\n'
    return line

def write_lines_all_options(args: argparse.Namespace, inFile: IO[str], outFile: IO[str], delim: str, qual: str|None, schema: Schema) -> None:
    filter_row: Callable[[str, Row], bool] | None
    if args.filter is None:
        filter_row = None
    else:
        co = compile(args.filter, '<string>', 'eval')
        def filter_row_func(l: str, r: Row) -> bool:
            return eval(co, {}, {'l': l, 'r': r})
        filter_row = filter_row_func

    map_row: Callable[[str, Row], Any] | None
    if args.map is None:
        map_row = None
    else:
        co = compile(args.map, '<string>', 'eval')
        def map_row_func(l: str, r: Row) -> Any:
            return eval(co, {}, {'l': l, 'r': r})
        map_row = map_row_func

    # write lines
    count = 0
    for line in inFile:
        if args.limit is not None and count >= args.limit:
            break

        if filter_row is not None or map_row is not None:
            values, qualified = split_line(line, delim, qual)
            row = Row(schema, values, qualified)
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
                new_line = to_line(map_out, delim, qual)
            else:
                new_line = line

            outFile.write(new_line)
            count += 1

def write_lines_limit(inFile: IO[str], outFile: IO[str], limit: int) -> None:
    for line in inFile:
        if limit <= 0:
            break
        outFile.write(line)
        limit -= 1

def write_all(inFile: IO[str], outFile: IO[str]) -> None:
    data = inFile.read(4096)
    while data != '':
        outFile.write(data)
        data = inFile.read(4096)

def filter_file(args: argparse.Namespace, inFile: IO[str], outFile: IO[str]) -> None:
    delim = get_delimiter(args)
    qual: str|None = args.qualifier

    # parse header
    schema = Schema(delim, qual)
    if not args.no_header:
        header = inFile.readline()
        header_values, header_qualified = split_line(header, delim, qual)
        schema.header_indexes = {c: i for i, c in enumerate(header_values)}

        if args.header_map is not None:
            row = Row(schema, header_values, header_qualified)
            header_out = eval(args.header_map, {}, {'l': header, 'r': row})
            new_header = to_line(header_out, delim, qual)
            outFile.write(new_header)
        else:
            outFile.write(header)

    # skip lines
    if args.offset is not None:
        count = 1
        while count < args.offset:
            inFile.readline()
            count += 1

    # write lines
    if args.filter is not None or args.map is not None:
        write_lines_all_options(args, inFile, outFile, delim, qual, schema)
    elif args.limit is not None:
        write_lines_limit(inFile, outFile, args.limit)
    else:
        write_all(inFile, outFile)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', help='input file')
    parser.add_argument('-d', '--delimiter', help='column delimiter')
    parser.add_argument('-f', '--filter', help='row filter expression')
    parser.add_argument('-H', '--header-map', help='header row mapping expression')
    parser.add_argument('-l', '--limit', type=int, help='max number of rows to output (excluding header)')
    parser.add_argument('-m', '--map', help='row mapping expression')
    parser.add_argument('--no-header', action='store_true', help='do not treat first row as header')
    parser.add_argument('-o', '--offset', type=int, help='starting row to output (excluding header)')
    parser.add_argument('--out', help='output file')
    parser.add_argument('-q', '--qualifier', help='column qualifier')

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
