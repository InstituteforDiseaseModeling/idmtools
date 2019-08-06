import glob
import os
import shutil


def remove_artifacts():
    for pattern in ['*.py[co]', '**/*.log', ]:
        [os.remove(i) for i in glob.glob(pattern, recursive=True)]
    for pattern in ['*.egg-info/']:
        [shutil.rmtree(i) for i in [k for k in glob.glob(pattern, recursive=True) if os.path.isdir(k)]]
    for pattern in ['htmlcov', '.pytest_cache', 'dist']:
        shutil.rmtree(pattern, True)


def get_coverage_actions(docker_tests: bool = False, integration_tests: bool = False):
    setup_test_environment(docker_tests, integration_tests)
    return [
        f'cd tests && coverage run --source ../idmtools -m pytest',
        (shutil.move, ('tests/.coverage', '.coverage')),
        'coverage report -m',
        'coverage html -i',
        'python ../dev_scripts/launch_dir_in_browser.py htmlcov/index.html'
    ]


def run_tests(docker_tests: bool = False, integration_tests: bool = False):
    os.chdir('tests')
    setup_test_environment(docker_tests, integration_tests)
    return os.system('py.test -p no:warning') == 0


def setup_test_environment(docker_tests, integration_tests):
    if integration_tests:
        os.environ['COMPS_TESTS'] = '1'
    if docker_tests:
        os.environ['DOCKER_TESTS'] = '1'


def task_clean_all():
    """Delete build or temporary artifacts"""

    return dict(actions=[remove_artifacts])


def task_lint():
    """Perform python code linting"""
    return dict(actions=['flake8 --ignore=E501 idmtools_core tests'], watch=['.'])


def task_test():
    """Executes unit tests"""
    return dict(actions=[run_tests], watch=['.'], clean=[remove_artifacts])


def task_test_all():
    """Executes unit tests, dockerized tests, and integration tests"""
    return dict(actions=[(run_tests, (True, True))])


def task_coverage():
    """Executes unit tests, dockerized tests, and integration tests"""
    return dict(actions=get_coverage_actions(), targets=['.coverage', 'htmlcov'])


def task_coverage_all():
    """Executes unit tests, dockerized tests, and integration tests"""
    return dict(actions=get_coverage_actions(True, True))


def task_dist():
    return dict(actions=['python setup.py sdist'], watch=['.'], targets=['dist'], task_dep=['clean_all'])
