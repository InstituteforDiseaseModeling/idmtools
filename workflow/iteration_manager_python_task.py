from copy import deepcopy
import json
import os
import re

from python_task import PythonTask


class IterationManagerPythonTask(PythonTask):

    BLANK_REPETITION_DICT = {
        'continue': True,
        'n_additional_repetitions': 2 # ck4, change values back to None after debug
    }

    REPETITION_FILE_PATTERN = 'iteration_check-%s.json'

    def __init__(self, workflow, iteration_args, **kwargs):
        kwargs['method'] = self.load_and_process_repetition_file
        super().__init__(**kwargs)

        # to make a iterative task object, we need to know what to call and with what to call it
        # e.g.
        # 'class': PythonTask
        # 'iterable_kwargs': {'name': 'name_root', 'input_filename': 'abc_%d.csv', 'output_filename': 'abc_%d.csv'}
        # 'non_iterable_kwargs': {'username': 'ckirkman'}
        self.workflow = workflow
        self.iteration_args = iteration_args

        self.control_filename = self.REPETITION_FILE_PATTERN % self.name

        self.iteration_task_pattern = re.compile('^%s_(?P<iteration_number>\d+)$' % self.iteration_args['name_root'])

    def load_and_process_repetition_file(self):
        # First try to load the repetition control file (it may or may not exist)
        try:
            with open(self.control_filename, 'r') as f:
                repetition_dict = json.load(f)
        except FileNotFoundError:
            # write a blank repetition file and error (expect user input)
            self.write_blank_repetition_file()
            raise Exception(f'Repetition file must be edited to continue: {self.control_filename}')

        if repetition_dict['continue'] is True:
            # add the appropriate tasks to the workflow and continue

            # First, create numbered copies of the iterative dependee of this task and link them into the dag
            for i in range(repetition_dict['n_additional_repetitions']):
                # tiling the needed args/inputs/outputs + linking the new task in
                self.insert_new_iteration_task()

                # now rebuild the dag
                self.workflow.build_dag()

            next_state = self.UNSTARTED

            os.remove(self.control_filename)
        elif repetition_dict['continue'] is False:
            # do not add any tasks and THIS task is successful/done now
            next_state = self.SUCCEEDED
            os.remove(self.control_filename)
        else:
            raise Exception('Invalid repetition control value: %s' % repetition_dict['continue'])
        return None, next_state

    def write_blank_repetition_file(self):
        with open(self.control_filename, 'w') as f:
            json.dump(self.BLANK_REPETITION_DICT, f)

    def insert_new_iteration_task(self, workflow=None):
        workflow = workflow or self.workflow
        most_recent_iteration_task, iteration_number = self.get_most_recent_iteration_task()
        iteration_number += 1
        if most_recent_iteration_task is None:
            print('MOST RECENT ITER TASK: None NUM: %s' % (iteration_number))
            print('MGR depends on: %s' % self.depends_on)
            # this is the FIRST iteration task we are making. It must link to the dependees of THIS task
            new_iteration_task = self.make_new_iteration_task(iteration_number=0,
                                                              depends_on=deepcopy(self.depends_on))
        else:
            print('MOST RECENT ITER TASK: %s NUM: %s' % (most_recent_iteration_task.name, iteration_number))
            print('MGR depends on: %s' % self.depends_on)
            # there has been at least one previous iteration task. The new iteration task will depend on the most recent
            new_iteration_task = self.make_new_iteration_task(iteration_number=iteration_number,
                                                              depends_on=[most_recent_iteration_task.name])
            # This task no longer depends directly on the prior most_recent_task now. Remove the dependence. dag.build()
            # call will break the dependent relationship; not possible to call it out explicitly here.
            self.depends_on = [task_name for task_name in self.depends_on if task_name != most_recent_iteration_task.name]
        self.depends_on.append(new_iteration_task.name)
        print('ADDING NEW TASK TO DAG: %s' % new_iteration_task.name)
        workflow.dag.add_node(new_iteration_task)
        print('DONE INSERTING')

    def make_new_iteration_task(self, iteration_number, depends_on):
        # We need to make a task object of the requested iterative type with incremented iteration number arguments
        iteration_task_class = self.iteration_args['class']

        all_args = {}
        name_root = self.iteration_args['name_root']
        all_args['name'] = f'{name_root}_{iteration_number}'  # no offset for name
        all_args['method'] = self.iteration_args['method']
        all_args['depends_on'] = depends_on

        method_kwargs = {}
        for arg, arg_config in self.iteration_args['method_kwargs'].items():
            pattern = arg_config['pattern']
            offset = arg_config.get('offset', 0)  # offset allows for chaining with prior/next iterations
            method_kwargs[arg] = pattern % (iteration_number + offset)
        all_args['method_kwargs'] = method_kwargs

        new_task = iteration_task_class(**all_args)
        return new_task

    def get_most_recent_iteration_task(self):
        # TODO: WARNING: this assumes the pattern is SOMETHING_%d !!!
        possible_tasks = [task for task in self.dependees if self.iteration_task_pattern.match(task.name)]
        if len(possible_tasks) == 0:
            most_recent_iteration_task = None
            iteration_number = -1
        elif len(possible_tasks) == 1:
            most_recent_iteration_task = possible_tasks[0]
            iteration_number = self.iteration_task_pattern.match(most_recent_iteration_task.name)['iteration_number']
            iteration_number = int(iteration_number)
        else:
            raise Exception('Could not determine most recent iteration task. %d tasks matched.' %
                            len(possible_tasks))
        return most_recent_iteration_task, iteration_number

    def discover_additional_tasks(self, workflow=None):
        workflow = workflow or self.workflow
        print('DISCOVERING ADDITIONAL TASKS')
        # discover all tasks that look like iterative tasks generated by this manager and sort by number

        # link them all together and organize by iteration number
        print('LOOKING THROUGH CACHED TASKS: %s' % [k for k in self.CACHE.iterkeys()])
        task_names = [k for k in self.CACHE.iterkeys() if self.iteration_task_pattern.match(k)]
        if len(task_names) == 0:
            return  # nothing to do

        task_names = sorted(task_names, key=lambda k: self.iteration_task_pattern.match(k)['iteration_number'])
        task_names = {int(self.iteration_task_pattern.match(k)['iteration_number']): k for k in task_names}
        task_numbers = list(sorted(task_names.keys()))
        min_task_number = task_numbers[0]
        max_task_number = task_numbers[-1]
        for task_number in range(min_task_number, max_task_number+1):
            print('INSERTING TASK NUMBER: %s' % task_number)
            self.insert_new_iteration_task(workflow=workflow)
            # now rebuild the dag
            workflow.build_dag()

        print('AFTER DISCOVERY TASKS: %s' % [t.name for t in workflow.dag.nodes])
        import sys
        sys.stdout.flush()
