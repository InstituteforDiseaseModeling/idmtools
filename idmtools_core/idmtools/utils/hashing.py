"""
Fast hash of Python objects.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Union, BinaryIO

import decimal
import hashlib
import io
import pickle
import types
from dataclasses import fields, _MISSING_TYPE
from logging import getLogger, Logger

logger = getLogger(__name__)
Pickler = pickle._Pickler


class _ConsistentSet(object):
    """
    Class used to ensure the hash of sets is preserved whatever the order of its items.
    """

    def __init__(self, set_sequence):
        """
        Force the order of elements in a set to ensure consistent hashing.
        """
        try:
            # Trying first to order the set using sorted
            self._sequence = sorted(set_sequence)
        except (TypeError, decimal.InvalidOperation):
            # If elements are unorderable, sort them using their hash.
            self._sequence = sorted((hash(e) for e in set_sequence))


class _MyHash(object):
    """
    A class used to hash objects that won't normally pickle.
    """

    def __init__(self, *args):
        self.args = args


class Hasher(Pickler):
    """
    A subclass of pickler to do hashing, rather than pickling.
    """

    def __init__(self, hash_name='md5'):
        """
        Initialize our hasher.

        Args:
            hash_name: Hash type to use. Defaults to md5
        """
        self.stream = io.BytesIO()
        Pickler.__init__(self, self.stream)
        # Initialise the hash obj
        self._hash = hashlib.new(hash_name)

    def hash(self, obj, return_digest=True):
        """
        Hash an object.

        Args:
            obj: Object to hash
            return_digest: Should the digest be returned?

        Returns:
            None if return_digest is False, otherwise the hash digest is returned
        """
        try:
            self.dump(obj)
        except pickle.PicklingError as e:
            e.args += ('PicklingError while hashing %r: %r' % (obj, e),)
            raise
        dumps = self.stream.getvalue()
        self._hash.update(dumps)
        if return_digest:
            return self._hash.hexdigest()

    def save(self, obj):
        """
        Save an object to hash.

        Args:
            obj: Obj to save.

        Returns:
            None
        """
        from idmtools.utils.collections import ExperimentParentIterator
        import abc
        if isinstance(obj, abc.ABCMeta):
            pass
        elif isinstance(obj, ExperimentParentIterator):
            pass
        elif isinstance(obj, Logger):
            pass
        else:
            if isinstance(obj, (types.MethodType, type({}.pop))):
                # the Pickler cannot pickle instance methods; here we decompose
                # them into components that make them uniquely identifiable
                if hasattr(obj, '__func__'):
                    func_name = obj.__func__.__name__
                else:
                    func_name = obj.__name__
                inst = obj.__self__
                if isinstance(inst, pickle):
                    obj = _MyHash(func_name, inst.__name__)
                elif inst is None:
                    # type(None) or type(module) do not pickle
                    obj = _MyHash(func_name, inst)
                else:
                    cls = obj.__self__.__class__
                    obj = _MyHash(func_name, inst, cls)
            Pickler.save(self, obj)

    def memoize(self, obj):
        """
        Disable memoization for strings so hashing happens on value and not reference.
        """
        if isinstance(obj, (str, bytes)):
            return
        Pickler.memoize(self, obj)

    def _batch_setitems(self, items):
        """
        Force the order of keys in dictionary to ensure consistent hashing.
        """
        try:
            # First try quick way of sorting keys if possible
            Pickler._batch_setitems(self, iter(sorted(items)))
        except TypeError:
            # If keys are unorderable, sort them using their hash
            Pickler._batch_setitems(self, iter(sorted((hash(k), v) for k, v in items)))

    def save_set(self, set_items):
        """
        Save set hashing.

        Args:
            set_items: Set items

        Returns:
            None
        """
        # forces order of items in Set to ensure consistent hash
        Pickler.save(self, _ConsistentSet(set_items))


def hash_obj(obj, hash_name='md5'):
    """
    Quick calculation of a hash to identify uniquely Python objects.

    Args:
        obj: Object to hash
        hash_name: The hashing algorithm to use. 'md5' is faster; 'sha1' is considered safer.
    """
    hasher = Hasher(hash_name=hash_name)
    return hasher.hash(obj)


def ignore_fields_in_dataclass_on_pickle(item):
    """
    Ignore certain fields for pickling on dataclasses.

    Args:
        item: Item to pickle

    Returns:
        State of item to pickle
    """
    state = item.__dict__.copy()
    attrs = set(vars(item).keys())

    # Retrieve fields default values
    fds = fields(item)
    field_default = {f.name: f.default for f in fds}

    # Update default with parent's pre-populated values
    if hasattr(item, 'pre_getstate'):
        pre_state = item.pre_getstate()
        pre_state = pre_state or {}
        field_default.update(pre_state)

    # Don't pickle ignore_pickle fields: set values to default
    for field_name in attrs.intersection(item.pickle_ignore_fields):
        if field_name in state:
            if isinstance(field_default[field_name], _MISSING_TYPE):
                state[field_name] = None
            else:
                state[field_name] = field_default[field_name]

    return state


def calculate_md5(filename: str, chunk_size: int = 8192) -> str:
    """
    Calculate MD5.

    Args:
        filename: Filename to caclulate md5 for
        chunk_size: Chunk size

    Returns:
        md5 as string
    """
    with open(filename, "rb") as f:
        return calculate_md5_stream(f, chunk_size)


def calculate_md5_stream(stream: Union[io.BytesIO, BinaryIO], chunk_size: int = 8192, hash_type: str = 'md5', file_hash=None):
    """
    Calculate md5 on stream.

    Args:
        chunk_size:
        stream:
        hash_type: Hash function
        file_hash: File hash

    Returns:
        md5 of stream
    """
    if file_hash is None:
        if not hasattr(hashlib, hash_type):
            raise ValueError(f"Could not find hash function {hash_type}")
        else:
            file_hash = getattr(hashlib, hash_type)()

    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        file_hash.update(chunk)
    return file_hash.hexdigest()
