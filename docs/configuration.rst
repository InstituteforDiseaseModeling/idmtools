=========
Configure
=========

The configuration of |IT_s| is set in the idmtools.ini file. This file is normally located in the project directory but |IT_s| will search up through the directory hierarchy, and lastly the files *~/.idmtools.ini* on Linux and *%LOCALAPPDATA%\\idmtools\\idmtools.ini* on Windows.
You can also specify the path to the idmtools file by setting the environment variable *IDMTOOLS_CONFIG_FILE*. An idmtools.ini file is recommended when using |IT_s|. If you want to generate an idmtools.ini file, see documentation about the :ref:`Configuration Wizard <idmtools-ini-wizard>`.
Configuration values can also be set using environment variables. The variables name can be specified using the format *IDMTOOLS_SECTION_OPTION* except for common options, which have the format *IDMTOOLS_OPTION*.

If no configuration file is found, an error is displayed. To supress this error, you can use *IDMTOOLS_NO_CONFIG_WARNING=1*

.. toctree::
   :maxdepth: 3
   :titlesonly:
   :caption: Specific configuration items and idmtools.ini wizard

   common-parameters
   logging
   cli/wizard

Below is an example configuration file:

.. literalinclude:: idmtools.ini
