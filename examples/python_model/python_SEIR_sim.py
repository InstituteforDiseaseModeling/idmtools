# Example Python Experiment with JSON Configuration
# In this example, we will demonstrate how to run a python experiment with JSON Configuration

# First, import some necessary system and idmtools packages.
import os
import sys
import json
from functools import partial
from typing import Any, Dict

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from inputs.ye_seir_model.custom_csv_analyzer import NodeCSVAnalyzer, InfectiousnessCSVAnalyzer


# Define some constant string used in this example
class ConfigParameters():
    Infectious_Period_Constant = "Infectious_Period_Constant"
    Base_Infectivity_Constant = "Base_Infectivity_Constant"
    Base_Infectivity_Distribution = "Base_Infectivity_Distribution"
    GAUSSIAN_DISTRIBUTION = "GAUSSIAN_DISTRIBUTION"
    Base_Infectivity_Gaussian_Mean = "Base_Infectivity_Gaussian_Mean"
    Base_Infectivity_Gaussian_Std_Dev = "Base_Infectivity_Gaussian_Std_Dev"


# Script need to be in a main block, other wise AnalyzerManager will have issue with multi threads in Windows OS.
if __name__ == '__main__':
    # We have python model defined in "SEIR_model.py" which takes several arguments like "--duration" and "--outbreak_coverage",
    # and supports a json config from a file named "nd_template.json". We want to sweep some arguments passed in to
    # "SEIR_model.py" and some parameters in "nd_template.json".
    # To accomplish this, we are going to proceed in a few high-level steps. See https://bit.ly/37DHUf0 for workflow
    # 1. Define our base task. This task is the common configuration across all our tasks. For us, that means some basic
    #    run info like script path as well as our arguments/value and parameter/value we don't plan on sweeping,
    #    "--duration", and most of the parameters inside "nd_template.json".
    # 2. Then we will define our TemplateSimulations object that will use our task to build a series of simulations
    # 3. Then we will define a SimulationBuilder and define our sweeps. This will involve also writing some callback
    #    functions that update the each task's config or option with the sweep values
    # 4. Then we will add our simulation builder to our TemplateSimulation object.
    # 5. We will then build our Experiment object using the TemplateSimulations as our simulations list.
    # 6. We will run the experiment on the platform
    # 7. Once and experiment is succeeded, we run two CSV analyzer to analyze results from the python model.

    # 1. first let's define our base task. Normally, you want to do set any assets/configurations you want across the
    # all the different Simulations we are going to build for our experiment. Here we load config file from a template json
    # file and rename the config_file_name(default value is config.json)
    parameters = json.load(open(os.path.join("inputs", "ye_seir_model", "Assets", "templates", 'seir_configuration_template.json'), 'r'))
    parameters[ConfigParameters.Base_Infectivity_Distribution] = ConfigParameters.GAUSSIAN_DISTRIBUTION
    task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "ye_seir_model", "Assets", "SEIR_model.py"),
                                    parameters=parameters,
                                    config_file_name="seir_configuration_template.json")
    # We define arguments/value for simulation duration that we don't want to sweep as an option for the task.
    task.command.add_option("--duration", 40)

    # 2. now let's use this task to create a TemplatedSimulation builder. This will build new simulations from sweep builders
    # we will define later. We can also use it to manipulate the base_task or the base_simulation
    ts = TemplatedSimulations(base_task=task)
    # We can define common metadata like tags across all the simulations using the base_simulation object
    ts.base_simulation.tags['simulation_name_tag'] = "SEIR_Model"

    # 3. Since we have our templated simulation object now, let's define our sweeps
    # To do that we need to use a builder
    builder = SimulationBuilder()

    # When adding sweep definitions, you need to generally provide two items
    # See https://bit.ly/314j7xS for a diagram of how the Simulations are built using TemplateSimulations +
    # SimulationBuilders
    # 3.1. A callback function that will be called for every value in the sweep. This function will receive a Simulation
    #    object and a value. You then define how to use those within the simulation. Generally, you want to pass those
    #    to your task's configuration interface. In this example, we are using JSONConfiguredPythonTask which has a
    #    set_parameter function that takes a Simulation, a parameter name, and a value. To pass to this function, we will
    #    user either a class wrapper or function partials
    # 3.2. A list/generator of values

    # Since our models uses a json config let's define an utility function that will update a single parameter at a
    # time on the model and add that param/value pair as a tag on our simulation.

    def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        """
        This function is called during sweeping allowing us to pass the generated sweep values to our Task Configuration

        We always receive a Simulation object. We know that simulations all have tasks and that for our particular set
        of simulations they will all include JSONConfiguredPythonTask. We configure the model with calls to set_parameter
        to update the config. In addition, we are can return a dictionary of tags to add to the simulations so we return
        the output of the 'set_parameter' call since it returns the param/value pair we set

        Args:
            simulation: Simulation we are configuring
            param: Param string passed to use
            value: Value to set param to

        Returns:

        """
        return simulation.task.set_parameter(param, value)


    # Let's sweep the parameter 'Base_Infectivity_Gaussian_Mean' for the values 0.5 and 2. Since our utility function requires
    # a Simulation, param, and value but the sweep framework all calls our function with Simulation, value, let's use the
    # partial function to define that we want the param value to always be "Base_Infectivity_Gaussian_Mean" so we can perform our sweep
    set_base_infectivity_gaussian_mean = partial(param_update, param=ConfigParameters.Base_Infectivity_Gaussian_Mean)
    # now add the sweep to our builder
    builder.add_sweep_definition(set_base_infectivity_gaussian_mean, [0.5, 2])


    # An alternative to using partial is define a class that store the param and is callable later. let's use that technique
    # to perform a sweep one the values 1 and 2 on parameter Base_Infectivity_Gaussian_Std_Dev

    # First define our class. The trick here is we overload __call__ so that after we create the class, and calls to the
    # instance will be relayed to the task in a fashion identical to the param_update function above. It is generally not
    # best practice to define a class like this in the body of our main script so it is advised to place this in a library
    # or at the very least the top of your file.
    class setParam:
        def __init__(self, param):
            self.param = param

        def __call__(self, simulation, value):
            return simulation.task.set_parameter(self.param, value)

    # Now add our sweep on a list
    builder.add_sweep_definition(setParam(ConfigParameters.Base_Infectivity_Gaussian_Std_Dev), [0.3, 1])

    # Use the same methodologies, we can sweep on option/arguments that pass to our Python model, uncomment the following code to enable it
    # # 3.3 first method:
    # def option_update(simulation: Simulation, option: str, value: Any) -> Dict[str, Any]:
    #     simulation.task.command.add_option(option, value)
    #     return {option: value}
    # set_outbreak_coverage = partial(option_update, option="--outbreak_coverage")
    # builder.add_sweep_definition(set_outbreak_coverage, [0.01, 0.1])
    #
    # # 3.4 second method:
    # class setOption:
    #     def __init__(self, option):
    #         self.option = option
    #
    #     def __call__(self, simulation, value):
    #         simulation.task.command.add_option(self.option, value)
    #         return {self.option: value}
    # builder.add_sweep_definition(setOption("--population"), [1000, 4000])

    # 4. Add our builder to the template simulations
    ts.add_builder(builder)

    # 5. Now we can create our Experiment using our template builder
    experiment = Experiment(name=os.path.split(sys.argv[0])[1], simulations=ts)
    # Add our own custom tag to simulation
    experiment.tags['experiment_name_tag'] = "SEIR_Model"
    # And maybe some custom Experiment Level Assets
    experiment.assets.add_directory(assets_directory=os.path.join("inputs", "ye_seir_model", "Assets"))

    # 6. In order to run the experiment, we need to create a `Platform`
    # The `Platform` defines where we want to run our simulation.
    # You can easily switch platforms by changing the Platform to for example 'CALCULON'
    platform = Platform('CUMULUS')

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True)

    # Check experiment status, only move to Analyzer step if experiment succeeded.
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        sys.exit(-1)

    # 7. Now let's look at the experiment results. Here are two outputs we want to analyze.
    filenames = ['output/individual.csv']
    filenames_2 = ['output/node.csv']

    # Initialize two analyser classes with the path of the output csv file
    analyzers = [InfectiousnessCSVAnalyzer(filenames=filenames), NodeCSVAnalyzer(filenames=filenames_2)]

    # Specify the id Type, in this case an Experiment on COMPS
    manager = AnalyzeManager(partial_analyze_ok=True,
                             ids=[(experiment.uid, ItemType.EXPERIMENT)],
                             analyzers=analyzers)
    # Analyze
    manager.analyze()
    sys.exit(0)

