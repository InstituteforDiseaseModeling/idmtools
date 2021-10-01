===========
Output data
===========

The output produced by running simulations using |IT_s| depends on the
configuration of the model itself. |IT_s| is itself agnostic to the output
format when running simulations.  However, the analysis framework expects
simulation output in CSV, JSON, XLSX, or TXT to be automatically loaded to a
Python object. All other formats are loaded as a raw binary stream. For more
information, see :doc:`analyzers/analyzers`.

If you are running simulations on |COMPS_s|, the configuration of the
"idmtools.ini" file will determine where output files can be found. 
For more information, see :doc:`cli/wizard`

.. include:: reuse/comps_note.txt

If you are running simulations or experiments locally, they are saved to your local computer at C:\\Users\\yourname\\.local_data\\workers for Windows and ~/.local_data/workers for Linux. 

Additionally, when running locally using Docker, output can be found in your browser in the output directory appended after the experiment or simulation ID. For example, the output from an experiment with an ID of S07OASET could be found at http://localhost:5000/data/S07OASET. The output from an individual simulation (ID FCPRIV7H) within that experiment could be found at http://localhost:5000/data/S07OASET/FCPRIV7H. 

The python_csv_output.py example below demonstrates how to produce output in CSV format for a simple parameter sweep.

.. literalinclude:: ../examples/python_model/python_csv_output.py