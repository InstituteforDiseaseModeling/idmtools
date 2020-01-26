from collections.abc import Iterable


def on_off(test):
    return "on" if test else "off"


def pluralize(word, plural_suffix="s"):
    if isinstance(word, Iterable):
        return plural_suffix if len(word) > 1 else ""
    return plural_suffix if word > 1 else ""


def verbose_timedelta(delta):
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


def get_qualified_class_name(cls):
    return f'{cls.__module__}.{cls.__name__}'


def get_qualified_class_name_from_obj(obj):
    return get_qualified_class_name(obj.__class__)
