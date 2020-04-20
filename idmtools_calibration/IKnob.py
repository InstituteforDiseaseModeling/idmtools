from abc import ABCMeta
from typing import Callable, List


class IKnob(metaclass=ABCMeta):

    def __init__(self, label: str, dynamic: bool = True, initial_value: object = None,
                 constraints: List[Callable] = []):
        self._value = initial_value
        self.label = label
        self.dynamic = dynamic
        self.constraints = [*constraints, dynamic_constraint]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if all(map(lambda c: c(value, self), self.constraints)):
            self._value = value
        else:
            print("Value not changed because of constraints")


def dynamic_constraint(new_value, knob: IKnob):
    return knob.dynamic or new_value == knob.value


def min_max_constraint(new_value, knob):
    return knob.min <= new_value <= knob.max


class MinMaxGuessKnob(IKnob):
    def __init__(self, label: str, min: float = None, max: float = None, initial_value: float = None,
                 dynamic: bool = True):
        self.min = min
        self.max = max
        super().__init__(label=label, initial_value=initial_value, dynamic=dynamic, constraints=[min_max_constraint])


a = MinMaxGuessKnob(min=0, max=10, initial_value=5, label="caca")
a.value = 11
print(a.value)
