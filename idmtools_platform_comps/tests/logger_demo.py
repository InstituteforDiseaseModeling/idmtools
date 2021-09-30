import logging
from logging import getLogger


def check_logger(logger):
    if not isinstance(logger, logging.PlaceHolder):
        print(logger.name)
    if hasattr(logger, 'level'):
        print(f' - level: {logging.getLevelName(logger.level)} ({logger.level})')
        print(" - propagate: ", logger.propagate)
        print(" - effectiveLevel: ",
              f"{logging.getLevelName(logger.getEffectiveLevel())} ({logger.getEffectiveLevel()})")

    # handle AttributeError: 'PlaceHolder' object has no attribute 'handlers'
    if hasattr(logger, 'handlers'):
        hls = logger.handlers
        print(f' - handlers ({len(logger.handlers)}): ', hls)
        for h in hls:
            print('   ', h, "~~~~~", type(h))


def check_comps_logger(full: bool = False, display=False):
    root = getLogger()
    check_logger(root)
    user_logger = getLogger('user')
    check_logger(user_logger)
    comps_logger = getLogger('COMPS')
    check_logger(comps_logger)
    from COMPS.Data.Experiment import logger as exp_logger
    check_logger(exp_logger)

    comps_loggers = {}
    if full:
        for log_name, cl in root.manager.loggerDict.items():

            if log_name.startswith("COMPS"):
                comps_loggers[log_name] = cl
                check_logger(cl)

    if display:
        print('\n'.join(list(comps_loggers.keys())))


def write_some_logs(fake=False, exp=False, comps=False, root=False, user=False, full=True, check=False):
    if fake or full:
        any_logger = getLogger('any_module')
        any_logger.propagate = False
        if check:
            check_logger(any_logger)
        any_logger.debug('any_logger: 1111')
        any_logger.info('any_logger: 2222')
        any_logger.warning('any_logger: 3333')
        any_logger.error('any_logger: 4444')
        any_logger.critical('any_logger: 5555')

    if exp or full:
        from COMPS.Data.Experiment import logger as exp_logger
        if check:
            check_logger(exp_logger)
        exp_logger.debug('exp_logger: c11')
        exp_logger.info('exp_logger: c22')
        exp_logger.warning('exp_logger: c33')
        exp_logger.error('exp_logger: c44')
        exp_logger.critical('exp_logger: c55')

    if comps or full:
        comps_logger = getLogger('COMPS')
        if check:
            check_logger(comps_logger)
        comps_logger.debug('comps_logger: c1')
        comps_logger.info('comps_logger: c2')
        comps_logger.warning('comps_logger: c3')
        comps_logger.error('comps_logger: c4')
        comps_logger.critical('comps_logger: c5')

    if root or full:
        root = getLogger()
        if check:
            check_logger(root)
        root.debug('root: 1')
        root.info('root: 2')
        root.warning('root: 3')
        root.error('root: 4')
        root.critical('root: 5')

    if user or full:
        user_logger = getLogger('user')
        if check:
            check_logger(user_logger)
        user_logger.debug('user: 11')
        user_logger.info('user: 22')
        user_logger.warning('user: 33')
        user_logger.error('user: 44')
        user_logger.critical('user: 55')


def main():
    from idmtools.core.platform_factory import Platform
    platform = Platform('BAYESIAN')

    check_comps_logger(full=False)
    write_some_logs(user=True, root=True, comps=True, exp=True, full=False)


if __name__ == '__main__':
    main()
