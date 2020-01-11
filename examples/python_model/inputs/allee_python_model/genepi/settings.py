from collections import defaultdict
import copy
import json
import logging
from Queue import PriorityQueue

from genepi import utils
from genepi import genome as gn
from genepi.disease import DiseaseModel


log = logging.getLogger(__name__)


genome_defaults = {'SNP': {'_module_': 'barcode'}}


simulation_defaults = dict(
    working_dir='simulations',
    random_seed=8675309,
    sim_duration=365 * 10,  # days
    sim_tstep=21)


class ParamContainer(object):

    def __init__(self, params):
        for name, value in params.items():
            setattr(self, name, value)


class Params(object):

    def __init__(self, sim_settings={},
                 genome_settings=genome_defaults,
                 disease_settings={},
                 reports=[], listeners=[], events=[],
                 demographics='single_node'):

        sim_params = simulation_defaults.copy()
        utils.update_dict(sim_params, **sim_settings)
        self.simulation = ParamContainer(sim_params)

        # Defer caching global instances (set_global=False)
        # of GenomeModel + DiseaseModel until Simulation.__init__ 

        SNP_settings = copy.deepcopy(genome_settings['SNP'])
        SNP_settings.update(dict(set_global=False))

        SNP_module = SNP_settings.pop('_module_')
        self.genome = gn.GenomeModel.initialize_from(SNP_module, **SNP_settings)

        disease_params = utils.init_from_settings(disease_settings, 'model')
        self.disease = DiseaseModel.initialize_from(disease_params, set_global=False)

        self.reports = []
        self.add_reports(*reports)

        self.listeners = defaultdict(list)
        self.add_listeners(*listeners)

        self.events = PriorityQueue()
        for (day, event) in events:
            self.add_event(day, event)

        self.demographics = self.populate_from_demographics(demographics)

    @classmethod
    def from_json(cls, json_file):

        with open(json_file, 'r') as jf:
            settings = json.load(jf)

        mods = dict(simulation='sim_settings',
                    genome='genome_settings',
                    disease='disease_settings')

        return cls(**{mods.get(k, k): v for k, v in settings.items()})

    @staticmethod
    def populate_from_demographics(demog_spec, **kwargs):

        if isinstance(demog_spec, basestring):
            return utils.initialize_module('demog', 'gridded', demog_spec, **kwargs)
        elif isinstance(demog_spec, dict):
            return utils.init_from_settings(demog_spec, 'demog')
        else:
            raise Exception('Only know how to call populate_from_demographics with str and dict arguments')

    @staticmethod
    def make_object(obj_spec, subpackage, module):

        if isinstance(obj_spec, basestring):
            obj = utils.initialize_module(subpackage, module, obj_spec)
        elif isinstance(obj_spec, dict):
            obj_name, params = utils.module_from_settings(obj_spec, module)
            obj = utils.initialize_module(subpackage, module, obj_name, **params)
        else:
            obj = obj_spec()

        return obj

    def add_reports(self, *args):
        for report_spec in args:
            report_obj = self.make_object(report_spec, 'report', 'report')
            self.reports.append(report_obj)

    def add_listeners(self, *args):
        for listener_spec in args:
            l = self.make_object(listener_spec, 'report', 'listener')
            self.listeners[l.event].append(l)

    def add_event(self, day, event):
        if isinstance(event, (basestring, dict)):
            raise Exception('Addition of events by module and parameter specification not yet supported.')
        self.events.put((day, event))
