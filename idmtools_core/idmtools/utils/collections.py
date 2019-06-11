from collections import Iterable
from typing import Tuple, List, Mapping, Union

from more_itertools import take


def cut_iterable_to(obj: Iterable, to: int) -> Tuple[Union[List, Mapping], int]:
    """
    Cut an iterable to a certain length
    Args:
        obj: The iterable to cut
        to: How many elements to return

    Returns: A list/dict (depending on the type of object) of elements and the remaining elements in the original list/dict
    """
    if isinstance(obj, dict):
        slice = {k: v for (k, v) in take(to, obj.items())}
    else:
        slice = take(to, obj)

    remaining = len(obj) - to
    remaining = 0 if remaining < 0 else remaining
    return slice, remaining
