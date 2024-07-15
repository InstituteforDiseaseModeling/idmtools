"""
idmtools ContainerPlatform JobHistory Utility.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import diskcache
from pathlib import Path
from datetime import datetime
from typing import NoReturn, Dict, Tuple, List
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools_platform_container.utils.general import normalize_path, is_valid_uuid
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')

JOB_HISTORY_DIR = "idmtools_container_history"


def initialize():
    """
    Initialization decorator for JobHistory.
    Returns:
        Wrapper function
    """

    def wrap(func):
        def wrapped_f(*args, **kwargs):
            JobHistory.initialization()
            value = func(*args, **kwargs)
            return value

        return wrapped_f

    return wrap


class JobHistory:
    """Job History Utility for idmtools Container Platform."""
    history = None
    history_path = Path.home().joinpath(".idmtools").joinpath(JOB_HISTORY_DIR)

    @classmethod
    def initialization(cls):
        """Initialize JobHistory."""
        if cls.history is None:
            cls.history_path.mkdir(parents=True, exist_ok=True)
            cls.history = diskcache.Cache(str(cls.history_path))

    @classmethod
    @initialize()
    def save_job(cls, job_dir: str, container_id: str, experiment: Experiment, platform=None) -> NoReturn:
        """
        Save job to history.
        Args:
            job_dir: job directory
            container_id: container id
            experiment: Experiment
            platform: Platform
        Returns:
            NoReturn
        """
        cache = cls.history

        from idmtools.core.context import get_current_platform
        if platform is None:
            platform = get_current_platform()

        # Get current datetime
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_item = {"JOB_DIRECTORY": normalize_path(job_dir),
                    "SUITE_ID": experiment.parent_id,
                    "EXPERIMENT_DIR": normalize_path(platform.get_directory(experiment)),
                    "EXPERIMENT_NAME": experiment.name,
                    "EXPERIMENT_ID": experiment.id,
                    "CONTAINER": container_id,
                    "CREATED": current_datetime}
        cache.set(experiment.id, new_item)
        cache.close()

    @classmethod
    @initialize()
    def get_job(cls, exp_id: str) -> Dict:
        """
        Get job from history.
        Args:
            exp_id: Experiment ID
        Returns:
            job data in dict
        """
        if not is_valid_uuid(exp_id):
            return None

        cache = cls.history
        value, expire_time = cache.get(exp_id, expire_time=True)
        if value is None:
            if exp_id in list(cache):
                user_logger.info(f"Item {exp_id} expired.")
            else:
                user_logger.info(f"Item {exp_id} not found.")
        else:
            local_expire_time = datetime.fromtimestamp(expire_time) if expire_time else None
            expire_time_str = local_expire_time.strftime('%Y-%m-%d %H:%M:%S') if local_expire_time else None
            if expire_time_str:
                value['EXPIRE'] = expire_time_str

        return value

    @classmethod
    def get_job_dir(cls, exp_id: str) -> str:
        """
        Get job directory from history.
        Args:
            exp_id: Experiment ID
        Returns:
            job directory
        """
        if not is_valid_uuid(exp_id):
            user_logger.info(f"Invalid item id: {exp_id}")
            return None

        data = cls.get_job(exp_id)
        if data is None:
            return None
        return data['JOB_DIRECTORY']

    @classmethod
    @initialize()
    def get_item_path(cls, item_id: str) -> Tuple:
        """
        Get item path from history.
        Args:
            item_id: Suite/Experiment/Simulation ID
        Returns:
            item path, item type
        """
        if not is_valid_uuid(item_id):
            logger.debug(f"Invalid item id: {item_id}")
            return

        cache = JobHistory.history
        item = cache.get(item_id)

        # Consider Experiment case
        if item:
            return Path(item['EXPERIMENT_DIR']), ItemType.EXPERIMENT

        for key in cache:
            value = cache.get(key)
            suite_id = value.get('SUITE_ID')
            exp_dir = value.get('EXPERIMENT_DIR')

            # Consider Suite case
            if suite_id == item_id:
                return Path(exp_dir).parent, ItemType.SUITE

            # Consider Simulation case
            pattern = f'*{item_id}/metadata.json'
            for meta_file in Path(exp_dir).glob(pattern=pattern):
                sim_dir = meta_file.parent
                return sim_dir, ItemType.SIMULATION

        return None

    @classmethod
    @initialize()
    def view_history(cls, container_id: str = None, limit: int = 10) -> List:
        """
        View job history.
        Args:
            container_id: Container ID
            limit: number of jobs to view
        Returns:
            list of job data
        """
        cache = cls.history
        data = []
        for key in cache:
            value, expire_time = cache.get(key, expire_time=True)
            if value is None:
                if key in list(cache):
                    user_logger.info(f"Item {key} expired.")
                else:
                    user_logger.info(f"Item {key} not found.")
                continue

            local_expire_time = datetime.fromtimestamp(expire_time) if expire_time else None
            expire_time_str = local_expire_time.strftime('%Y-%m-%d %H:%M:%S') if local_expire_time else None
            if expire_time_str:
                value['EXPIRE'] = expire_time_str

            if container_id is not None:
                if value['CONTAINER'] == container_id:
                    data.append(value)
            else:
                data.append(value)

        # Sort data by datetime
        sorted_data = sorted(data, key=lambda x: datetime.strptime(x["CREATED"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        return sorted_data[0:limit]

    @classmethod
    @initialize()
    def delete(cls, exp_id: str) -> NoReturn:
        """
        Delete job from history.
        Args:
            exp_id: Experiment ID
        Returns:
            NoReturn
        """
        cache = cls.history
        cache.pop(exp_id)
        cache.close()

    @classmethod
    @initialize()
    def expire_history(cls, dt: str = None) -> NoReturn:
        """
        Expire job history based on the input expiration time.
        Args:
            dt: datetime to expire (format like "2024-07-30 15:12:05")
        Returns:
            NoReturn
        """
        from datetime import datetime
        # Parse the datetime string into a datetime object
        dt_object = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') if dt else None

        # Convert the datetime object to a timestamp (seconds since epoch)
        timestamp = dt_object.timestamp() if dt_object else None

        cache = cls.history
        cache.expire(now=timestamp)
        cache.close()

    @classmethod
    @initialize()
    def clear(cls, container_id: str = None) -> NoReturn:
        """
        Clear job history.
        Args:
            container_id: Container ID
        Returns:
            NoReturn
        """
        cache = cls.history
        if container_id is None:
            cache.clear()
        else:
            for key in cache:
                value = cache.get(key)
                if value is None:
                    user_logger.info(f"key {key} not found in cache")
                    continue
                if value['CONTAINER'] == container_id:
                    cache.delete(key)

        cache.close()

    @classmethod
    @initialize()
    def volume(cls) -> NoReturn:
        """Clear job history."""
        cache = cls.history
        return cache.volume()

    @classmethod
    @initialize()
    def sync(cls) -> NoReturn:
        """Sync job history."""
        cache = cls.history

        for key in cache:
            values = cache.get(key)
            exp_dir = values.get('EXPERIMENT_ID')

            root = Path(exp_dir)
            if not root.exists():
                cache.pop(key)
                logger.debug(f"Remove job {key} from job history.")

        cache.close()

    @classmethod
    @initialize()
    def count(cls, container_id: str = None) -> int:
        """
        Count job history.
        Args:
            container_id: Container ID
        Returns:
            job history count
        """
        if container_id is None:
            return len(cls.history)
        else:
            jobs = [key for key in cls.history if cls.history[key]['CONTAINER'] == container_id]
            return len(jobs)

    @classmethod
    @initialize()
    def container_history(cls) -> List:
        """List of job containers."""
        cache = cls.history
        data = {}

        for key in cache:
            value = cache[key]
            container_id = value['CONTAINER']
            if container_id not in data:
                data[container_id] = []
            data[container_id].append(key)

        return data

    @classmethod
    @initialize()
    def verify_container(cls, container_id) -> bool:
        """Verify history container."""
        cache = cls.history

        for key in cache:
            value = cache[key]
            if container_id.startswith(value['CONTAINER']):
                return True
        return False
