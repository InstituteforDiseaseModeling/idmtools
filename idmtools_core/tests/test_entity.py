import copy
import pickle
import unittest

from idmtools.core import IEntity
from idmtools.entities.Suite import Suite
from idmtools.utils.decorators import pickle_ignore_fields
from tests.utils.ITestWithPersistence import ITestWithPersistence
from tests.utils.TestExperiment import TestExperiment


@pickle_ignore_fields(["ignore", "ignore_with_restore"])
class EntityWithIgnoreField(IEntity):
    def __init__(self):
        super().__init__()
        self.ignore = 3
        self.ignore_with_restore = 1
        self.not_ignored = 4

    def post_setstate(self):
        self.ignore_with_restore = 5


def _custom_post_setstate(o):
    o.ignore = 5


class TestEntity(ITestWithPersistence):

    def test_hashing(self):
        a = IEntity()
        a.tags = {"a": 1}

        c = IEntity()
        c.tags = {"a": 2}
        self.assertNotEqual(a, c)

        b = IEntity()
        b.tags = {"a": 1}

        # Those 2 entities are the same because same elements
        self.assertEqual(a, b)

        # a and c should be identical after deepcopy
        c = copy.deepcopy(a)
        self.assertEqual(a, c)

        # a and b should be identical after pickling
        b = pickle.loads(pickle.dumps(a))
        self.assertEqual(a, b)

    def test_pickle_ignore(self):
        a = TestExperiment(name="test")
        self.assertSetEqual(a.pickle_ignore_fields, {'assets', 'builder', 'simulations'})
        b = pickle.loads(pickle.dumps(a))
        self.assertEqual(b.simulations, [])
        self.assertIsNone(b.builder)

        s = Suite(name="test")
        self.assertSetEqual(s.pickle_ignore_fields, {"experiments"})
        b = pickle.loads(pickle.dumps(s))
        self.assertEqual(b.experiments, [])

        a = EntityWithIgnoreField()
        self.assertEqual(a.ignore, 3)
        self.assertEqual(a.ignore_with_restore, 1)
        self.assertEqual(a.not_ignored, 4)
        b = pickle.loads(pickle.dumps(a))
        self.assertNotEqual(b.ignore, a.ignore)
        self.assertIsNone(b.ignore)
        self.assertEqual(b.not_ignored, a.not_ignored)
        self.assertEqual(b.ignore_with_restore, 5)

        # Test that object remains equal even with different parameters if those are ignored
        a = EntityWithIgnoreField()
        b = EntityWithIgnoreField()
        a.ignore = "A"
        b.ignore_with_restore = 10
        self.assertEqual(a, b)
        a.not_ignored = 100
        self.assertNotEqual(a, b)

        # Test that we do not change the object while doing equality tests
        self.assertEqual(b.ignore_with_restore, 10)

    def test_suite(self):
        s = Suite(name="test")
        self.assertEqual(s.name, "test")

        s.experiments.append(TestExperiment("t1"))
        s.experiments.append(TestExperiment("t2"))
        self.assertEqual(len(s.experiments), 2)


if __name__ == '__main__':
    unittest.main()
