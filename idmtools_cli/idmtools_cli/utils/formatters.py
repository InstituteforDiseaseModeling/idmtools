"""Utility functions around formatting output for cli."""
from __future__ import absolute_import
import re
from .utils import tsplit, schunk

NEWLINES = ('\n', '\r', '\r\n')


def clean(s: str):
    """
    Clean string so that all special formatting is stripped.

    Args:
        s: str

    Returns:
        Cleaned string
    """
    strip = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    txt = strip.sub('', s)

    return txt


def min_width(string, cols: int, padding=' '):
    """
    Returns given string with right padding.

    Args:
        string: string to be formatted
        cols: min width the text to be formatted
        padding: Padding

    Returns:
        String formatted with min width
    """
    stack = tsplit(str(string), NEWLINES)

    for i, substring in enumerate(stack):
        _sub = clean(substring).ljust((cols + 0), padding)
        stack[i] = _sub

    return '\n'.join(stack)


def max_width(string: str, cols: int, separator='\n'):
    """
    Returns a freshly formatted.

    Args:
        string: string to be formatted
        cols: max width the text to be formatted
        separator: separator to break rows

    Returns:
        String formatted with max width
    """
    stack = tsplit(string, NEWLINES)

    for i, substring in enumerate(stack):
        stack[i] = substring.split()

    _stack = []

    for row in stack:
        _row = ['', ]
        _row_i = 0

        for word in row:
            if (len(_row[_row_i]) + len(word)) <= cols:
                _row[_row_i] += word
                _row[_row_i] += ' '

            elif len(word) > cols:

                # ensure empty row
                if len(_row[_row_i]):
                    _row[_row_i] = _row[_row_i].rstrip()
                    _row.append('')
                    _row_i += 1

                chunks = schunk(word, cols)
                for i, chunk in enumerate(chunks):
                    if i + 1 != len(chunks):
                        _row[_row_i] += chunk
                        _row[_row_i] = _row[_row_i].rstrip()
                        _row.append('')
                        _row_i += 1
                    else:
                        _row[_row_i] += chunk
                        _row[_row_i] += ' '
            else:
                _row[_row_i] = _row[_row_i].rstrip()
                _row.append('')
                _row_i += 1
                _row[_row_i] += word
                _row[_row_i] += ' '
        else:
            _row[_row_i] = _row[_row_i].rstrip()

        _row = map(str, _row)
        _stack.append(separator.join(_row))

    _s = '\n'.join(_stack)
    return _s
