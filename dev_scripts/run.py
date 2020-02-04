import argparse
import os
import subprocess
import sys
from logging import getLogger
import logging

logger = getLogger(__name__)


def setup_logging(working_dir):
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    fileHandler = logging.FileHandler("%s/make.log" % os.path.abspath(working_dir))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--environment', nargs='+', help='Environment variables to set ')
    parser.add_argument('-wd', '--working-dir', help='Working Directory')
    parser.add_argument('-rt', '--return-code', default=None, help='Return Code')
    parser.add_argument('-p', '--path', nargs='+', help='Add items to the path')
    parser.add_argument('-ex', help='Add items to the path')

    args = parser.parse_args()
    setup_logging(args.working_dir)
    if args.environment:
        env = dict()
        for e in args.environment:
            parts = e.split("=")
            env[parts[0]] = parts[1]
        logger.info(f"Environment opts: {env}")

    if args.path:
        for p in args.path:
            logger.info(f'Adding {os.path.abspath(p)} to the path')
            sys.path.insert(0, os.path.abspath(p))

    logger.debug('Environment: %s', str(os.environ))

    if args.working_dir:
        logger.info(f'Changing working directory to {os.path.abspath(args.working_dir)}')
        os.chdir(os.path.abspath(args.working_dir))
    logger.info(f'Running {args.ex}')
    try:
        output = subprocess.check_output(args.ex)
        result = 0
    except subprocess.CalledProcessError as e:
        result = e.returncode
        output = e.output
        logger.debug(f'Return Code: {result}')
    logger.debug('Command output: %s', output)
    sys.exit(result)
