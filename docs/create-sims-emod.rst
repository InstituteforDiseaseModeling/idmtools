===========================
Create |EMOD_s| simulations
===========================

To create simulations using |EMOD_s| you must use the `emodpy <https://emod-hub.github.io/emodpy/>`__ with |IT_s|. Included with emodpy is the :py:class:`~emodpy.emod_task.EMODTask` class, inheriting from the :py:class:`~idmtools.entities.itask.ITask` abstract class, and used for the running and configuration of |EMOD_s| simulations and experiments.

.. uml::

    @startuml
    abstract class ITask
    ITask <|-- EMODTask
    @enduml

For more information about the architecture of job (simulation/experiment) creation and how |EMOD_s| leverages |IT_s| plugin architecture, see :doc:`reference`.

The following Python excerpt shows an example of using :py:class:`~emodpy.emod_task.EMODTask` class and from_default method to create a task object using default config, campaign, and demographic values from :py:class:`~emodpy.defaults.emod_sir.EMODSir` class and to use the |exe_s| from local directory::

    task = EMODTask.from_default(default=EMODSir(), eradication_path=os.path.join(BIN_PATH, "Eradication"))

Another option, instead of using from_default, is to use the from_files method::

    task = EMODTask.from_files(config_path=os.path.join(INPUT_PATH, "config.json"),
                               campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                               demographics_paths=os.path.join(INPUT_PATH, "demographics.json"),
                               eradication_path=eradication_path)

For complete examples of the above see the following Python scripts:

* (from_default) :py:class:`emodpy.examples.create_sims_from_default_run_analyzer`
* (from_files) :py:class:`emodpy.examples.create_sims_eradication_from_github_url`