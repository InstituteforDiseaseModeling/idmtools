from idmtools_platform_local.status import Status


def create_test_data():
    from idmtools_platform_local.internals.workers.utils import create_or_update_status

    # this experiment has no children
    create_or_update_status('AAAAA', '/data/AAAAA', dict(a='b', c='d'),
                            extra_details=dict(simulation_type='Python'))
    # Experiment
    create_or_update_status('BBBBB', '/data/BBBBB', dict(e='f', g='h'),
                            extra_details=dict(simulation_type='Python'))
    # Simulation
    create_or_update_status('CCCCC', '/data/CCCCC', dict(i='j', k='l'), parent_uuid='BBBBB',
                            extra_details=dict(simulation_type='Python'))
    # Experiment
    create_or_update_status('DDDDD', '/data/DDDD', dict(e='f', c='d'),
                            extra_details=dict(simulation_type='Python'))

    # Simulation
    create_or_update_status('EEEEE', '/data/EEEEE', dict(i='j', k='l'), parent_uuid='DDDDD',
                            status=Status.done,
                            extra_details=dict(simulation_type='Python'))
    create_or_update_status('FFFFF', '/data/FFFFF', dict(i='j', k='l'), parent_uuid='DDDDD',
                            status=Status.done,
                            extra_details=dict(simulation_type='Python'))
