import unittest

from idmtools.core.item_id import ItemId


class TestItemId(unittest.TestCase):

    def test_normalization_of_tuple_values_to_str(self):
        id1 = ItemId(group_tuples=[(1, 2)])
        id2 = ItemId(group_tuples=[('1', '2')])
        self.assertEqual(id1, id2)

    def test_attrs_set_properly_on_instantiation(self):
        tuples = [('sim', 1), ('exp', 2), ('suite', 3)]
        id = ItemId(group_tuples=tuples)
        for tup in tuples:
            name = str(tup[0])
            value = str(tup[1])
            self.assertTrue(hasattr(id, name))
            self.assertEqual(getattr(id, name), value)

    def test_hierarchy_methods(self):
        id = ItemId(group_tuples=[('alpha', 1), ('beta', 2), ('gamma', 3)])
        self.assertEqual(id.group_hierarchy, ['alpha', 'beta', 'gamma'])
        self.assertEqual(id.value_hierarchy, ['1', '2', '3'])

        id = ItemId(group_tuples=[('chocolate', 42)])
        self.assertEqual(id.group_hierarchy, ['chocolate'])
        self.assertEqual(id.value_hierarchy, ['42'])

    def test_equal(self):
        id1 = ItemId(group_tuples=[('thingy', 100)])
        id2 = ItemId(group_tuples=[('thingy', 100)])
        self.assertEqual(id1, id2)

        id1 = ItemId(group_tuples=[('sim', 1), ('exp', 2), ('suite', 3)])
        id2 = ItemId(group_tuples=[('sim', 1), ('exp', 2), ('suite', 3)])
        self.assertEqual(id1, id2)

        id_wrong_length = ItemId(group_tuples=[('sim', 1), ('exp', 2)])
        self.assertNotEqual(id1, id_wrong_length)

        id_different_value = ItemId(group_tuples=[('sim', 1), ('exp', 2), ('suite', 99)])
        self.assertNotEqual(id1, id_different_value)

        id_different_name = ItemId(group_tuples=[('sim', 1), ('CaptainPicard', 2), ('suite', 3)])
        self.assertNotEqual(id1, id_different_name)
