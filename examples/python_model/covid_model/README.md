# covid_abm run on SSMT
Here is an example of the support of the `covid_abm` (https://github.com/amath-idm/covid_abm) model developed at IDM.
It cannot use the normal `Task` implementation because the dependencies do not install successfully on COMPS 
(scipy/numba) with our normal method.

The approach chosen is to create a SSMT worker to run the simulations contained in the script provided to the COVID19SSMT object.

The `COVID19SSMT` object takes the following as parameters:
- `item_name`: Name for the run on COMPS
- `covid_abm_path`: Path to the covid_abm package
- `run_script`: Path to the script to run on SSMT

The example folder contains the following:

- `covid_abm`: the model that will be added as an extra library
- `covid_ssmt.py`: contains the class COVID19SSMT implementing the specifics of running covid_abm on SSMT
- `commission_script.py`: the script that needs to be ran by the user to commission the worker
- `user_script.py`: the script that will be executed on SSMT and that will run the simulations