from python_task import PythonTask


# TODO: fix this up re: changes to iterative mgr python task
class IterativePythonTask(PythonTask):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.iterative_attributes = dict() if iterative_attributes is None else iterative_attributes
        # # force name to be an iterative attribute of a defined pattern, overriding normal Task behavior
        #
        # # now add all attributes that depend on self.number
        # # DO NOT add depends_on in here. Those are handled automatically by an iteration manager task
        # for attr_name, attr_value in self.iterative_attributes.items():
        #     setattr(self, attr_name, attr_value)
        print(f'Created {type(self)} with method kwargs: {self.method_kwargs}')