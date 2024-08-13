.. _idmtools-ini-wizard:

idmtools.ini wizard
===================

You can use the ``config`` command to create a configuration block in your project's ``idmtools.ini`` file.

.. command-output:: idmtools config --help

If you do not specify a config path, the command will use the ``idmtools.ini`` file in the current directory. To edit a different file, use the ``--config_path`` argument to specify its path, such as: ``idmtools config --config_path C:\my_project\idmtools.ini``.

Use the ``block`` command to start the wizard that will guide you through the creation of a configuration block in the selected ``idmtools.ini``, for example: ``idmtools config block``.

Here is a demo of the command in action

.. image:: /images/config-wizard.svg