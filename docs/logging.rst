Logging
=======
IDM-Tools has built in logging. In the default configurtion, only messages in the *INFO* level are logged to a file
called idmtools.log. You can change the log filename using the parameter *log_filename* under the *Logging section
of idmtools.ini. You can also enable console logging by setting the *console* parameter to *on* paramter within 
the configuration section. Lastly, you can change the logging verbosity by setting the *level* parameter to either
CRITICAL, ERROR, WARN, INFO, or DEBUG.