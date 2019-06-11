from idmtools.core import EntityContainer, INamedEntity


class Suite(INamedEntity):
    pickle_ignore_fields = ["experiments"]

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
