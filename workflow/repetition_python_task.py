import json
import os

from iterative_python_task import IterativePythonTask


# A RepetitionTask can ONLY depend on an iterative-type task, e.g. IterativePythonTask
# TODO: add verification somewhere to enforce this if feasible
class RepetitionPythonTask(IterativePythonTask):

    class DependeeCountException(Exception):
        pass

    BLANK_REPETITION_DICT = {
        'continue': None,
        'n_repetitions': None
    }

    def __init__(self, path, workflow, **kwargs):
        self.workflow = workflow
        kwargs['method'] = self.load_and_process_repetition_file
        iterative_attributes = {'path': f'{path}-%d'}

        n_dependees = len(kwargs.get('depends_on', []))
        # n_dependees = len(kwargs.get('dependees', []))  # TODO: a hack in light of using 'depends_on'
        if n_dependees != 1:
            raise self.DependeeCountException(f'A RepetitionPythonTask must have exactly 1 dependee task, not '
                                              f'{n_dependees}')

        super().__init__(iterative_attributes=iterative_attributes, **kwargs)

        # record keeping for copy()
        self.initialization_path = path
        self.initialization_workflow = workflow
        self.kwargs_for_super = kwargs

    def copy(self):
        from copy import deepcopy  # so we don't pollute prior objects history/remembered kwargs
        kwargs = deepcopy(self.kwargs_for_super)
        kwargs['number'] = self.number + 1
        return type(self)(path=self.initialization_path, workflow=self.initialization_workflow,
                          **kwargs)

    # TODO: any exception in this method should trigger FAIL, and write out a blank repetition file for editing
    def load_and_process_repetition_file(self):
        path = self.path
        try:
            with open(path, 'r') as f:
                repetition_dict = json.load(f)
        except FileNotFoundError:
            # write a blank repetition file and error (expect user input)
            self.write_blank_repetition_file()
            raise Exception(f'Repetition file must be edited to continue: {path}')

        # File does exist, so delete it and then process the loaded repetition file
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

        # TODO: add code to read/honor n_duplicates properly
        if repetition_dict['continue'] is True:
            # add the appropriate tasks to the workflow and continue

            # TODO: write the numbered_copy method or its equivalent and update this line
            # First, create numbered copies of the single dependee this task has. Link them up.
            prior_task = None
            new_tasks = []
            for i in range(repetition_dict['n_repetitions']):
                new_task = self.dependees[0].copy()
                if prior_task is not None:
                    new_task.depends_on = [prior_task.name]
                new_tasks.append(new_task)
                prior_task = new_task

            # TODO: write the numbered_copy method or its equivalent and update this line
            # TODO: make sure the new repetition task has a DIFFERENT path it checks for the repetition file
            # now create a a numbered copy of THIS repetition task
            new_repetition_task = self.copy()

            # link them together so the new repetition task depends on the duplicated dependee
            # and then splice it into the workflow between this task and this task's dependents
            new_tasks[0].depends_on = [self.name]

            new_repetition_task.depends_on = [new_tasks[-1].name]

            # as a nicety, we should remove THIS task (self.name) from the depends_on list of self.dependents
            # from a DAG correctness point of view, it is not a problem, however (just makes visualization messier)
            # self.dependents = [new_task]

            # now rebuild the dag after adding the new nodes to it
            all_tasks = self.workflow.dag.nodes + new_tasks + [new_repetition_task]
            self.workflow.dag.nodes = all_tasks
            self.workflow.dag.build()
        else:
            # do not add any tasks and THIS task is successful/done now
            pass

    def write_blank_repetition_file(self):
        with open(self.path, 'w') as f:
            json.dump(f, self.BLANK_REPETITION_DICT)
