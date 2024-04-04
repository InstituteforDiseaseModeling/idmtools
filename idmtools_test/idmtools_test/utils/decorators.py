import functools
import shutil

import tempfile

import os
import platform
import time
import unittest
from functools import wraps
from logging import getLogger
from typing import Callable, Union, Any, Optional
import pytest
from idmtools import IdmConfigParser
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.utils import is_global_configuration_enabled

# The following decorators are used to control test
# To allow for different use cases(dev, test, packaging, etc)
# We have switches that should allow a rich set of possible
# test combinations
#
# The default tests run with all the optional tests set to off(except Linux since that is auto-detected)
# For test-external runs any tests that require external communication
# This currently is any comps related test
# test-docker run any tests that depend on docker locally(Mostly local runn)
# test-all runs all tests

logger = getLogger(__name__)

linux_only = unittest.skipIf(
    not platform.system() in ["Linux", "Darwin"], 'No Tests that are meant for linux'
)

windows_only = unittest.skipIf(
    platform.system() in ["Linux", "Darwin"], 'No Tests that are meant for Windows'
)

skip_if_global_configuration_is_enabled = pytest.mark.skipif(is_global_configuration_enabled(), reason=f"Either {IdmConfigParser.get_global_configuration_name()} is set or the environment variable 'IDMTOOLS_CONFIG_FILE' is set")
# this is mainly for docker in docker environments but also applies to environments
# where you must use the local ip address for connectivity vs localhost
skip_api_host = unittest.skipIf(os.getenv("API_HOST", None) is not None, "API_HOST is defined")


def run_test_in_n_seconds(n: int, print_elapsed_time: bool = False) -> Callable:
    """
    Decorator that assert a test will run in N seconds. If it does not, it will fail.

    THIS DOES NOT MANAGE processes and it will not stop long running processes. It simply times a test and ensure it
    ran in less than N seconds

    Args:
        n (int): Number of seconds that is considered acceptable
        print_elapsed_time: Will print the function name and elasped time at the end of each function it decorates

    Returns:
        (Callable) : Wrapped function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            end = time.time()
            if print_elapsed_time:
                print(f"{func.__name__} took {end - start}s to run!")
            args[0].assertLess(end - start, n, f"{func.__name__} took {end - start}s to run!")
            return ret

        return wrapper

    return decorator


def default_fixture_pickle_save(filename, args, pickler=None, write_mode='bw'):
    if pickler is None:
        import pickle
        pickler = pickle
    with open(filename, write_mode) as o:
        try:
            pickler.dump(args, o)
        except TypeError as e:
            print("Unpicklable object!")
            print(e)


def dump_function_input_for_test(output_directory: Union[str, Callable[[str, Callable], str]] = None,
                                 capture_output: bool = False, include_module_in_path: bool = True,
                                 custom_pickler=None, save_extension: str = '.pkl', write_mode: str = 'bw',
                                 custom_save_output_func: Optional[Callable[[str, Any], Any]] = None):
    """

    Args:
        output_directory: Output directory of fixture
        capture_output: Capture output of function as well
        include_module_in_path: When using the default path scheme, should the module path be part of the
            destination name
        custom_pickler: When using default save function, do you want to use a custom pickler or alternative like json
        save_extension: Save extension. Default to '.pkl'
        custom_save_output_func: Custom save function

    Examples:
        Using with a class:
        ```
        class Experiment

            @classmethod
            @dump_function_input_for_test()
            def save(cls)
                pass

            @dump_function_input_for_test()
            def normal_funct(self, a):
                pass
        ```
    Returns:

    """
    # if no output directory, set to fixture path
    if output_directory is None:
        output_directory = COMMON_INPUT_PATH

    def decorate(func):
        # create directory for function output
        # if we have a function for directory naming, call it
        if callable(output_directory):
            out = output_directory(COMMON_INPUT_PATH, func)
        else:
            fname = f'{func.__module__}.{func.__name__}' if include_module_in_path else func.__name__
            fname = fname.replace('.', os.path.sep)
            out = os.path.abspath(os.path.join(output_directory, fname))

        # create our paths to input/output files
        out_directory = os.path.join(out, 'output')
        input_directory = os.path.join(out, 'input')

        @wraps(func)
        def wrapper(*args, **kwargs):
            call_time = int(round(time.time() * 1000))
            # if output directory is a
            # save keywords and args to files
            os.makedirs(input_directory, exist_ok=True)
            input_file_out = os.path.join(input_directory, f'{call_time}{save_extension}')
            if custom_save_output_func:
                custom_save_output_func(input_file_out, (args, kwargs))
            else:
                default_fixture_pickle_save(input_file_out, (args, kwargs), custom_pickler, write_mode)
            result = func(*args, **kwargs)
            if capture_output:
                os.makedirs(out_directory, exist_ok=True)
                output_file_out = os.path.join(out_directory, f'{call_time}{save_extension}')
                if custom_save_output_func:
                    custom_save_output_func(output_file_out, result)
                else:
                    default_fixture_pickle_save(output_file_out, result, custom_pickler, write_mode)
            return result

        return wrapper

    return decorate


def run_in_temp_dir(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_dir = os.getcwd()
        temp_dir = tempfile.mkdtemp()
        try:
            logger.debug(f"Running function in: {temp_dir}")
            os.chdir(temp_dir)
            func(*args, **kwargs)
        finally:
            os.chdir(current_dir)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

    return wrapper


def warn_amount_ssmt_image_decorator(func):
    """
    A decorator to warn developers about possible failures due to SSMT.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                "These tests can fail due to changes to idmtools-core, idmtools-models, or idmtools-platform-comps. "
                "If you have changed the code in those libraries, you will need to build a new ssmt image, publish to staging,"
                "then update idmtools_platform_comps/tests/idmtools.ini by uncommenting the 'docker_image' options. You should"
                "change the value to the new version of the SSMT image. COMPS Will automatically pull the new image."
            )
            raise e

    return wrapper
