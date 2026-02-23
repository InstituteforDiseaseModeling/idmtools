===============
Troubleshooting
===============

You can use troubleshooting commands to get information about plugins (CLI, Platform, and Task) and to get detailed system information. To see the list of troubleshooting commands, type the following at a command prompt:

.. command-output:: idmtools info --help

To see the list of troubleshooting commands and options for the ``plugins`` command, type the following at a command prompt:

.. command-output:: idmtools info plugins --help

To see the list of troubleshooting options for the ``system`` command, type the following at a command prompt:

.. command-output:: idmtools info system --help

To see the versions of |IT_s| and related modules, along with the plugins they provide, you can use the ``version`` command. Here is an example of the output:

.. command-output:: idmtools version

To see a list of the predefined configurations from platform plugins, use the command:

.. command-output:: idmtools info plugins platform-aliases