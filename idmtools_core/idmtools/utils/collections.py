from typing import Tuple, List, Mapping, Union, Iterable

from more_itertools import take


def cut_iterable_to(obj: Iterable, to: int) -> Tuple[Union[List, Mapping], int]:
    """
       Cut an iterable to a certain length.

    Args:
        obj: The iterable to cut.
        to: The number of elements to return.

    Returns: 
        A list or dictionary (depending on the type of object) of elements and 
        the remaining elements in the original list or dictionary.
    """
    if isinstance(obj, dict):
        slice = {k: v for (k, v) in take(to, obj.items())}
    else:
        slice = take(to, obj)

    remaining = len(obj) - to
    remaining = 0 if remaining < 0 else remaining
    return slice, remaining


def list_rindex(lst, item):
    """
    Find the first place item occurs in a list, starting from the end of the list.
    
    Returns:
        The index of the item in the list, or -1 if item not found in the list.
    """
    i_max = len(lst)
    i_limit = -i_max
    i = -1
    while i > i_limit:
        if lst[i] == item:
            return i_max + i
        i -= 1
    return -1
