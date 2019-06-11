from idmtools.core import EntityContainer, INamedEntity


class Suite(INamedEntity):
    pickle_ignore_fields = ["experiments"]

    def __init__(self, name: 'str'):
        super().__init__(name=name)
        self.experiments = EntityContainer()

    def post_setstate(self):
        self.experiments = EntityContainer()
