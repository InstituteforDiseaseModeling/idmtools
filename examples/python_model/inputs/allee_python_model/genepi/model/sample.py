import random  # use np.random everywhere?

from genepi.utils import callable_function


def init(function_name, **params):

    try:
        random_function = getattr(random, function_name)
        return sample_function(random_function, **params)

    except AttributeError:
        raise


class sample_function(callable_function):

    def __init__(self, random_function, shift=None,
                 min_value=None, max_value=None, **random_params):

        self.random_function = random_function
        self.shift = shift
        self.min_value = min_value
        self.max_value = max_value
        self.random_params = random_params

    def __call__(self):

        value = self.random_function(**self.random_params)

        if self.shift is not None:
            value += self.shift

        if self.min_value is not None:
            value = max(self.min_value, value)

        if self.max_value is not None:
            value = min(self.max_value, value)

        return value
