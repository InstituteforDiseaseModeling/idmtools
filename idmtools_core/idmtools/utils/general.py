from uuid import UUID


def convert_to_uuid(item_id):
    return item_id if isinstance(item_id, UUID) else UUID(item_id)
