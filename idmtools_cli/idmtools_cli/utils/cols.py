"""Defines utilities for display formatting on multiple platforms."""
from __future__ import absolute_import
from typing import Optional
from .formatters import max_width, min_width
import sys

NEWLINES = ('\n', '\r', '\r\n')


def _find_unix_console_width() -> Optional[int]:
    """
    Find the width of an Unix console where possible.

    Returns:
        Width
    """
    import termios
    import fcntl
    import struct

    # fcntl.ioctl will fail if stdout is not a tty
    if not sys.stdout.isatty():
        return None

    s = struct.pack("HHHH", 0, 0, 0, 0)
    fd_stdout = sys.stdout.fileno()
    size = fcntl.ioctl(fd_stdout, termios.TIOCGWINSZ, s)
    height, width = struct.unpack("HHHH", size)[:2]
    return width


def _find_windows_console_width() -> int:
    """
    Find the windows console width.

    Returns:
        Returns width of Windows Console
    """
    from ctypes import windll, create_string_buffer
    stdin, stdout, stderr = -10, -11, -12  # noqa: F841

    h = windll.kernel32.GetStdHandle(stderr)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom,
         maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        return sizex


def console_width(kwargs: dict) -> int:
    """
    Determine Console Width.

    Args:
        kwargs: Optional args. Currently Width is supported

    Returns:
        Console Width
    """
    if sys.platform.startswith('win'):
        cons_width = _find_windows_console_width()
    else:
        cons_width = _find_unix_console_width()

    _width = kwargs.get('width', None)
    if _width:
        cons_width = _width
    else:
        if not cons_width:
            cons_width = 80

    return cons_width


def columns(*cols, **kwargs) -> str:
    """
    Format click output in columns.

    Args:
        *cols: Colums in tuples
        **kwargs: Optional arguments

    Examples:
        > click.echo(columns((a, 20), (b, 20), (b, None)))

    Returns:
        Column formatted strings
    """
    cwidth = console_width(kwargs)

    _big_col = None
    _total_cols = 0

    cols = [list(c) for c in cols]

    for i, (string, width) in enumerate(cols):

        if width is not None:
            _total_cols += (width + 1)
            cols[i][0] = max_width(string, width).split('\n')
        else:
            _big_col = i

    if _big_col:
        cols[_big_col][1] = (cwidth - _total_cols) - len(cols)
        cols[_big_col][0] = max_width(cols[_big_col][0], cols[_big_col][1]).split('\n')

    height = len(max([c[0] for c in cols], key=len))

    for i, (strings, width) in enumerate(cols):

        for _ in range(height - len(strings)):
            cols[i][0].append('')

        for j, string in enumerate(strings):
            cols[i][0][j] = min_width(string, width)

    stack = [c[0] for c in cols]
    _out = []

    for i in range(height):
        _row = ''

        for col in stack:
            _row += col[i]
            _row += ' '

        _out.append(_row)

    return '\n'.join(_out)
