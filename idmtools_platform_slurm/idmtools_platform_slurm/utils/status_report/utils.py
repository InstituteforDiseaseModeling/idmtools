import os
from pathlib import Path
from logging import getLogger
from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

user_logger = getLogger('user')


def get_latest_experiment(platform: 'IPlatform') -> Dict:
    """
    Find the latest experiment.
    Args:
        platform:
    Returns:
        Dictionary with experiment info
    """
    try:
        # take the last suite as the search scope
        last_suite_dir = max(Path(platform.job_directory).glob('*/'), key=os.path.getmtime)
        batch_dir = max(Path(last_suite_dir).glob('*/sbatch.sh'), key=os.path.getmtime)
        exp_dir = Path(batch_dir).parent
        exp_id = exp_dir.name
        suite_id = exp_dir.parent.name

        job_id_path = exp_dir.joinpath('job_id.txt')
        if not job_id_path.exists():
            job_id = None
        else:
            job_id = open(job_id_path).read().strip()

        r = dict(job_id=job_id, suite_id=suite_id, experiment_id=exp_id, experiment_directory=str(exp_dir),
                 job_directory=str(platform.job_directory))
        return r
    except:
        raise FileNotFoundError("Could not find the last Experiment")
