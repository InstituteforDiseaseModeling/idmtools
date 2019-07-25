def timestamp(time=None):
    """
    Args:
        time:  a time object; if None provided, use now.

    Returns: A str timestamp in UTC, format: YYYYMMDD_HHmmSS

    """
    import datetime
    if not time:
        time = datetime.datetime.utcnow()
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    return timestamp
