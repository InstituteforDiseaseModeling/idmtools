import copy
import pickle
import unittest

from idmtools.core import IEntity
from idmtools.entities.Suite import Suite
from tests.utils.ITestWithPersistence import ITestWithPersistence
from tests.utils.TestExperiment import TestExperiment
from tests.utils.TestSimulation import TestSimulation


class EntityWithIgnoreField(IEntity):
    pickle_ignore_fields = ["ignore"]

    def __init__(self):
        super().__init__()
        self.ignore = 3


def _custom_post_setstate(o):
    o.ignore = 5


class TestEntity(ITestWithPersistence):

    def test_hashing(self):
        a = IEntity()
        a.tats = {"a": 1}

        b = IEntity()
        b.tags = {"a": 1}

        # Those 2 entities are different
        self.assertNotEqual(a, b)

        # a and b should be identical after deepcopy
        b = copy.deepcopy(a)
        self.assertEqual(a, b)

        # a and b should be identical after pickling
        b = pickle.loads(pickle.dumps(a))
        self.assertEqual(a, b)

    def test_state_management(self):
        a = EntityWithIgnoreField()
        self.assertEqual(a.ignore, 3)

        # The ignore field, should be ignored when unpickling object therefore present but set to None
        b = pickle.loads(pickle.dumps(a))
        self.assertTrue(hasattr(b, "ignore"))
        self.assertIsNone(b.ignore)

        # If we have a post_restore_state, unpickling should restore the attribute to the value defined in the function
        EntityWithIgnoreField.post_setstate = _custom_post_setstate
        b = pickle.loads(pickle.dumps(a))
        self.assertEqual(b.ignore, 5)

    def test_pickle_ignore(self):
        a = TestExperiment(name="test")
        self.assertEqual(a.pickle_ignore_fields, ["simulations", "builder"])
        b = pickle.loads(pickle.dumps(a))
        self.assertEqual(b.simulations, [])
        self.assertIsNone(b.builder)

        s = Suite(name="test")
        self.assertEqual(s.pickle_ignore_fields, ["experiments"])
        b = pickle.loads(pickle.dumps(s))
        self.assertEqual(b.experiments, [])

    def test_experiment(self):
        a = TestExperiment(name="test")
        self.assertEqual(a.name, "test")

        a.simulations.append(TestSimulation())
        a.simulations.append(TestSimulation())
        self.assertEqual(len(a.simulations), 2)

    def test_suite(self):
        s = Suite(name="test")
        self.assertEqual(s.name, "test")

        s.experiments.append(TestExperiment("t1"))
        s.experiments.append(TestExperiment("t2"))
        self.assertEqual(len(s.experiments), 2)



if __name__ == '__main__':
    unittest.main()
