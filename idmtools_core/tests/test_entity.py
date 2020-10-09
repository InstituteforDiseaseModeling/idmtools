import copy
import pickle
from functools import partial
from unittest.mock import MagicMock
import allure
import unittest
from dataclasses import dataclass, field, fields
import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.suite import Suite
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask


@dataclass
class EntityWithIgnoreField(IEntity):
    ignore: int = field(default=3, compare=False, metadata={"pickle_ignore": True})
    ignore_with_restore: int = field(default=1, compare=False, metadata={"pickle_ignore": True})
    not_ignored: int = field(default=4, metadata={"md": True})

    def post_setstate(self):
        self.ignore_with_restore = 5


def _custom_post_setstate(o):
    o.ignore = 5


# Used to test pre/post creation hooks
def bad_function_signature(arg1):
    pass


@pytest.mark.smoke
@allure.story("Entities")
@allure.suite("idmtools_core")
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
        a = TemplatedSimulations(base_task=TestTask())

        self.assertSetEqual(a.pickle_ignore_fields, set(f.name for f in fields(a) if "pickle_ignore" in f.metadata and f.metadata["pickle_ignore"]))
        a.add_builder(SimulationBuilder())

        b = pickle.loads(pickle.dumps(a))
        self.assertIsNotNone(b.builders)
        self.assertEqual(len(b.builders), 1)

        s = Suite(name="test")
        self.assertSetEqual(s.pickle_ignore_fields, set(f.name for f in fields(s) if "pickle_ignore" in f.metadata and f.metadata["pickle_ignore"]))
        b = pickle.loads(pickle.dumps(s))
        self.assertIsNone(b.experiments)

        a = EntityWithIgnoreField(ignore=10, ignore_with_restore=5)
        self.assertEqual(a.ignore, 10)
        self.assertEqual(a.ignore_with_restore, 5)
        self.assertEqual(a.not_ignored, 4)

        b = pickle.loads(pickle.dumps(a))
        self.assertNotEqual(b.ignore, a.ignore)
        self.assertEqual(b.not_ignored, a.not_ignored)
        self.assertEqual(b.ignore_with_restore, 5)

        # Test that object remains equal even with different parameters if those are not part of compare
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

        s.experiments.append(Experiment.from_task(TestTask(), name='t1'))
        s.experiments.append(Experiment.from_task(TestTask(), name='t2'))
        self.assertEqual(len(s.experiments), 2)

    def test_pre_creation_only_two_args(self):
        with self.assertRaises(ValueError) as m:

            s = Simulation(task=TestTask())
            s.add_pre_creation_hook(bad_function_signature)
        self.assertEqual(m.exception.args[0], 'Pre creation hooks should have 2 arguments. The first argument will be the item, the second the platform')

    def test_pre_creation_allow_partials(self):

        s = Simulation(task=TestTask())
        globals()['abc'] = 0

        class DummyClass:
            def hook_func(self, item, platform):
                globals()['abc'] += 1
                pass

            def add_hook(self, sim: Simulation):
                hook = partial(DummyClass.hook_func, self)
                sim.add_pre_creation_hook(hook)

        a = DummyClass()
        a.add_hook(s)
        s.pre_creation(None)
        self.assertEqual(globals()['abc'], 1)

    def test_post_creation_allow_partials(self):

        s = Simulation(task=TestTask())
        globals()['abc'] = 0

        class DummyClass:
            def hook_func(self, item, platform):
                globals()['abc'] += 1
                pass

            def add_hook(self, sim: Simulation):
                hook = partial(DummyClass.hook_func, self)
                sim.add_post_creation_hook(hook)

        a = DummyClass()
        a.add_hook(s)
        s.post_creation(None)
        self.assertEqual(globals()['abc'], 1)

    def test_post_creation_only_two_args(self):
        with self.assertRaises(ValueError) as m:

            s = Simulation()
            s.add_post_creation_hook(bad_function_signature)
        self.assertEqual(m.exception.args[0], 'Post creation hooks should have 2 arguments. The first argument will be the item, the second the platform')

    def test_simulation_pre_creation_hooks(self):
        fake_platform = MagicMock()
        s = Simulation(task=TestTask())

        def inc_count(item, platform):
            self.assertEqual(s, item)
            self.assertEqual(platform, fake_platform)
        s.add_pre_creation_hook(inc_count)
        s.pre_creation(fake_platform)

    def test_simulation_post_creation_hooks(self):
        fake_platform = MagicMock()
        s = Simulation(task=TestTask())

        def inc_count(item, platform):
            self.assertEqual(s, item)
            self.assertEqual(platform, fake_platform)
        s.add_post_creation_hook(inc_count)
        s.post_creation(fake_platform)

    def test_experiment_pre_creation_hooks(self):
        fake_platform = MagicMock()
        e = Experiment()
        e.simulations.append(Simulation(task=TestTask()))

        def inc_count(item, platform):
            self.assertEqual(e, item)
            self.assertEqual(platform, fake_platform)

        e.add_pre_creation_hook(inc_count)
        e.pre_creation(fake_platform)

    def test_experiment_post_creation_hooks(self):
        fake_platform = MagicMock()
        e = Experiment()

        def inc_count(item, platform):
            self.assertEqual(e, item)
            self.assertEqual(platform, fake_platform)

        e.add_post_creation_hook(inc_count)
        e.post_creation(fake_platform)

    def test_suite_pre_creation_hooks(self):
        fake_platform = MagicMock()
        e = Experiment()
        e.simulations.append(Simulation(task=TestTask()))
        s = Suite()
        s.experiments.append(e)

        def inc_count(item, platform):
            self.assertEqual(s, item)
            self.assertEqual(platform, fake_platform)

        s.add_pre_creation_hook(inc_count)
        s.pre_creation(fake_platform)

    def test_suite_post_creation_hooks(self):
        fake_platform = MagicMock()
        e = Experiment()
        s = Suite()
        s.experiments.append(e)

        def inc_count(item, platform):
            self.assertEqual(s, item)
            self.assertEqual(platform, fake_platform)

        s.add_post_creation_hook(inc_count)
        s.post_creation(fake_platform)



if __name__ == '__main__':
    unittest.main()
