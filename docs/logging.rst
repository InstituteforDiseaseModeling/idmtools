Logging
=======

|IT_s| includes built-in logging, which is configured in the [LOGGING] section of the idmtools.ini file, and includes the following parameters: **level**, **console**, **file_level**, **enable_file_logging**, and **log_filename**. Default settings are shown in the following example::

    [LOGGING]
    level = INFO
    console = off
    file_level = DEBUG
    enable_file_logging = on
    log_filename = idmtools.log

Logging verbosity is controlled by configuring the parameter, **level**, with one of the below listed options. They are in descending order, where the lower the item in the list, the more verbose logging is included.

| CRITICAL
| ERROR
| WARNING
| INFO
| DEBUG

Console logging is enabled by configuring the parameter, **console**, to "on".

File logging is enabled by default, however it can be disabled by configuring the parameter, **enable_file_logging**, to "off".The **log_filename** parameter can be configured to something other than the default filename, "idmtools.log".

