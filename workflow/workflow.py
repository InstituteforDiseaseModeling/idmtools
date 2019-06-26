from copy import deepcopy
import diskcache
import time
import yaml

from task import Task
from system_task import SystemTask
from DAG import DAG


class Workflow:

    CACHE = diskcache.Cache('workflow.diskcache')

    BLANK_CACHE_ENTRY = {
        'name': None,
        'tasks': []
    }

    def __init__(self, name, tasks):
        self.name = name
        # for task in tasks:
        #     task.set_cache(cache)

        self.dag = DAG(nodes=tasks)

        # not ALL tasks are necessarily specified in the arguments. Iterative tasks are NOT
        # and must be discovered (they are dynamically generated). To get them, we ask every
        # task we know about to discover and splice in the appropriate tasks.
        for task in tasks:
            if hasattr(task, 'discover_additional_tasks'):
                task.discover_additional_tasks(workflow=self)

        # reset all FAILED tasks to UNSTARTED, including discovered ones
        for task in tasks:
            if task.status == Task.FAILED:
                task.status = Task.UNSTARTED


    @property
    def status(self):
        return {task.name: task.status for task in self.dag.nodes}

    def start(self):
        # if there is state indicating a partial run, this method should just skip all the stuff that is done

        # While there are tasks that could potentially be started in the future (the non-fail-blocked, non-succeeded
        # subgraph is not empty

        # we should really allow > 1 task at a time, using a single execution process (this one) for prototype
        while len(self.get_unblocked_tasks()) > 0:
            print('Not all completed, continuing...')
            print({t.name: t.status for t in self.dag.nodes})
            task = self.get_task_for_processing()
            if task is not None:
                print(f'Got new task for running: {task.name} - {task.status} - {task.depends_on} - {len(task.dependees)}')
                task.run()
            else:
                print('No task is ready, waiting...')
                time.sleep(1)
        print('DONE EXECUTING WORKFLOW')
        print('Final state:\n%s' % self.status)

    def get_task_for_processing(self):
        ready_tasks = self.get_ready_tasks()
        if len(ready_tasks) > 0:
            selected_task = ready_tasks[0]
        else:
            selected_task = None
        return selected_task

    def get_ready_tasks(self):
        # returns None if no task is ready for processing,
        ready_tasks = []
        for task in self.dag.nodes:
            dependee_tasks = task.dependees
            if task.status in Task.READY_STATUSES and all([dt.status == Task.SUCCEEDED for dt in dependee_tasks]):
                ready_tasks.append(task)
        return ready_tasks

    def get_unblocked_tasks(self):
        import sys
        # an unblocked task is one that is not in a self.COMPLETED state (SUCCEEDED, FAILED) and does not descend from
        # a FAILED task. Meaning, a Task that is running or could potentially run in the future.
        unblocked_tasks = []
        for task in self.dag.nodes:
            print('CHECKING TO SEE IF TASK %s IS UNBLOCKED...' % task.name)
            sys.stdout.flush()
            if task.status not in Task.COMPLETED_STATUSES:
                dependee_nodes = self.dag.get_dependee_nodes(node=task, include_indirect=True)
                if all([t.status != Task.FAILED for t in dependee_nodes]):
                    print('%s IS UNBLOCKED...' % task.name)
                    sys.stdout.flush()
                    unblocked_tasks.append(task)
                else:
                    print('%s IS **BLOCKED...' % task.name)
                    sys.stdout.flush()
            else:
                print('%s IS ALREADY IN A COMPLETED STATE: %s' % (task.name, task.status))
                sys.stdout.flush()

        return unblocked_tasks

    @property
    def all_completed(self):
        # returns True/False
        return all([task.status in Task.COMPLETED_STATUSES for task in self.dag.nodes])

    @classmethod
    def from_yaml(cls, yaml_filename):
        # TODO: make sure dependents/dependees are set on task load
        with open(yaml_filename, 'r') as f:
            dict_spec = yaml.safe_load(f)

        task_defaults = dict_spec['defaults']
        workflow_dict = dict_spec['workflow']

        tasks = []
        for task_name, task_details in workflow_dict.items():
            task_definition = cls.deep_merge(task_defaults, task_details)
            task_definition['name'] = task_name
            task = SystemTask(**task_definition)
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

    def to_cache(self):
        # fully update workflow & contained task state in the the caches
        try:
            entry = self.CACHE[self.name]
        except KeyError:  # it a task is not in the db, create a new entry
            entry = deepcopy(self.BLANK_CACHE_ENTRY)

        # update info, then write to cache
        entry['tasks'] = [task.name for task in self.dag.nodes]
        self.CACHE[self.name] = entry
        for task in self.dag.nodes:
            task.to_cache()

    def from_cache(self):
        raise Exception('unimplemented. Do it, and do it for task classes where needed, particularly'
                        'the dynamically created tasks. Might need to dump a lot more info to task cache?')

    def build_dag(self):
        # the purpose of this method is to make sure the in-memory/in-DB state of the workflow is
        # the same. Otherwise, the dag knows how to build itself.
        print('REBUILDING DAG')
        self.dag.build()
        print('DONE REBUILDING DAG')
        self.to_cache()

