from collections import defaultdict
import logging
import random

from genepi import genome as gn
from genepi import disease
from genepi.population import Population
from genepi.settings import Params
from genepi.config import Global


log = logging.getLogger(__name__)


class Simulation(object):

    def __init__(self, params=None):
        self.day = 0

        if params is None:
            params = Params()

        self.params = params.simulation

        gn.set_model(params.genome)
        disease.set_model(params.disease)

        self.reports = params.reports
        self.listeners = params.listeners
        self.events = params.events

        self.migrants = defaultdict(list)
        self.cohort_migrants = defaultdict(int)

        random.seed(self.params.random_seed)
        log.debug('Simulation: random seed = %d', self.params.random_seed)

        Global.simulation = self  # Used to callback from setting of initial infections

        self.populations = {pop_id: Population(pop_id, self, **pop_kwargs)
                            for pop_id, pop_kwargs in params.demographics.items()}

    @classmethod
    def initialize_from_file(cls, json_file):
        params = Params.from_json(json_file)
        return cls(params)

    def run(self):

        for tstep in range(self.params.sim_duration / self.params.sim_tstep):
            self.update()

        for report in self.reports:
            report.write(self.params.working_dir)

        for broadcast_event, listeners in self.listeners.items():
            for listener in listeners:
                listener.write(self.params.working_dir)

    def update(self):

        dt = self.params.sim_tstep
        self.day += dt
        log.info('\nt=%d', self.day)

        self.evaluate_events()

        for p in self.populations.values():
            p.update(dt)

        self.resolve_migration()

        for r in self.reports:
            r.update()

    def evaluate_events(self):

        while True:
            if self.events.empty():
                break

            next_day = self.events.queue[0][0]
            if next_day > self.day:
                break

            next_event_fn = self.events.get()[1]
            log.info('Executing event function.')
            next_event_fn(self)

    def resolve_migration(self):

        for dest, emigrant_and_src_list in self.migrants.items():
            for emigrant, src in emigrant_and_src_list:
                log.debug('Migrating to %s: infection %s from %s', dest, emigrant.infection, src)
                self.populations[dest].receive_immigrant(emigrant, src)

        self.migrants.clear()

        for dest, n_emigrants in self.cohort_migrants.items():
            self.populations[dest].susceptibles.n_humans += n_emigrants

        self.cohort_migrants.clear()

    def notify(self, event, *args):

        listeners = self.listeners.get(event, [])
        for l in listeners:
            l.notify(*args)


"""
Access single globally accessible Simulation object to hold parameter configuration
and to manage the interaction of state updates and reporting.
"""


def get():
    return Global.simulation

