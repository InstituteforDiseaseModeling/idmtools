"""
idmtools slurm cli comands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import click
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.utils.status_report.status_report import generate_status_report
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')


@click.group(short_help="SLURM Related Commands")
@click.argument('job-directory')
@click.pass_context
def slurm(ctx: click.Context, job_directory):
    """
    Commands related to managing the SLURM platform.
    Args:
        ctx: click.Context
        job_directory: Slurm Working Directory
    Returns:
        None
    """
    ctx.obj = dict(job_directory=job_directory)


@slurm.command()
@click.option('--suite-id', default=None, help="Idmtools Suite id")
@click.option('--exp-id', default=None, help="Idmtools Experiment id")
@click.option('--status-filter', default=(), type=click.Choice(['0', '-1', '100']), multiple=True,
              help="list of status")
@click.option('--sim-filter', default=(), multiple=True, help="list of simulations")
@click.option('--job-filter', default=(), multiple=True, help="list of slurm jobs")
@click.option('--verbose', default=True, help="Verbose")
@click.option('--root', default='sim', type=click.Choice(['job', 'sim']), help="Dictionary root key")
@click.option('--display', default=True, help="Display")
@click.option('--display-count', default=20, help="Display Count")
@click.pass_context
def status_report(ctx: click.Context, suite_id=None, exp_id=None, status_filter=None, sim_filter=None, job_filter=None,
                  root='sim', verbose=True, display=True, display_count=20):
    job_dir = ctx.obj['job_directory']
    print('job_dir: ', job_dir)
    print('suite_id: ', suite_id)
    print('exp_id: ', exp_id)
    print('status_filter: ', status_filter)
    print('sim_filter: ', sim_filter)
    print('job_filter: ', job_filter)
    print('display_count: ', display_count)
    print('verbose: ', verbose)
    print('root: ', root)
    print('display: ', display)

    if suite_id is not None:
        scope = (suite_id, ItemType.SUITE)
    elif exp_id is not None:
        scope = (exp_id, ItemType.EXPERIMENT)
    else:
        scope = None

    platform = Platform('SLURM_LOCAL', job_directory=job_dir)

    generate_status_report(platform=platform, scope=scope,
                           status_filter=status_filter if len(status_filter) > 0 else None,
                           job_filter=job_filter if len(job_filter) > 0 else None,
                           sim_filter=sim_filter if len(sim_filter) > 0 else None,
                           root=root, verbose=verbose, display=display, display_count=display_count)
