import json
import os
import traceback
from argparse import Namespace
from logging import getLogger, DEBUG
from COMPS import Client
from idmtools.core.exceptions import idmtools_error_handler

logger = getLogger(__name__)
user_logger = getLogger('user')


def ensure_debug_logging():
    # set to debug before loading idmtools
    os.environ['IDMTOOLS_LOGGING_LEVEL'] = 'DEBUG'
    os.environ['IDMTOOLS_LOGGING_CONSOLE'] = 'on'
    from idmtools.core.logging import setup_logging
    setup_logging(level=DEBUG, console=True, force=True)
    # Import idmtools here to enable logging
    from idmtools import __version__
    logger.debug(f"Using idmtools {__version__}")


def setup_verbose(args: Namespace):
    print(args)
    if args.verbose:
        ensure_debug_logging()
        logger.debug(f"Args: {args}")


def login_to_env():
    # load the work item
    client = Client()
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Logging into {os.environ['COMPS_SERVER']}")
    client.login(os.environ['COMPS_SERVER'])
    return client


def get_error_handler_dump_config_and_error(jc):
    def ssmt_error_handler(exctype, value: Exception, tb):
        with open("error_reason.json", 'w') as err_out:
            output_error = dict(type=exctype.__name__, args=list(value.args), tb=traceback.format_tb(tb), job_config=jc)
            output_error['tb'] = [t.strip() for t in output_error['tb']]
            if hasattr(value, 'doc_link'):
                output_error['doc_link'] = value.doc_link
            json.dump(output_error, err_out, indent=4, sort_keys=True)

        idmtools_error_handler(exctype, value, tb)

    return ssmt_error_handler
