===========
Output data
===========

The output produced by running simulations using |IT_s| depends on the
configuration of the model itself. |IT_s| is itself agnostic to the output
format when running simulations.  However, the analysis framework expects
simulation output in CSV, JSON, XLSX, or TXT to be automatically loaded to a
Python object. All other formats are loaded as a raw binary stream. For more
information, see :doc:`analyzers`. 

If you are running simulations on |COMPS_s|, the configuration of the
:doc:`cli-config` file will determine where output files can be found. 

.. include:: reuse/comps_note.txt

If you are running simulations locally, you can find the output files in the output directory appended after the simulation ID. For example, the output from a simulation with an ID of 5000 could be found at http://localhost:5000/data/output.

The python_csv_output.py example below demonstrates how to produce output in CSV format for a simple parameter sweep.

.. literalinclude:: ../examples/python_model/python_csv_output.py
