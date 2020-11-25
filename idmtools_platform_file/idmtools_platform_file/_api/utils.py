import os
from contextlib import suppress
from pathlib import PurePath
from typing import Union
from idmtools.entities.experiment import Experiment
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation


def find_next_name(start: int, output_directory: PurePath, item: Union[Experiment, Simulation, IWorkflowItem], format_name_str: str = None) -> str:
    if format_name_str is None:
        format_name_str = '{item.name}{i}'
    filename = output_directory.joinpath(format_name_str.format(**dict(item=item, i=start)))
    while os.path.exists(filename):
        filename = output_directory.joinpath(format_name_str.format(**dict(item=item, i=start)) if item.name else f"{start}")
        start += 1
    return str(filename)


def create_next_dir(output_directory: PurePath, item: Union[Experiment, Simulation, IWorkflowItem], start: int = None, format_name_str: str = None) -> str:
    if start is None:
        start = 0
    while True:
        fn = find_next_name(start, output_directory, item, format_name_str)
        with suppress(FileExistsError):
            os.makedirs(fn)
            return fn
