"""
Fast  hash of Python objects
"""

import decimal
import hashlib
import io
import pickle
import types

Pickler = pickle._Pickler


class _ConsistentSet(object):
    """
    Class used to ensure the hash of Sets is preserved whatever the order of its items.
    """

    def __init__(self, set_sequence):
        """
        Forces order of elements in set to ensure consistent hash.
        """
        try:
            # Trying first to order the set using sorted
            self._sequence = sorted(set_sequence)
        except (TypeError, decimal.InvalidOperation):
            # If elements are unorderable, sort them using their hash.
            self._sequence = sorted((hash(e) for e in set_sequence))


class _MyHash(object):
    """ Class used to hash objects that won't normally pickle """

    def __init__(self, *args):
        self.args = args


class Hasher(Pickler):
    """ A subclass of pickler, to do hashing, rather than pickling. """

    def __init__(self, hash_name='md5'):
        self.stream = io.BytesIO()
        Pickler.__init__(self, self.stream)
        # Initialise the hash obj
        self._hash = hashlib.new(hash_name)

    def hash(self, obj, return_digest=True):
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
        if isinstance(obj, (types.MethodType, type({}.pop))):
            # the Pickler cannot pickle instance methods; here we decompose
            # them into components that make them uniquely identifiable
            if hasattr(obj, '__func__'):
                func_name = obj.__func__.__name__
            else:
                func_name = obj.__name__
            inst = obj.__self__
            if type(inst) == type(pickle):
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
        We want hashing to happen on value and not reference so we disable memoization for strings
        """
        if isinstance(obj, (str, bytes)):
            return
        Pickler.memoize(self, obj)

    def _batch_setitems(self, items):
        """
        Force the order of keys in dict to ensure consistent hashing
        """
        try:
            # First try quick way of sorting keys if possible
            Pickler._batch_setitems(self, iter(sorted(items)))
        except TypeError:
            # If keys are unorderable, sort them using their hash
            Pickler._batch_setitems(self, iter(sorted((hash(k), v) for k, v in items)))

    def save_set(self, set_items):
        # forces order of items in Set to ensure consistent hash
        Pickler.save(self, _ConsistentSet(set_items))


def hash_obj(obj, hash_name='md5'):
    """ Quick calculation of a hash to identify uniquely Python objects

        Args:
        hash_name: 'md5' or 'sha1'
            Hashing algorithm used. sha1 is supposedly safer, but md5 is
            faster.
    """
    hasher = Hasher(hash_name=hash_name)
    return hasher.hash(obj)
