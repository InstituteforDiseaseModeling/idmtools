def timestamp(time=None):
    """
    Return a timestamp.

    Args:
        time: A time object; if None provided, use now.

    Returns: 
        A string timestamp in UTC, format YYYYMMDD_HHmmSS.

    """
    import datetime
    if not time:
        time = datetime.datetime.utcnow()
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    return timestamp
