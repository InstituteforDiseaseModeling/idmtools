===========
Output data
===========

The output produced by running simulations using |IT_s| depends on the
configuration of the model itself. |IT_s| is itself agnostic to the output
format when running simulations. However, the analysis framework expects
simulation output in CSV or JSON format. For more information, see
:doc:`analyzers`. 

If you are running simulations on |COMPS_s|, the configuration of the
:doc:`cli-config` file will determine where output files can be found. 

.. include:: reuse/comps_note.txt

.. TBD add info about local simulations here

For example, the python_csv_output.py example below demonstrates how to produce output in CSV format for a simple parameter sweep.

.. literalinclude:: ../examples/python_model/python_csv_output.py
