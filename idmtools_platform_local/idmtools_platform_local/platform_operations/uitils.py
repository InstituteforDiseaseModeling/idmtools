status_translate = dict(
    created='CREATED',
    in_progress='RUNNING',
    canceled='FAILED',
    failed='FAILED',
    done='SUCCEEDED'
)


def local_status_to_common(status):
    from idmtools.core import EntityStatus
    return EntityStatus[status_translate[status]]
