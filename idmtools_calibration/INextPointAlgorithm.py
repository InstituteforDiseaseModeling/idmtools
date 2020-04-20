from abc import ABCMeta


class INextPointAlgorithm(metaclass=ABCMeta):

    def get_samples(self):
        pass

    def set_results(self, results):
        pass

    def plot_state(self):
        pass

    def save(self):
        pass

    def load(self, state):
        pass