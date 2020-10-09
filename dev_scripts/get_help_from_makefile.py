#!/usr/bin/env python
import re
import argparse
import os

help_pattern = re.compile(r'(^[a-zA-Z\-]+):([a-zA-Z\- ]*)##(.*?)$')


def parse_help_from_make(filename):
    with open(filename, 'r') as make_in:
        lines = make_in.readlines()
        help = []
        for line in lines:
            m = help_pattern.match(line)
            if m:
                help.append((m.group(1), m.group(3)))

        help = sorted(help, key=lambda x: x[0])
        return help


def print_help(help_items):
    print("\n".join([f'{x[0].strip().ljust(20)}:{x[1].strip()}' for x in help_items]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default=[], action="append", help="Path to makefile")
    args = parser.parse_args()

    if args.file:
        help_items = []
        print(args.file)
        for f in args.file:
            help_items.extend(parse_help_from_make(os.path.abspath(f)))
    else:
        help_items = parse_help_from_make(f'{os.path.join(os.getcwd(), "Makefile")}')

    print_help(help_items)
