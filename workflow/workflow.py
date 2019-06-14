from copy import deepcopy
import diskcache
import shutil
import time
import yaml

from task import Task
from DAG import DAG


class Workflow:

    CACHE = diskcache.Cache('workflow.diskcache')

    def __init__(self, tasks):
        self.dag = DAG(nodes=tasks)

    @property
    def status(self):
        return {task.name: task.status for task in self.dag.nodes}

    def start(self):
        # if there is state indicating a partial run, this method should just skip all the stuff that is done

        # we should really allow > 1 task at a time, using a single execution process (this one) for prototype
        while not self.all_completed:
            print('Not all completed, continuing...')
            task = self.get_task_for_processing()
            if task is not None:
                print(f'Got new task for running: {task.name} - {task.status}')
                task.run()
            else:
                print('No task is ready, waiting...')
                time.sleep(1)
        print('DONE EXECUTING WORKFLOW')

    def get_task_for_processing(self):
        # returns None if no task is ready for processing,
        selected_task = None
        for task in self.dag.nodes:
            dependee_tasks = task.dependees
            if task.status in Task.READY_STATUSES and all([dt.status == Task.SUCCEEDED for dt in dependee_tasks]):
                selected_task = task
                break
        return selected_task

    @property
    def all_completed(self):
        # returns True/False
        return all([task.status in Task.COMPLETED_STATUSES for task in self.dag.nodes])

    @classmethod
    def from_yaml(cls, yaml_filename, clear_cache=False):

        # TODO: is this really the right way/place for this?
        if clear_cache:
            cls.CACHE.clear()

        # TODO: make sure dependents/dependees are set on task load
        with open(yaml_filename, 'r') as f:
            dict_spec = yaml.safe_load(f)

        task_defaults = dict_spec['defaults']
        workflow_dict = dict_spec['workflow']

        tasks = []
        for task_name, task_details in workflow_dict.items():
            task_definition = cls.deep_merge(task_defaults, task_details)
            task_definition['name'] = task_name
            task_definition['cache'] = cls.CACHE
            task = Task(**task_definition)
            tasks.append(task)
        return cls(tasks=tasks)

    @classmethod
    def deep_merge(cls, dict1, dict2):
        # merge dict2 into/on top of dict1
        # only recurses into dictionaries (e.g. not lists, or lists of dictionaries)
        # does not modify either dict inputs; returns a new dict
        merged_dict = {}

        all_keys = set(list(dict1.keys()) + list(dict2.keys()))
        for k in all_keys:
            if k in dict1 and k not in dict2:
                # the key exists only in the destination dictionary
                merged_dict[k] = deepcopy(dict1[k])
            elif k in dict2 and k not in dict1:
                # the key exists only in the source dictionary
                merged_dict[k] = deepcopy(dict2[k])
            else:
                types = {type(dict1[k]), type(dict2[k])}
                if len(types) != 1:
                    raise Exception('Cannot merge items of different types: %s' % types)
                if isinstance(dict1[k], dict):
                    # the key is in both the destination and source and the value is a dict, recurse
                    merged_dict[k] = cls.deep_merge(dict1[k], dict2[k])
                else:
                    # the key is in both the destination and source and the value is NOT a dict; use the source value
                    merged_dict[k] = deepcopy(dict2[k])
        return merged_dict

    def to_json(self):
        return self.dag.to_json()
