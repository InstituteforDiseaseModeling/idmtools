import os
import platform
import time
import unittest
from functools import wraps
from typing import Callable, Union, Any, Optional

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
from idmtools_test import COMMON_INPUT_PATH

linux_only = unittest.skipIf(
    not platform.system() in ["Linux", "Darwin"], 'No Tests that are meant for linux'
)

windows_only = unittest.skipIf(
    platform.system() in ["Linux", "Darwin"], 'No Tests that are meant for Windows'
)

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


def restart_local_platform(silent=True, stop_before=True, stop_after=True, dump_logs=True, *args, **kwargs):
    global client
    if client is None:
        import docker
        client = docker.from_env()
    from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager
    from idmtools_platform_local.infrastructure.docker_io import DockerIO
    from idmtools_platform_local.cli.utils import get_service_info
    # disable spinner
    if silent:
        os.environ['NO_SPINNER'] = '1'

    args = (client,) + args
    sm = DockerServiceManager(*args, **kwargs)
    do = DockerIO()

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if stop_before:
                sm.cleanup(tear_down_brokers=True, delete_data=True)
                do.cleanup(True)
            result = None
            try:
                result = func(*args, **kwargs)
            except Exception:
                raise
            finally:
                if dump_logs:
                    try:
                        info = get_service_info(sm, diff=False, logs=True)
                        print(info)
                    except:  # noqa E722
                        pass
                if stop_after and os.getenv('NO_TEST_WORKER_CLEANUP', '0').lower() not in ['1', 'true', 'yes', 'y']:
                    sm.cleanup(tear_down_brokers=True, delete_data=True)
                    do.cleanup(True)
            return result

        return wrapper

    return decorate


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
