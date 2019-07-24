import copy
import random

from idmtools.workflows.calibration import Sample


class DummyNPA:

    def generate_samples(self, parameters, how_many):
        samples = []
        for i in range(how_many):
            sample = Sample(index=i)
            for parameter in parameters:
                p = copy.deepcopy(parameter)
                p.value = round(random.uniform(p.min, p.max), 3)
                sample.parameters.append(p)

            samples.append(sample)

        return samples
