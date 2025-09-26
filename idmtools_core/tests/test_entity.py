import copy
import pickle
import uuid
from functools import partial
from unittest.mock import MagicMock
import allure
import unittest
from dataclasses import dataclass, field, fields
import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core import NoPlatformException, ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.generic_workitem import GenericWorkItem
from idmtools.entities.simulation import Simulation
from idmtools.entities.suite import Suite
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.utils.entities import save_id_as_file_as_hook
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask

PRE_COMMIT_FAIL_MESSAGE = 'Pre creation hooks should have 2 arguments. The first argument will be the item, the second the platform'
POST_COMMIT_FAIL_MESSAGE = 'Post creation hooks should have 2 arguments. The first argument will be the item, the second the platform'


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
        self.assertIsNone(getattr(b, "_experiments", None))

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
        self.assertEqual(m.exception.args[0], PRE_COMMIT_FAIL_MESSAGE)

    def test_post_creation_no_save_id(self):
        fake_platform = MagicMock()
        with self.assertRaises(NotImplementedError) as m:
            s = Simulation(task=TestTask())
            s.add_post_creation_hook(save_id_as_file_as_hook)
            s.post_creation(fake_platform)
        self.assertEqual(m.exception.args[0], "Saving id is currently only support for Experiments and Workitems")

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
        s.pre_creation(Platform('Test'))
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
        s.post_creation(Platform('Test'))
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

    def test_task_pre_creation_hooks(self):
        fake_platform = MagicMock()
        tt = TestTask()
        s = Simulation(task=tt)
        test_hook = MagicMock()
        tt.add_pre_creation_hook(test_hook)
        s.pre_creation(fake_platform)
        self.assertEqual(test_hook.call_count, 1)

    def test_task_pre_creation_hooks_bad_signature(self):
        tt = TestTask()

        def inc_count(s):
            pass

        with self.assertRaises(ValueError) as m:
            tt.add_pre_creation_hook(inc_count)
        self.assertEqual(m.exception.args[0], PRE_COMMIT_FAIL_MESSAGE)

    def test_task_post_creation_hooks_bad_signature(self):
        tt = TestTask()

        def inc_count(s):
            pass

        with self.assertRaises(ValueError) as m:
            tt.add_post_creation_hook(inc_count)
        self.assertEqual(m.exception.args[0], POST_COMMIT_FAIL_MESSAGE)

    def test_simulation_post_creation_hooks(self):
        fake_platform = MagicMock()
        s = Simulation(task=TestTask())

        def inc_count(item, platform):
            self.assertEqual(s, item)
            self.assertEqual(platform, fake_platform)
        s.add_post_creation_hook(inc_count)
        s.post_creation(fake_platform)

    def test_experiment_pre_creation_hooks(self):
        fake_platform = Platform("TestExecute", type="TestExecute")
        base_task = TestTask()
        sim = Simulation.from_task(base_task)
        builder = SimulationBuilder()
        exp = Experiment.from_builder(builder, base_task=base_task)
        exp.simulations.append(sim)
        mock_hook = MagicMock()
        exp.add_pre_creation_hook(mock_hook)
        with fake_platform:
            exp.run(wait_until_done=True)
            self.assertEqual(mock_hook.call_count, 1)

    def test_experiment_post_creation_hooks(self):
        fake_platform = Platform("TestExecute", type="TestExecute")
        base_task = TestTask()
        sim = Simulation.from_task(base_task)
        builder = SimulationBuilder()
        exp = Experiment.from_builder(builder, base_task=base_task)
        exp.simulations.append(sim)
        mock_hook = MagicMock()
        exp.add_post_creation_hook(mock_hook)
        with fake_platform:
            exp.run(wait_until_done=True)
            self.assertEqual(mock_hook.call_count, 1)

    def test_workitem_pre_create(self):
        fake_platform = MagicMock()
        wi = GenericWorkItem(task=TestTask(), name='test_wi_precreate')
        test_hook = MagicMock()
        wi.add_pre_creation_hook(test_hook)
        wi.pre_creation(fake_platform)
        self.assertEqual(test_hook.call_count, 1)

    def test_workitem_post_create(self):
        fake_platform = MagicMock()
        wi = GenericWorkItem(task=TestTask(), name='test_wi_postcreate')
        test_hook = MagicMock()
        wi.add_pre_creation_hook(test_hook)
        wi.pre_creation(fake_platform)
        self.assertEqual(test_hook.call_count, 1)

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

class TestExperimentParent:
    id = "mock-suite-id"

    @pytest.fixture
    def experiment(self):
        """Create a basic experiment instance for testing."""
        return Experiment(name="test_experiment")

    def test_parent_getter_no_parent(self, experiment):
        """Test parent getter when no parent is set."""
        assert experiment.parent is None

    def test_parent_getter_with_parent_id_no_platform(self, experiment):
        """Test parent getter when parent_id is set but no platform exists."""
        experiment.parent_id = "test_parent_id"
        with pytest.raises(NoPlatformException):
            _ = experiment.parent

    def test_parent_getter_with_parent_id_and_platform(self, experiment):
        """Test parent getter when both parent_id and platform are set."""
        # Mock platform and its get_item method
        mock_platform = MagicMock()
        mock_suite = MagicMock()
        mock_platform.get_item.return_value = mock_suite

        experiment.parent_id = "test_parent_id"
        experiment.platform = mock_platform
        experiment.platform.get_item.return_value = mock_suite
        # Get parent
        experiment._parent = mock_suite
        parent = experiment.parent

        assert parent == mock_suite

    def test_parent_setter_with_valid_parent(self, experiment):
        """Test setting a valid parent."""
        mock_parent = MagicMock()
        experiment.parent = mock_parent

        # Verify add_experiment was called on parent
        mock_parent.add_experiment.assert_called_once_with(experiment)

    def test_parent_setter_with_none(self, experiment):
        """Test setting parent to None."""
        experiment.parent = None
        assert experiment._parent is None
        assert experiment.parent_id is None
        assert experiment.suite_id is None

    def test_suite_getter(self, experiment):
        experiment = Experiment(name="test_experiment")
        mock_suite = MagicMock()
        def fake_add_experiment(exp):
            exp._parent = mock_suite
            exp.parent_id = exp.suite_id = "suite-123"
        mock_suite.add_experiment.side_effect = fake_add_experiment
        experiment.parent = mock_suite  # triggers parent setter
        assert experiment.suite is mock_suite  # suite getter delegates to parent
        mock_suite.add_experiment.assert_called_once_with(experiment)

    def test_suite_setter(self, experiment):
        """Test that suite setter sets parent."""
        mock_suite = MagicMock()

        def fake_add_experiment(exp):
            exp._parent = mock_suite
            exp.parent_id = exp.suite_id = "suite-123"

        mock_suite.add_experiment.side_effect = fake_add_experiment
        experiment.suite = mock_suite
        assert experiment.parent is mock_suite
        mock_suite.add_experiment.assert_called_once_with(experiment)


if __name__ == '__main__':
    unittest.main()
