import os
from pprint import pprint

from finalize_task import FinalizeTask
from system_task import SystemTask
from python_task import PythonTask
from workflow import Workflow
from iterative_python_task import IterativePythonTask
from iteration_manager_python_task import IterationManagerPythonTask


class OptimTool:
    def __init__(self):
        pass

    def compute_next_points(self, input_points):
        output_points = input_points.copy()
        output_points.loc[:, 'value'] = output_points['value'].apply(lambda x: x + 1)
        return output_points


class CramerRao:
    def __init__(self):
        pass

    def resample(self, input_points):
        output_points = input_points.copy()
        output_points.loc[:, 'value'] = output_points['value'].apply(lambda x: x + 0.01)
        return output_points


NEXT_POINT_ALGORITHM = OptimTool
RESAMPLE_ALGORITHM = CramerRao
REFERENCE_DATA_SOURCE = os.path.join('Data', 'unparsed_reference_data.json')
FINAL_POINTS_FILENAME = 'calibrated_and_resampled_points.csv'


def add_file(input_filename, output_filename):
    import pandas as pd
    df = pd.read_csv(input_filename, index_col=0)
    df.loc[:, 'a'] = df['a'] + df['b']
    df.to_csv(output_filename)
    return None, None


def process_reference_data(reference_data_source, output_filename):
    from shutil import copyfile
    copyfile(reference_data_source, output_filename)
    return None, None


def copy_file(file, to):
    import shutil
    shutil.copy(file, to)
    return None, None


def run_calibration_iteration(next_point_algorithm, input_points_csv_filename, output_points_csv_filename,
                              reference_data_filename):
    import pandas as pd

    algo = next_point_algorithm()

    input_points = pd.read_csv(input_points_csv_filename, index_col=0)
    new_points = algo.compute_next_points(input_points=input_points)
    new_points.to_csv(output_points_csv_filename)

    return None, None


def resample(algorithm, final_calibration_args, output_points_csv_filename):
    import pandas as pd
    algo = algorithm()

    final_args = final_calibration_args()
    input_points_csv_filename = final_args['method_kwargs']['output_points_csv_filename']
    input_points = pd.read_csv(input_points_csv_filename, index_col=0)
    new_points = algo.resample(input_points=input_points)
    new_points.to_csv(output_points_csv_filename)

    return None, None


iteration_args = {
    'class': IterativePythonTask,
    'method': run_calibration_iteration,
    'name_root': 'iter',
    'method_kwargs': {
        'next_point_algorithm': {
            'value': NEXT_POINT_ALGORITHM
        },
        'input_points_csv_filename': {
            'pattern': 'points_%d.csv',
            'offset': -1  # apply this numerical shift to the task's number to get the right pattern input
        },
        'output_points_csv_filename': {
            'pattern': 'points_%d.csv',
            'offset': 0  # apply this numerical shift to the task's number to get the right pattern input
        },
        'reference_data_filename': {
            'value': 'reference.json'
        }
    }
}

iteration_mgr = IterationManagerPythonTask(name='iteration-manager',
                                           depends_on=['rename_input_files'],
                                           iteration_args=iteration_args,  # these define it
                                           workflow=None)  # must be set after Workflow creation to be functional

# TODO: once this example runs and works, make a variant where the iteration tasks are sub-workflows!

tasks = [
    PythonTask(name='process_reference_data',
               method=process_reference_data,
               method_kwargs={'reference_data_source': REFERENCE_DATA_SOURCE, 'output_filename': 'reference.json'},
               depends_on=[]),

    PythonTask(name='rename_input_files', method=copy_file,
               method_kwargs={'file': 'calibration_starting_points.csv', 'to': 'points_-1.csv'},
               depends_on=['process_reference_data']),

    iteration_mgr,

    PythonTask(name='resample',
               method=resample,
               method_kwargs={
                   'algorithm': RESAMPLE_ALGORITHM,
                   'final_calibration_args': iteration_mgr.args_for_last_iteration,  # This will be called to discover the filename.at run time for this task. User must be careful to consider dependencies appropriately!
                   'output_points_csv_filename': FINAL_POINTS_FILENAME
               },
               depends_on=['iteration-manager']),

    FinalizeTask(name='finalize', depends_on=[]),

]

wf = Workflow(name='demo', tasks=tasks)
iteration_mgr.workflow = wf

initial_status = wf.status
print('Initial status of tasks in Workflow:')
pprint(initial_status)

wf.start()

final_status = wf.status
print('Final status of tasks in Workflow:')
pprint(final_status)
