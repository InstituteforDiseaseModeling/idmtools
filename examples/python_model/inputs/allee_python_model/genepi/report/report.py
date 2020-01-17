from collections import defaultdict
import json
import logging
import os

from genepi import simulation


log = logging.getLogger(__name__)


class Report(object):

    def update(self):
        pass

    def write(self, working_directory):
        pass


class PopulationInfectionReport(Report):
    """
    A helper class to record high-level metrics of simulation state
    of infections in populations to output file
    """

    def __init__(self, report_filename='PopulationInfectionReport.json'):
        self.report_filename = report_filename
        self.data = {'tsteps': [],
                     'n_humans': defaultdict(list),
                     'f_infected': defaultdict(list),
                     'f_polygenomic': defaultdict(list),
                     'mean_COI': defaultdict(list)}

    def update(self):

        day = simulation.get().day
        log.debug('Report updated at t=%d', day)
        self.data['tsteps'].append(day)

        for pid, p in simulation.get().populations.items():
            n_humans = p.n_humans()
            self.data['n_humans'][pid].append(n_humans)

            n_infecteds = float(p.n_infecteds())
            f_infected = n_infecteds / n_humans if n_humans else 0
            self.data['f_infected'][pid].append(f_infected)

            f_poly = p.n_polygenomic() / n_infecteds if n_infecteds else 0
            self.data['f_polygenomic'][pid].append(f_poly)

            self.data['mean_COI'][pid].append(p.mean_COI())

    def write(self, working_directory):

        self.data['populations'] = simulation.get().populations.keys()

        filename = os.path.join(working_directory, self.report_filename)

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        with open(filename, 'w') as outfile:
            json.dump(self.data, outfile, sort_keys=True)
