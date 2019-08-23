from collections import OrderedDict


class ItemId:

    GROUP_DELIMITER = ':'

    # expects an ordered set of tuples, e.g. [('simulation_id', 'ghi'), ('experiment_id', 'def'), ('suite_id', 'abc')]
    def __init__(self, group_tuples):
        # normalize all key/values to str for consistency, e.g. 1 vs '1'
        group_tuples = [(str(tup[0]), str(tup[1])) for tup in group_tuples]
        self.groups = OrderedDict(group_tuples)
        for group_name, group_value in self.groups.items():
            setattr(self, group_name, group_value)

    @property
    def group_hierarchy(self):
        return list(self.groups.keys())

    @property
    def value_hierarchy(self):
        return list(self.groups.values())

    def __repr__(self):
        return self.GROUP_DELIMITER.join([str(v) for v in self.groups.values()])

    def __eq__(self, other):
        return self.group_hierarchy == other.group_hierarchy and self.value_hierarchy == other.value_hierarchy
