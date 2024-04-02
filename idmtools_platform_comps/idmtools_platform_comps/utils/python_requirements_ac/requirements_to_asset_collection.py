"""idmtools requirements to asset collection.

This is the entry point for users to use RequirementsToAssetCollection tool.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import hashlib
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from typing import List
from packaging.requirements import Requirement
from COMPS.Data import QueryCriteria
from COMPS.Data.AssetCollection import AssetCollection as COMPSAssetCollection
from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.comps_platform import COMPSPlatform, SLURM_ENVS
from idmtools_platform_comps.utils.package_version import get_highest_version

CURRENT_DIRECTORY = os.path.dirname(__file__)
REQUIREMENT_FILE = 'requirements_updated.txt'
MODEL_LOAD_LIB = "install_requirements.py"
MODEL_CREATE_AC = 'create_asset_collection.py'
MD5_KEY = 'idmtools-requirements-md5-{}'
logger = getLogger(__name__)
user_logger = getLogger("user")


@dataclass(repr=False)
class RequirementsToAssetCollection:
    """
    RequirementsToAssetCollection provides a utility to install python packages into an asset collection.

    Notes:
        - TODO - Incorporate example in this docs
    """
    #: Platform object
    platform: COMPSPlatform = field(default=None)
    #: Name of experiment when installing requirements
    name: str = field(default="install custom requirements")
    #: Path to requirements file
    requirements_path: str = field(default=None)
    #: list of packages
    pkg_list: list = field(default=None)
    #: list of wheel files locally to upload and install
    local_wheels: list = field(default=None)
    # User tags
    asset_tags: dict = field(default=None)
    #: Internal checksum to calculate unique requirements set has be ran before
    _checksum: str = field(default=None, init=False)
    #: Calculated requirements including versions
    _requirements: List[str] = field(default=None, init=False)
    #: Since requirements vary by os, target it on the platform as well
    _os_target: str = field(default=None, init=False)
    #: Reserved tags
    __reserved_tag: list = field(default=None, init=False)

    def __post_init__(self):
        """
        Constructor.

        Raises:
            ValueError - if  requirements_path, pkg_list, and local_wheels are empty.
        """
        if not any([self.requirements_path, self.pkg_list, self.local_wheels]):
            raise ValueError("Impossible to proceed without either requirements path or package list or local wheels!")

        self.requirements_path = os.path.abspath(self.requirements_path) if self.requirements_path else None
        self.pkg_list = self.pkg_list or []
        self.local_wheels = [os.path.abspath(whl) for whl in self.local_wheels] if self.local_wheels else []
        self.asset_tags = self.asset_tags or {}

    @property
    def checksum(self):
        """
        Calculate checksum on the requirements file.

        Returns:
            The md5 of the requirements.
        """
        if not self._checksum:
            req_content = '\n'.join(self.requirements)
            self._checksum = hashlib.md5(req_content.encode('utf-8')).hexdigest()

        return self._checksum

    @property
    def md5_tag(self):
        """
        Get unique key for our requirements + target.

        Returns:
            The md5 tag.
        """
        self.init_platform()
        return {MD5_KEY.format(self._os_target): self.checksum}

    @property
    def requirements(self):
        """
        Requirements property. We calculate this using consolidate_requirements.

        Returns:
            Consolidated requirements.
        """
        if not self._requirements:
            self._requirements = self.consolidate_requirements()

        return self._requirements

    def init_platform(self):
        """Initialize the platform."""
        if self.platform is None:
            # Try to detect platform
            from idmtools.core.context import get_current_platform
            p = get_current_platform()
            if p is not None:
                self.platform = p

        self._os_target = "win" if "slurm" not in self.platform.environment.lower() and self.platform.environment.lower() not in SLURM_ENVS else "linux"
        self.__reserved_tag = ['idmtools', 'task_type', MD5_KEY.format(self._os_target)]

    def run(self, rerun=False):
        """
        Run our utility.

        The working logic of this utility:
            1. check if asset collection exists for given requirements, return ac id if exists
            2. create an Experiment to install the requirements on COMPS
            3. create a WorkItem to create a Asset Collection

        Returns: return ac id based on the requirements if Experiment and WorkItem Succeeded

        Raises:
            Exception - If an error happens on workitem

        Notes:
            - TODO The exceptions here should be rewritten to parse errors from remote system like AssetizeOutputs
        """
        # Late validation
        self.init_platform()

        # Check if ac with md5 exists
        ac = self.retrieve_ac_by_tag()

        if ac and not rerun:
            return ac.id

        # Create Experiment to install custom requirements
        exp = self.run_experiment_to_install_lib()
        if exp is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug('Failed to install requirements!')
            raise Exception('Failed to install requirements!')

        if logger.isEnabledFor(DEBUG):
            logger.debug(f'\nexp: {exp.uid}')

        # Create a WorkItem to create asset collection
        wi = self.run_wi_to_create_ac(exp.uid)
        if wi is None:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Failed to create asset collection from experiment: {exp.uid}')
            raise Exception(f'Failed to create asset collection from experiment: {exp.uid}')

        if logger.isEnabledFor(DEBUG):
            logger.debug(f'\nwi: {wi.uid}')

        # get ac or return ad_id
        ac = self.retrieve_ac_from_wi(wi)

        if ac:
            return ac.id

    def save_updated_requirements(self):
        """
        Save consolidated requirements to a file requirements_updated.txt.

        Returns:
            None
        """
        user_logger.info(
            f"Creating an updated requirements file ensuring all versions are specified at {REQUIREMENT_FILE}")
        req_content = '\n'.join(self.requirements)
        with open(REQUIREMENT_FILE, 'w') as outfile:
            outfile.write(req_content)

    def retrieve_ac_by_tag(self, md5_check=None):
        """
        Retrieve comps asset collection given ac tag.

        Args:
            md5_check: also can use custom md5 string as search tag
        Returns: comps asset collection
        """
        # Late validation
        self.init_platform()

        md5_str = md5_check or self.checksum
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'md5_str: {md5_str}')

        # check if ac with tag idmtools-requirements-md5 = my_md5 exists
        ac_list = COMPSAssetCollection.get(
            query_criteria=QueryCriteria().select_children('tags').where_tag(
                [f'{MD5_KEY.format(self._os_target)}={md5_str}']))

        # if exists, get ac and return it
        if len(ac_list) > 0:
            ac_list = sorted(ac_list, key=lambda t: t.date_created, reverse=True)
            user_logger.info(f"Found existing requirements assets at {ac_list[0].id}")
            return ac_list[0]

    def retrieve_ac_from_wi(self, wi):
        """
        Retrieve ac id from file ac_info.txt saved by WI.

        Args:
            wi: SSMTWorkItem (which was used to create ac from library)
        Returns: COMPS asset collection
        """
        ac_file = "ac_info.txt"

        # retrieve ac file
        ret = self.platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, [ac_file])

        # get file content
        ac_id_bytes = ret[ac_file]

        # convert bytes to string
        ac_id_str = ac_id_bytes.decode('utf-8')

        # return comps ac
        return self.platform.get_item(ac_id_str, ItemType.ASSETCOLLECTION, raw=True)

    def add_wheels_to_assets(self, experiment):
        """
        Add wheels to assets of our experiment.

        Args:
            experiment: Experiment to add assets to

        Returns:
            None
        """
        for whl in self.local_wheels:
            a = Asset(filename=os.path.basename(whl), absolute_path=whl)
            experiment.add_asset(a)

    def run_experiment_to_install_lib(self):
        """
        Create an Experiment which will run another py script to install requirements.

        Returns: Experiment created
        """
        self.save_updated_requirements()

        task = JSONConfiguredPythonTask(script_path=os.path.join(CURRENT_DIRECTORY, MODEL_LOAD_LIB))
        experiment = Experiment(name=self.name, simulations=[task.to_simulation()])
        experiment.add_asset(Asset(REQUIREMENT_FILE))
        experiment.tags = self.md5_tag

        # Avoid conflict to reserved tag
        if len(set(self.asset_tags).intersection(self.__reserved_tag)) > 0:
            raise Exception(f"{self.__reserved_tag} are reserved tags, please use other tags!")

        # Remove conflicts in case
        for tag in self.__reserved_tag:
            self.asset_tags.pop(tag, None)

        # Update experiment's tags
        experiment.tags.update(self.asset_tags)

        self.add_wheels_to_assets(experiment)
        user_logger.info("Run install of python requirements on COMPS. To view the details, see the experiment below")
        experiment.run(wait_until_done=True, platform=self.platform, use_short_path=True, num_cores=1)

        if experiment.succeeded:
            return experiment

    def run_wi_to_create_ac(self, exp_id):
        """
        Create an WorkItem which will run another py script to create new asset collection.

        Args:
            exp_id: the Experiment id (which installed requirements)
        Returns: work item created
        """
        from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

        md5_str = self.checksum
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'md5_str: {md5_str}')

        wi_name = "wi to create ac"
        command = f"python3 {MODEL_CREATE_AC} {exp_id} {self.platform.endpoint} {self._os_target}"

        # Update tags
        tags = {MD5_KEY.format(self._os_target): self.checksum}
        tags.update(self.asset_tags)

        user_logger.info(
            "Converting Python Packages to an Asset Collection. This may take some time for large dependency lists")
        wi = SSMTWorkItem(name=wi_name, command=command,
                          transient_assets=AssetCollection([os.path.join(CURRENT_DIRECTORY, MODEL_CREATE_AC)]),
                          tags=tags, related_experiments=[exp_id])

        wi.run(wait_until_done=True, platform=self.platform)

        if wi.succeeded:
            # make ac as related_asset_collection to wi
            from COMPS.Data.WorkItem import RelationType
            comps_ac = self.retrieve_ac_from_wi(wi)
            comps_wi = self.platform.get_item(wi.uid, ItemType.WORKFLOW_ITEM, raw=True)
            comps_wi.add_related_asset_collection(comps_ac.id, relation_type=RelationType.Created)
            comps_wi.save()
            return wi
        else:
            user_logger.warning("Work item failed. See logs")
            try:
                files = self.platform.get_files_by_id(wi.uid, wi.item_type, ["stderr.txt"])
                user_logger.error(f'Server Error Log: {files["stderr.txt"].decode("utf-8")}')
            except:  # noqa: E722
                pass

    def consolidate_requirements(self):
        """
        Combine requirements and dynamic requirements (a list).

        We do the following:
          - get the latest version of package if version is not provided
          - dynamic requirements will overwrites the requirements file

        Returns: the consolidated requirements (as a list)
        """
        req_dict = {}
        comment_list = []

        if self.requirements_path:
            with open(self.requirements_path, 'r') as fd:
                for _cnt, line in enumerate(fd):
                    line = line.strip()
                    if line == '':
                        continue

                    if line.startswith('#'):
                        comment_list.append(line)
                        continue

                    req = Requirement(line)
                    req_dict[req.name] = req.specifier

        # pkg_list will overwrite pkg in requirement file
        if self.pkg_list:
            for pkg in self.pkg_list:
                req = Requirement(pkg)
                req_dict[req.name] = req.specifier

        req_list = []
        for k, v in req_dict.items():
            pkg_requirement = f'{k}{str(v)}'
            req_list.append(f'{k}=={get_highest_version(pkg_requirement)}')

        wheel_list = []
        if self.local_wheels:
            wheel_list.extend([f"Assets/{os.path.basename(whl)}" for whl in self.local_wheels])

        req_list = sorted(req_list, reverse=False)
        wheel_list = sorted(wheel_list, reverse=False)
        update_req_list = req_list + wheel_list

        return update_req_list
