"""
Tools to format different outputs for human consumption.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from collections.abc import Iterable
from typing import Type


def on_off(test) -> str:
    """
    Print on or off depending on boolean state of test.

    Args:
        test: Boolean/object to check state

    Returns:
        On or off
    """
    return "on" if test else "off"


def pluralize(word, plural_suffix="s"):
    """
    Convert work to plural form.

    Args:
        word: Word
        plural_suffix: plural suffix. Default to s

    Returns:
        Pluralized string
    """
    if isinstance(word, Iterable):
        return plural_suffix if len(word) > 1 else ""
    return plural_suffix if word > 1 else ""


def verbose_timedelta(delta):
    """
    The verbose_timedelta provides ms accurate, human readable of a time delta.

    Args:
        delta:

    Returns:
        Time delta
    """
    if isinstance(delta, float):
        if delta < 1:
            return "0 seconds"
        hours, remainder = divmod(delta, 3600)
    else:
        if delta.seconds < 1:
            return "0 seconds"
        hours, remainder = divmod(delta.seconds, 3600)

    minutes, seconds = divmod(remainder, 60)
    hstr = "%s hour%s" % (hours, "s"[hours == 1:])
    mstr = "%s minute%s" % (minutes, "s"[minutes == 1:])
    sstr = "{:.2f} second{}".format(seconds, "s"[seconds == 1:])
    dhms = [hstr, mstr, sstr]
    for x in range(len(dhms)):
        if not dhms[x].startswith('0'):
            dhms = dhms[x:]
            break
    dhms.reverse()
    for x in range(len(dhms)):
        if not dhms[x].startswith('0'):
            dhms = dhms[x:]
            break
    dhms.reverse()
    return ', '.join(dhms)


def get_qualified_class_name(cls: Type) -> str:
    """
    Return the full class name for an object.

    Args:
        cls: Class object to get name

    Returns:
        Fully qualified class name
    """
    return f'{cls.__module__}.{cls.__name__}'


def get_qualified_class_name_from_obj(obj: object) -> str:
    """
    Return the full class name from object.

    Args:
        obj: Object

    Example:
        ```
        a = Platform('COMPS')
        class_name = get_qualified_class_name(a)
        print(class_name)
        'idmtools_platform_comps.comps_platform.COMPSPlatform'
        ```

    Returns:
        Full module path to class of object
    """
    return get_qualified_class_name(obj.__class__)
