from dataclasses import field, dataclass
from idmtools.core import EntityContainer
from idmtools.core.interfaces.INamedEntity import INamedEntity


def default_experiments():
    return EntityContainer()


@dataclass
class Suite(INamedEntity):
    experiments: 'EntityContainer' = field(default_factory=default_experiments, metadata={"pickle_ignore": True})

    def post_setstate(self):
        self.experiments = EntityContainer()

    def display(self):
        from idmtools.utils.display import display, suite_table_display
        display(self, suite_table_display)

    def __repr__(self):
        return f"<Suite {self.uid} - {len(self.experiments)} experiments>"
