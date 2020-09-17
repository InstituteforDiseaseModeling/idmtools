from typing import Dict, List

from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation


def parse_relation(extra_args: Dict[str, List], item):
    from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
    if isinstance(item, Experiment):
        extra_args['related_experiments'].append(item.id)
    elif isinstance(item, Suite):
        extra_args['related_suites'].append(item.id)
    elif isinstance(item, Simulation):
        extra_args['related_simulations'].append(item.id)
    elif isinstance(item, SSMTWorkItem):
        extra_args['related_work_items'].append(item.id)