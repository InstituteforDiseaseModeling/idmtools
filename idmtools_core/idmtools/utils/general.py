"""
Tag Parsing and Normalization Utilities.

This module provides helper functions and classes for converting string-based metadata tags
into native Python types (e.g., bool, int, float) to enable accurate filtering and comparison.

It includes:
- JSON serialization/deserialization of tags
- Conversion of sets to lists for JSON compatibility
- Coercion logic via TagValue for safe and flexible comparisons

Typical use cases include tag-based filtering of simulations or experiments during analysis.

Typical Use Case:
-----------------
Used during filtering of simulations or experiments in analysis pipelines where user-defined
tags are compared with numeric thresholds or exact matches.

Example:
--------
    sim.tags={"Run_Number": lambda v: 4 <= v <= 10, "Coverage": "0.8"}
    parsed = parse_value_tags(sim.tags, wrap_with_tagvalue=True)
    assert parsed["Run_Number"] >=4 and <=10
    assert parsed["Coverage"] == 0.8

Copyright 2025, Gates Foundation. All rights reserved.
"""
import json
from typing import Dict

from idmtools.core.interfaces.ientity import IEntity


def parse_item_tags(item: IEntity):
    """
    Normalize and update an entity's tags in place.

    This function parses the given item's tags using `parse_value_tags` and updates
    the `item.tags` dictionary with the normalized values.

    Args:
        item: An entity object that contains a `.tags` dictionary.

    Returns:
        The same item, with its `.tags` dictionary updated in-place.
    """
    if item.tags is None:
        return item
    else:
        item.tags = parse_value_tags(item.tags)
        return item


def parse_value_tags(tags: Dict, wrap_with_tagvalue: bool = False) -> Dict[str, any]:
    """
    Parse and normalize a tag dictionary into native Python types.

    Converts string tag values such as:
        - "true"/"false" → bool
        - "5" → int
        - "0.8" → float
        - sets → lists

    Optionally wraps values using `TagValue` for comparison safety.

    Args:
        tags (dict): The dictionary of raw tag values to parse.
        wrap_with_tagvalue (bool): If True, wraps each value in a TagValue object
                                   for smart comparison support.

    Returns:
        dict: A dictionary with normalized or wrapped tag values.
    """
    # convert tags value as set to list first
    tags = {k: list(v) if isinstance(v, set) else v for k, v in tags.items()}
    tags_json = json.dumps(tags, cls=SetEncoder)
    # Then: parse back into a dict with properly typed values
    converted_tags = json.loads(tags_json, cls=CustomDecoder)
    # Update result.tags in-place
    for k, v in converted_tags.items():
        converted = v
        if wrap_with_tagvalue:
            converted = TagValue(v)
        tags[k] = converted
    return tags


class SetEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that converts Python sets into lists to ensure compatibility with JSON serialization.
    """

    def default(self, obj):
        """
        Override default encoding behavior.

        Args:
            obj: The object being encoded.

        Returns:
            JSON-compatible representation of the object.
        """
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


class CustomDecoder(json.JSONDecoder):
    """
    Custom JSON decoder that converts string values into appropriate Python types (bool, int, float, None).
    """

    def __init__(self, *args, **kwargs):  # noqa D415
        # Optionally override object_hook here
        super().__init__(object_hook=self.custom_object_hook, *args, **kwargs)

    @staticmethod
    def denormalize_tag_value(val):
        """
        Convert a raw string tag value into a Python-native type.

        Supported conversions:
        - "true"/"false" → bool
        - "null"/"none" → None
        - "5", "0.8" → int, float

        Args:
            val (Any): The value to convert.

        Returns:
            The normalized Python value.
        """
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

    def custom_object_hook(self, obj: Dict):
        """
        Apply normalization to each value in a decoded JSON object.

        Args:
            obj (dict): Dictionary of tag values.

        Returns:
            dict: Normalized tag dictionary.
        """
        # Modify dicts as they're loaded
        new_obj = {}
        for k, v in obj.items():
            new_obj[k] = self.denormalize_tag_value(v)
        return new_obj


class TagValue:
    """
    Wrapper for a tag value that supports smart comparisons.

    Automatically converts strings like "5" or "0.8" to int/float
    and enables comparison against numbers or other tag values.

    Useful when users perform tag-based filtering with operators
    like >, <, ==, etc., and tag values may be strings.

    Attributes:
        raw (Any): The original tag value before coercion.
    """

    def __init__(self, raw):  # noqa  D107
        self.raw = raw

    def _coerce(self, other):
        """
        Convert both self.raw and other to comparable types using the same logic as CustomDecoder.

        Args:
            other (Any): Value to compare to.

        Returns:
            Tuple[Any, Any]: Coerced values ready for comparison.
        """
        convert = CustomDecoder.denormalize_tag_value
        return convert(self.raw), convert(other)

    def __eq__(self, other): return self._coerce(other)[0] == self._coerce(other)[1]  # noqa E704

    def __lt__(self, other): return self._coerce(other)[0] < self._coerce(other)[1]  # noqa E704

    def __le__(self, other): return self._coerce(other)[0] <= self._coerce(other)[1]  # noqa E704

    def __gt__(self, other): return self._coerce(other)[0] > self._coerce(other)[1]  # noqa E704

    def __ge__(self, other): return self._coerce(other)[0] >= self._coerce(other)[1]  # noqa E704

    def __repr__(self): return repr(self.raw)  # noqa E704

    def __str__(self): return str(self.raw)  # noqa E704


class FilterSafeItem:
    """
    A lightweight wrapper around an entity (e.g., Simulation or Experiment) to enable safe tag-based filtering during multiprocessing operations (e.g., within analyzers).

    This wrapper:
    - Normalizes and wraps tag values via `TagValue` to support flexible comparisons (e.g., >, ==).
    - Supports safe pickling/unpickling by stripping unpickleable fields like `_platform`.
    - Delegates attribute access to the original wrapped item via `__getattr__` (if implemented).

    Typical usage:
        safe_item = FilterSafeItem(simulation)
        tags = safe_item.tags
        # Now tags["Run_Number"] supports TagValue comparison logic

    Attributes:
        _item (IEntity): The original entity being wrapped.
    """

    def __init__(self, item):
        """
        Initialize the filter-safe wrapper with a given entity.

        Args:
            item (IEntity): The original simulation or experiment to wrap.
        """
        self._item = item

    def __getstate__(self):
        """
        Prepare the object for pickling by removing unpickleable platform references.

        Returns:
            dict: The serializable state dictionary.
        """
        state = self.__dict__.copy()
        for key in ['_platform', '_platform_object', '_parent']:
            state.pop(key, None)
        return state

    def __getattr__(self, attr):
        """
        Delegate access to attributes not defined on the wrapper to the wrapped item.

        This makes FilterSafeItem behave like the original simulation object for all
        standard attributes (e.g., `id`, `status`, `experiment_id`, etc.).
        This function makes simulation._item.id = simulation.id the same in filter function.

        Returns:
            The attribute value from the wrapped entity.
        """
        return getattr(self._item, attr)

    def __setstate__(self, state):
        """
        Restore object state after unpickling.

        Args:
            state (dict): The state dictionary.
        """
        self.__dict__.update(state)

    @property
    def tags(self):
        """
        Get normalized tags from the wrapped item, with each value wrapped in TagValue for type-safe comparison.

        Returns:
            Dict[str, any]: Dictionary of tags.
        """
        return parse_value_tags(self._item.tags)
