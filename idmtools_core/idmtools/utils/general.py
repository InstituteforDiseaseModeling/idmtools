import json


def parse_item_tags(item):
    """
    parse item's tags
    Args:
        item:

    Returns:

    """
    if item.tags is None:
        return item
    else:
        converted_tags = parse_value_tags(item.tags)
        for k, v in converted_tags.items():
            item.tags[k] = v
        return item


def parse_value_tags(tags):
    tags_json = json.dumps(tags)
    # Then: parse back into a dict with properly typed values
    converted_tags = json.loads(tags_json, cls=CustomDecoder)
    # Update result.tags in-place
    for k, v in converted_tags.items():
        tags[k] = v
    return tags


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        # Optionally override object_hook here
        super().__init__(object_hook=self.custom_object_hook, *args, **kwargs)

    @staticmethod
    def denormalize_tag_value(val):
        if not isinstance(val, str):
            return val  # Already a native type

        val_lower = val.strip().lower()
        if val_lower == "true":
            return True
        elif val_lower == "false":
            return False
        elif val_lower in ("null", "none"):
            return None

        # Try integer/float
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            pass

        # Return as-is if it's not a simple number/bool/null
        return val

    def custom_object_hook(self, obj):
        # Modify dicts as they're loaded
        new_obj = {}
        for k, v in obj.items():
            new_obj[k] = self.denormalize_tag_value(v)
        return new_obj
