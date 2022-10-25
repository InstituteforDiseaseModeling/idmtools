"""
Defines our IAnalyzer interface used as base of all other analyzers.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""


def get_caller():
    """
    Trace the stack and find the caller.

    Returns:
        The direct caller.
    """
    import inspect

    try:
        s = inspect.stack()
    except (IndexError, RuntimeError):
        # in some high thread environments and under heavy load, we can get environment changes before retrieving
        # stack in those case assume we are good
        # We can also encounter IndexError in dynamic environments like Snakemake, jinja, etc
        return "__newobj__"
    return s[2][3]
