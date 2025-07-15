"""
Here we implement the FilePlatform suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Type, Dict, Tuple
from logging import getLogger
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools_platform_file.platform_operations.utils import FileSuite, FileExperiment

if TYPE_CHECKING:
    from idmtools_platform_file.file_platform import FilePlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class FilePlatformSuiteOperations(IPlatformSuiteOperations):
    """
    Provides Suite operation to the FilePlatform.
    """
    platform: 'FilePlatform'  # noqa F821
    platform_type: Type = field(default=FileSuite)

    def get(self, suite_id: str, **kwargs) -> FileSuite:
        """
        Get a suite from the File platform.
        Args:
            suite_id: Suite id
            kwargs: keyword arguments used to expand functionality
        Returns:
            File Suite object
        """
        metas = self.platform._metas.filter(item_type=ItemType.SUITE, property_filter={'id': str(suite_id)})
        if len(metas) > 0:
            return FileSuite(metas[0])
        else:
            raise RuntimeError(f"Not found Suite with id '{suite_id}'")

    def platform_create(self, suite: Suite, **kwargs) -> Tuple[FileSuite, str]:
        """
        Create suite on File Platform.
        Args:
            suite: idmtools suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            File Suite object created
        """
        # Generate Suite folder structure
        self.platform.mk_directory(suite)
        meta = self.platform._metas.dump(suite)

        # Return File Suite
        file_suite = FileSuite(meta)
        return file_suite, file_suite.id

    def platform_run_item(self, suite: Suite, **kwargs):
        """
        Called during commissioning of an item. This should perform what is needed to commission job on platform.
        Args:
            suite: Suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        # Refresh with entity ids
        self.platform._metas.dump(suite)

    def post_run_item(self, suite: Suite, **kwargs) -> None:
        """
        Perform post-processing steps after a suite run.
        Args:
            suite: The suite object that has just finished running
            **kwargs: Additional keyword arguments

        Returns:
            None
        """
        super().post_run_item(suite, **kwargs)
        # Refresh platform object
        suite._platform_object = self.get(suite.id, **kwargs)

    def get_parent(self, suite: FileSuite, **kwargs) -> Any:
        """
        Fetches the parent of a suite.
        Args:
            suite: File suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        return None

    def get_children(self, suite: FileSuite, parent: Suite = None, raw=True, **kwargs) -> List[Any]:
        """
        Fetch File suite's children.
        Args:
            suite: File suite
            raw: True/False
            parent: the parent of the experiments
            kwargs: keyword arguments used to expand functionality
        Returns:
            List of File experiments
        """
        exp_list = []
        exp_meta_list = self.platform._metas.get_children(suite)
        for meta in exp_meta_list:
            file_exp = FileExperiment(meta)
            if raw:
                exp_list.append(file_exp)
            else:
                exp = self.platform._experiments.to_entity(file_exp, parent=parent)
                exp_list.append(exp)
        return exp_list

    def to_entity(self, file_suite: FileSuite, children: bool = True, **kwargs) -> Suite:
        """
        Convert a FileSuite object to idmtools Suite.
        Args:
            file_suite: simulation to convert
            children: bool True/False
            kwargs: keyword arguments used to expand functionality
        Returns:
            Suite object
        """
        suite = Suite()
        suite.platform = self.platform
        suite.uid = file_suite.uid
        suite.name = file_suite.name
        suite.parent = None
        suite.tags = file_suite.tags
        suite._platform_object = file_suite
        suite.experiments = []

        if children:
            suite.experiments = self.get_children(file_suite, parent=suite, raw=False)
        return suite

    def refresh_status(self, suite: Suite, **kwargs):
        """
        Refresh the status of a suite. On comps, this is done by refreshing all experiments.
        Args:
            suite: idmtools suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        for experiment in suite.experiments:
            self.platform.refresh_status(experiment, **kwargs)

    def create_sim_directory_map(self, suite_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            suite_id: suite id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        # s = Suite.get(suite_id)
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=False, force=True)
        exps = suite.experiments
        sims_map = {}
        for exp in exps:
            d = self.platform._experiments.create_sim_directory_map(exp.id)
            sims_map = {**sims_map, **d}
        return sims_map

    def platform_delete(self, suite_id: str) -> None:
        """
        Delete platform suite.
        Args:
            suite_id: platform suite id
        Returns:
            None
        """
        try:
            suite = self.platform.get_item(suite_id, ItemType.SUITE, force=True, raw=False)
        except RuntimeError:
            return

        exps = suite.experiments
        for exp in exps:
            try:
                shutil.rmtree(self.platform.get_directory(exp))
            except RuntimeError:
                logger.info("Could not delete the associated experiment...")
                return
        try:
            shutil.rmtree(self.platform.get_directory(suite))
        except RuntimeError:
            logger.info(f"Could not delete suite ({suite_id})...")
            return

    def platform_cancel(self, suite_id: str, force: bool = False) -> None:
        """
        Cancel platform suite's file job.
        Args:
            suite_id: suite id
            force: bool, True/False
        Returns:
            None
        """
        pass

    def get_assets(self, suite: Suite, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Fetch the files associated with a suite.

        Args:
            suite: Suite (idmtools Suite or FileSuite)
            files: List of files to download
            **kwargs:

        Returns:
            Dict[str, Dict[Dict[str, Dict[str, str]]]]:
                A nested dictionary structured as:
                {
                   suite.id{
                        experiment.id: {
                            simulation.id {
                                filename: file content as string,
                                ...
                            },
                            ...
                        },
                    }
                }
        """
        ret = dict()
        if isinstance(suite, FileSuite):
            file_suite = suite
        else:
            file_suite = suite.get_platform_object()
        children = self.platform._get_children_for_platform_item(file_suite)
        for child in children:
            ret[child.id] = self.platform._experiments.get_assets(child, files, **kwargs)
        return ret
