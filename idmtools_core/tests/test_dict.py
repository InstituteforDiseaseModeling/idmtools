import unittest
from idmtools.core.interfaces.ientity import IEntity
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


class TestDictionary(ITestWithPersistence):

    def test_dict(self):
        a = {"a": 1, "b": 2}
        c = {"b": 2, "a": 1}
        self.assertEqual(a, c)
        self.assertDictEqual(a, c)

    def test_dict_list(self):
        a = {"a": [1, 3], "b": 2}
        c = {"b": 2, "a": [1, 3]}
        self.assertEqual(a, c)
        self.assertDictEqual(a, c)

        a = {"a": [1, 3], "b": 2}
        c = {"b": 2, "a": [3, 1]}
        self.assertNotEqual(a, c)

        a = {"a": [1, 3], "b": 2}
        c = {"a": [3, 1], "b": 2}
        self.assertNotEqual(a, c)

    def test_entity_tags(self):
        a = IEntity()
        a.tags = {"a": 1, "b": 2}

        c = IEntity()
        c.tags = {"b": 2, "a": 1}
        self.assertEqual(a, c)

    def test_simulation_tags(self):
        from idmtools_model_emod import EMODExperiment

        e = EMODExperiment()
        sim1 = e.simulation()
        sim2 = e.simulation()

        sim1.tags = {"a": 1, "b": 2}
        sim2.tags = {"b": 2, "a": 1}
        self.assertEqual(sim1, sim2)

        sim3 = e.simulation()
        sim3.tags = {"a": 2, "b": 2}
        self.assertNotEqual(sim1, sim3)

        sim4 = e.simulation()
        sim4.tags = {"a": 1, "b": 2, "c": 3}
        self.assertNotEqual(sim1, sim4)

        sim5 = e.simulation()
        sim5.tags = {"a": 1, "c": 3, "b": 2}
        self.assertEqual(sim4, sim5)

        sim6 = e.simulation()
        sim7 = e.simulation()

        sim6.tags = {"a": 1, "b": [2]}
        sim7.tags = {"b": [2], "a": 1}
        self.assertEqual(sim6, sim7)

    def test_simulation_tags_complex(self):
        from idmtools_model_emod import EMODExperiment

        e = EMODExperiment()
        sim6 = e.simulation()
        sim7 = e.simulation()

        sim6.tags = {"a": 1, "b": {"e": 3, "f": 4}}
        sim7.tags = {"b": {"f": 4, "e": 3}, "a": 1}
        self.assertEqual(sim6, sim7)

        d1 = {
            "a": 2,
            "b": [1, 7],
            "e": {
                "C": 2,
                "F": 1
            },
            "f": {4, 5},
            "z": {"A": {3, 2}},
        }

        d2 = {
            "f": {5, 4},
            "z": {"A": {2, 3}},
            "a": 2,
            "e": {
                "F": 1,
                "C": 2
            },
            "b": [1, 7]
        }

        sim8 = e.simulation()
        sim9 = e.simulation()

        sim8.tags = d1
        sim9.tags = d2
        self.assertEqual(sim8, sim9)


if __name__ == '__main__':
    unittest.main()
