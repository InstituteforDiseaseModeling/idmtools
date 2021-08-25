from logging import getLogger

from idmtools.core.logging import setup_logging, IdmToolsLoggingConfig

# At any point in running you can import the setup logging to reset logging
# In this example, we enable the console logger at run time
logger = getLogger()
logger.debug("This will not be visible at the command line")
setup_logging(IdmToolsLoggingConfig(console=True, level='DEBUG', force=True))
logger.debug("You should be able to see this at the command line")
