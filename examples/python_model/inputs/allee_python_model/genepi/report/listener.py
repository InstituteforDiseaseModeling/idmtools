from collections import defaultdict
import csv
import json
import logging
import os

import numpy as np
import pandas as pd

from genepi import genome as gn
from genepi.strain import Strain
from genepi.infection import Infection
from genepi.transmission import Transmission
from genepi import simulation

log = logging.getLogger(__name__)


class Listener(object):

    def notify(self, *args):
        pass

    def write(self, working_directory):
        pass


class TransmissionGeneticsReport(Listener):
    """
    A helper class to record detailed report on genetics
    of infection transmission events to output file
    """

    def __init__(self, report_filename='TransmissionGeneticsReport.csv'):
        self.report_filename = report_filename
        self.event = 'infection.transmit'
        self.data = []

    def notify(self, *args):
        try:
            transmission = args[0]
            assert isinstance(transmission, list)
            for t in transmission:
                assert isinstance(t, Transmission)
                self.data.append(t.to_tuple())
        except:
            raise Exception('Expected list of Transmission objects as first argument.')

    def write(self, working_directory):

        filename = os.path.join(working_directory, self.report_filename)

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        with open(filename, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['day', 'pid', 'iid', 'iidParent', 'gidParent1', 'gidParent2', 'gid'])
            for r in self.data:
                writer.writerow(r)


class GenomeReport(Listener):
    """
    A helper class to record map of Strain.id to Strain.genome
    """

    def __init__(self, report_filename='GenomeReport', report_interval=None):
        self.report_filename = report_filename
        self.event = 'strain.init'
        self.data = []
        self.report_interval = report_interval

    def notify(self, *args):

        try:
            g = args[0]
            assert isinstance(g, Strain)
        except:
            raise Exception('Expected Strain object as first argument.')

        if self.report_interval and simulation.get().day not in range(*self.report_interval):
            return

        self.data.append(g.barcode())

    # TODO: performance may be improved by pre-allocating array

    def write(self, working_directory):

        filename = os.path.join(working_directory, self.report_filename)

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        A = np.array(self.data)
        np.savez(filename, genomes=A, header=gn.model().get_SNP_names())

        df = pd.DataFrame(A, columns=gn.model().get_SNP_names())
        df.to_csv(filename + '.csv')


class ExpiredStrainReport(Listener):
    """
    A helper class to record distribution of Strain duration by complexity of infection.
    """

    def __init__(self, report_filename='ExpiredStrain.json'):
        self.report_filename = report_filename
        self.event = 'strain.expired'
        self.duration_by_COI = defaultdict(list)

    def notify(self, *args):

        try:
            strain = args[0]
            assert isinstance(strain, Strain)
        except:
            raise Exception('Expected Strain object as first argument.')

        try:
            infection = args[1]
            assert isinstance(infection, Infection)
        except:
            raise Exception('Expected Infection object as second argument.')

        self.duration_by_COI[infection.n_strains()].append(strain.time_since_infection)

    def write(self, working_directory):

        filename = os.path.join(working_directory, self.report_filename)

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        with open(filename, 'w') as fp:
            json.dump(self.duration_by_COI, fp)