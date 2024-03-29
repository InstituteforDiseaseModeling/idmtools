Logging overview
================

|IT_s| includes built-in logging, which is configured in the [LOGGING] section of the idmtools.ini file, and includes the following parameters: **level**, **console**, and **filename**. Default settings are shown in the following example::

    [LOGGING]
    level = INFO
    console = off
    filename = idmtools.log

Logging verbosity is controlled by configuring the parameter, **level**, with one of the below listed options. They are in descending order, where the lower the item in the list, the more verbose logging is included.

| CRITICAL
| ERROR
| WARNING
| INFO
| DEBUG

Console logging is enabled by configuring the parameter, **console**, to "on". The **filename** parameter can be configured to something other than the default filename, "idmtools.log".

See :ref:`Enabling/Disabling/Changing Log Level at Runtime` for an example on enabling logging/changing levels at runtime.