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
        print("\n".join([f'{x[0].strip().ljust(20)}:{x[1].strip()}' for x in help]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    parse_help_from_make(f'{os.path.join(os.getcwd(), "Makefile")}')
