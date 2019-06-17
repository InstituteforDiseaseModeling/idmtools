from idmtools.core import EntityContainer, INamedEntity
from idmtools.utils.decorators import pickle_ignore_fields


@pickle_ignore_fields(["experiments"])
class Suite(INamedEntity):
    def __init__(self, name: 'str'):
        super().__init__(name=name)
        self.experiments = EntityContainer()

    def post_setstate(self):
        self.experiments = EntityContainer()

    def display(self):
        from idmtools.utils.display import display, suite_table_display
        display(self, suite_table_display)

    def __repr__(self):
        return f"<Suite {self.uid} - {len(self.experiments)} experiments>"
