from dataclasses import field, dataclass
from idmtools.entities import ISuite


@dataclass
class Suite(ISuite):
    description: str = field(default=None, compare=False)

    def update_tags(self, tags={}):
        self.tags.update(tags)

    def display(self):
        from idmtools.utils.display import display, suite_table_display
        display(self, suite_table_display)

    def __repr__(self):
        return f"<Suite {self.uid} - {len(self.experiments)} experiments>"
