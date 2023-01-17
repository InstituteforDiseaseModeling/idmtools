"""
idmtools slurm cli comands.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import click
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
