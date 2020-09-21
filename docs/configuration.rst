Configuration
=============

The configuration of |IT_s| is set in the idmtools.ini file. This file is normally located in the project directory but |IT_s| will search up through the directory hierarchy, and lastly the files *~/.idmtools.ini* on Linux and *%LOCALAPPDATA%\idmtools\idmtools.ini* on Windows. You can also specify the path to the idmtools file by setting the environment variable *IDMTOOLS_CONFIG_FILE*. An idmtools.ini file must be included when using |IT_s|.

Below is an example configuration file:

.. literalinclude:: ../examples/idmtools.ini

.. toctree::
   :maxdepth: 3
   :titlesonly:
   :caption: Specific configuration items and idmtools.ini wizard

   common-parameters
   logging
   wizard