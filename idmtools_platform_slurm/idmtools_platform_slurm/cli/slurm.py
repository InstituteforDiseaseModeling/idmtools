"""
idmtools slurm cli commands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
import click
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools_platform_slurm.utils.status_report.status_report import generate_status_report
from idmtools_platform_slurm.utils.status_report.utils import get_latest_experiment, check_status
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')


@click.group(short_help="Slurm platform related commands.")
@click.argument('job-directory')
@click.pass_context
def slurm(ctx: click.Context, job_directory):
    """
    Commands related to managing the SLURM platform.

    job_directory: Slurm Working Directory
    """
    ctx.obj = dict(job_directory=job_directory)


@slurm.command(help="Get simulation's report")
@click.option('--suite-id', default=None, help="Idmtools Suite id")
@click.option('--exp-id', default=None, help="Idmtools Experiment id")
@click.option('--status-filter', type=click.Choice(['0', '-1', '100']), multiple=True, help="list of status")
@click.option('--sim-filter', multiple=True, help="list of simulations")
@click.option('--job-filter', multiple=True, help="list of slurm jobs")
@click.option('--root', default='sim', type=click.Choice(['job', 'sim']), help="Dictionary root key")
@click.option('--verbose/--no-verbose', default=True, help="Enable verbose output in results")
@click.option('--display/--no-display', default=True, help="Display with working directory or not")
@click.option('--display-count', default=20, help="Display Count")
@click.pass_context
def status_report(ctx: click.Context, suite_id, exp_id, status_filter, sim_filter, job_filter, root, verbose, display,
                  display_count):
    job_dir = ctx.obj['job_directory']

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


@slurm.command(help="Get Suite/Experiment/Simulation directory")
@click.option('--sim-id', default=None, help="Idmtools Simulation id")
@click.option('--exp-id', default=None, help="Idmtools Experiment id")
@click.option('--suite-id', default=None, help="Idmtools Suite id")
@click.pass_context
def get_path(ctx: click.Context, sim_id, exp_id, suite_id):
    job_dir = ctx.obj['job_directory']
    platform = Platform('SLURM_LOCAL', job_directory=job_dir)

    if sim_id is not None:
        item_dir = platform.get_directory_by_id(sim_id, ItemType.SIMULATION)
    elif exp_id is not None:
        item_dir = platform.get_directory_by_id(exp_id, ItemType.EXPERIMENT)
    elif suite_id is not None:
        item_dir = platform.get_directory_by_id(suite_id, ItemType.SUITE)
    else:
        raise Exception('Must provide at least one: suite-id, exp-id or sim-id!')

    user_logger.info(item_dir)


@slurm.command(help="Get status of Experiment/Simulation")
@click.option('--sim-id', default=None, help="Idmtools Simulation id")
@click.option('--exp-id', default=None, help="Idmtools Experiment id")
@click.pass_context
def get_status(ctx: click.Context, sim_id, exp_id):
    job_dir = ctx.obj['job_directory']
    platform = Platform('SLURM_LOCAL', job_directory=job_dir)

    if sim_id is not None:
        status = platform._op_client.get_simulation_status(sim_id)
    elif exp_id is not None:
        exp = platform.get_item(exp_id, ItemType.EXPERIMENT)
        status = exp.status
    else:
        raise Exception('Must provide at least one: exp-id or sim-id!')

    user_logger.info(status.name if status else None)


@slurm.command(help="Get Suite/Experiment/Simulation slurm job")
@click.option('--sim-id', default=None, help="Idmtools Simulation id")
@click.option('--exp-id', default=None, help="Idmtools Experiment id")
@click.option('--suite-id', default=None, help="Idmtools Suite id")
@click.pass_context
def get_job(ctx: click.Context, sim_id, exp_id, suite_id):
    job_dir = ctx.obj['job_directory']
    platform = Platform('SLURM_LOCAL', job_directory=job_dir)

    if sim_id is not None:
        job_id = platform._op_client.get_job_id(sim_id, ItemType.SIMULATION)
    elif exp_id is not None:
        job_id = platform._op_client.get_job_id(exp_id, ItemType.EXPERIMENT)
    elif suite_id is not None:
        suite = platform.get_item(suite_id, ItemType.SUITE)
        exp_id = suite.experiments[0].id
        job_id = platform._op_client.get_job_id(exp_id, ItemType.EXPERIMENT)
    else:
        raise Exception('Must provide at least one: suite-id, exp-id or sim-id!')

    user_logger.info(job_id)


@slurm.command(help="Get the latest experiment info")
@click.pass_context
def get_latest(ctx: click.Context):
    job_dir = ctx.obj['job_directory']
    platform = Platform('SLURM_LOCAL', job_directory=job_dir)

    result = get_latest_experiment(platform)
    user_logger.info(json.dumps(result, indent=3))


@slurm.command(help="Get simulation's status")
@click.option('--exp-id', default=None, help="Idmtools Experiment id")
@click.option('--display/--no-display', default=False, help="Display with working directory or not")
@click.pass_context
def status(ctx: click.Context, exp_id, display):
    """
    Get job status.
    Args:
        ctx: click.Context
        exp_id: experiment id
        display: bool True/False
    Returns:
        None
    """
    job_dir = ctx.obj['job_directory']
    platform = Platform('SLURM_LOCAL', job_directory=job_dir)

    check_status(platform=platform, exp_id=exp_id, display=display)
