from abc import ABCMeta, abstractmethod
from typing import Any

from marshmallow import Schema, ValidationError


class IWorkflowStep(metaclass=ABCMeta):

    def __init__(self, name: str, inputs_schema: Schema = None, output_schema: Schema = None):
        self.name = name
        self.inputs_schema = inputs_schema
        self.output_schema = output_schema
        self.inputs = None

    @abstractmethod
    def execute(self):
        pass

    def set_inputs(self, inputs: Any):
        if self.inputs_schema:
            try:
                self.inputs = self.inputs_schema.load(inputs)
            except ValidationError as err:
                print(f"Error parsing data for the step {self.name}:\n{err.messages}")
                exit()
        else:
            self.inputs = inputs
