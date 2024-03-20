"""idmtools singularity build workitem.

Notes:
    - TODO add examples here.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import hashlib
import io
import json
import os
import re
import uuid
from dataclasses import dataclass, field, InitVar
from logging import getLogger, DEBUG
from os import PathLike
from pathlib import PurePath
from typing import List, Dict, Union, Optional, TYPE_CHECKING
from urllib.parse import urlparse
from uuid import UUID
from COMPS.Data import QueryCriteria
from jinja2 import Environment
from idmtools import IdmConfigParser
from idmtools.assets import AssetCollection, Asset
from idmtools.assets.file_list import FileList
from idmtools.core import EntityStatus, NoPlatformException
from idmtools.core.logging import SUCCESS
from idmtools.entities.command_task import CommandTask
from idmtools.entities.relation_type import RelationType
from idmtools.utils.hashing import calculate_md5_stream
from idmtools_platform_comps.ssmt_work_items.comps_workitems import InputDataWorkItem
from idmtools_platform_comps.utils.general import save_sif_asset_md5_from_ac_id
from idmtools_platform_comps.utils.package_version import get_docker_manifest, get_digest_from_docker_hub

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform

SB_BASE_WORKER_PATH = os.path.join(os.path.dirname(__file__), 'base_singularity_work_order.json')

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass(repr=False)
class SingularityBuildWorkItem(InputDataWorkItem):
    """
    Provides a wrapper to build utilizing the COMPS build server.

    Notes:
        - TODO add references to examples
    """
    #: Path to definition file
    definition_file: Union[PathLike, str] = field(default=None)
    #: definition content. Alternative to file
    definition_content: str = field(default=None)
    #: Enables Jinja parsing of the definition file or content
    is_template: bool = field(default=False)
    #: template_args
    template_args: Dict[str, str] = field(default_factory=dict)
    #: Image Url
    image_url: InitVar[str] = None
    #: Destination image name
    image_name: str = field(default=None)
    #: Name of the workitem
    name: str = field(default=None)
    #: Tages to add to container asset collection
    image_tags: Dict[str, str] = field(default_factory=dict)
    #: Allows you to set a different library. (The default library is “https://library.sylabs.io”). See https://sylabs.io/guides/3.5/user-guide/cli/singularity_build.html
    library: str = field(default=None)
    #: only run specific section(s) of definition file (setup, post, files, environment, test, labels, none) (default [all])
    section: List[str] = field(default_factory=lambda: ['all'])
    #: build using user namespace to fake root user (requires a privileged installation)
    fix_permissions: bool = field(default=False)
    # AssetCollection created by build
    asset_collection: AssetCollection = field(default=None)
    #: Additional Mounts
    additional_mounts: List[str] = field(default_factory=list)
    #: Environment vars for remote build
    environment_variables: Dict[str, str] = field(default_factory=dict)
    #: Force build
    force: bool = field(default=False)
    #: Don't include default tags
    disable_default_tags: bool = field(default=None)
    # ID that is added to work item and then results collection that can be used to tied the items together
    run_id: uuid.UUID = field(default_factory=uuid.uuid4)

    #: loaded if url is docker://. Used to determine if we need to re-run a build
    __digest: Dict[str, str] = field(default=None)
    __image_tag: str = field(default=None)

    #: rendered template. We have to store so it is calculated before RUN which means outside our normal pre-create hooks
    __rendered_template: str = field(default=None)

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, image_url: str):
        """Constructor."""
        self.work_item_type = 'ImageBuilderWorker'
        self._image_url = None
        # Set this for now. Later it should be replace with some type of Specialized worker identifier
        self.task = CommandTask("ImageBuilderWorker")
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)

        self.image_url = image_url if isinstance(image_url, str) else None
        if isinstance(self.definition_file, PathLike):
            self.definition_file = str(self.definition_file)

    def get_container_info(self) -> Dict[str, str]:
        """Get container info.

        Notes:
            - TODO remove this
        """
        pass

    @property
    def image_url(self):  # noqa: F811
        """Get the image url."""
        return self._image_url

    @image_url.setter
    def image_url(self, value: str):
        """
        Set the image url.

        Args:
            value: Value to set value to

        Returns:
            None
        """
        url_info = urlparse(value)
        if url_info.scheme == "docker":
            if "packages.idmod.org" in value:
                full_manifest, self.__image_tag = get_docker_manifest(url_info.path)
                self.__digest = full_manifest['config']['digest']
            else:
                self.__image_tag = url_info.netloc + ":latest" if ":" not in value else url_info.netloc
                image, tag = url_info.netloc.split(":")
                self.__digest = get_digest_from_docker_hub(image, tag)
            if self.fix_permissions:
                self.__digest += "--fix-perms"
            if self.name is None:
                self.name = f"Load Singularity image from Docker {self.__image_tag}"
        # TODO how to do this for shub
        self._image_url = value

    def context_checksum(self) -> str:
        """
        Calculate the context checksum of a singularity build.

        The context is the checksum of all the assets defined for input, the singularity definition file, and the environment variables

        Returns:
            Conext checksum.
        """
        file_hash = hashlib.sha256()
        # ensure our template is set
        self.__add_common_assets()
        for asset in sorted(self.assets + self.transient_assets, key=lambda a: a.short_remote_path()):
            if asset.absolute_path:
                with open(asset.absolute_path, mode='rb') as ain:
                    calculate_md5_stream(ain, file_hash=file_hash)
            else:
                self.__add_file_to_context(json.dumps([asset.filename, asset.relative_path, str(asset.checksum)], sort_keys=True) if asset.persisted else asset.bytes, file_hash)

        if len(self.environment_variables):
            contents = json.dumps(self.environment_variables, sort_keys=True)
            self.__add_file_to_context(contents, file_hash)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Context: sha256:{file_hash.hexdigest()}')
        return f'sha256:{file_hash.hexdigest()}'

    def __add_file_to_context(self, contents: Union[str, bytes], file_hash):
        """
        Add a specific file content to context checksum.

        Args:
            contents: Contents
            file_hash: File hash to add to

        Returns:
            None
        """
        item = io.BytesIO()
        item.write(contents.encode('utf-8') if isinstance(contents, str) else contents)
        item.seek(0)
        calculate_md5_stream(item, file_hash=file_hash)

    def render_template(self) -> Optional[str]:
        """
        Render template. Only applies when is_template is True. When true, it renders the template using Jinja to a cache value.

        Returns:
            Rendered Template
        """
        if self.is_template:
            # We don't allow re-running template rendering
            if self.__rendered_template is None:
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Rendering template")
                contents = None
                # try from file first
                if self.definition_file:
                    with open(self.definition_file, mode='r') as ain:
                        contents = ain.read()
                elif self.definition_content:
                    contents = self.definition_content

                if contents:
                    env = Environment()
                    template = env.from_string(contents)
                    self.__rendered_template = template.render(env=os.environ, sbi=self, **self.template_args)
            return self.__rendered_template
        return None

    @staticmethod
    def find_existing_container(sbi: 'SingularityBuildWorkItem', platform: 'IPlatform' = None) -> Optional[AssetCollection]:
        """
        Find existing container.

        Args:
            sbi: SingularityBuildWorkItem to find existing container matching config
            platform: Platform To load the object from

        Returns:
            Existing Asset Collection
        """
        if platform is None:
            from idmtools.core.context import CURRENT_PLATFORM
            if CURRENT_PLATFORM is None:
                raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
            platform = CURRENT_PLATFORM
        ac = None
        if not sbi.force:  # don't search if it is going to be forced
            qc = QueryCriteria().where_tag(['type=singularity']).select_children(['assets', 'tags']).orderby('date_created desc')
            if sbi.__digest:
                qc.where_tag([f'digest={sbi.__digest}'])
            elif sbi.definition_file or sbi.definition_content:
                qc.where_tag([f'build_context={sbi.context_checksum()}'])
            if len(qc.tag_filters) > 1:
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Searching for existing containers")
                ac = platform._assets.get(None, query_criteria=qc)
            if ac:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Found: {len(ac)} previous builds")
                ac = platform._assets.to_entity(ac[0])
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f'Found existing container in {ac.id}')
            else:
                ac = None

        return ac

    def __add_tags(self):
        """
        Add default tags to the asset collection to be created.

        The most important part of this logic is the digest/run_id information we add. This is what enables the build/pull-cache through comps.

        Returns:
            None
        """
        self.image_tags['type'] = 'singularity'
        # Disable all tags but image name and type
        if not self.disable_default_tags:
            if self.platform is not None and hasattr(self.platform, 'get_username'):
                self.image_tags['created_by'] = self.platform.get_username()
            # allow users to override run id using only the tag
            if 'run_id' in self.tags:
                self.run_id = self.tags['run_id']
            else:
                # set the run id on the workitem and resulting tags
                self.tags['run_id'] = str(self.run_id)
            self.image_tags['run_id'] = self.tags['run_id']
            # Check for the digest
            if self.__digest and isinstance(self.__digest, str):
                self.image_tags['digest'] = self.__digest
                self.image_tags['image_from'] = self.__image_tag
                if self.image_name is None:
                    self.image_name = self.__image_tag.strip(" /").replace(":", "_").replace("/", "_") + ".sif"
            # If we are building from a file, add the build context
            elif self.definition_file:
                self.image_tags['build_context'] = self.context_checksum()
                if self.image_name is None:
                    bn = PurePath(self.definition_file).name
                    bn = str(bn).replace(".def", ".sif")
                    self.image_name = bn
            elif self.definition_content:
                self.image_tags['build_context'] = self.context_checksum()
            if self.image_url:
                self.image_tags['image_url'] = self.image_url

        # Final fall back for image name
        if self.image_name is None:
            self.image_name = "image.sif"
        if self.image_name and not self.image_name.endswith(".sif"):
            self.image_name = f'{self.image_name}.sif'
        # Add image name to the tags
        self.image_tags['image_name'] = self.image_name

    def _prep_work_order_before_create(self) -> Dict[str, str]:
        """
        Prep work order before creation.

        Returns:
            Workorder for singularity build.
        """
        self.__add_tags()
        self.load_work_order(SB_BASE_WORKER_PATH)
        if self.definition_file or self.definition_content:
            self.work_order['Build']['Input'] = "Assets/Singularity.def"
        else:
            self.work_order['Build']['Input'] = self.image_url
        if len(self.environment_variables):
            self.work_order['Build']['StaticEnvironment'] = self.environment_variables
        if len(self.additional_mounts):
            self.work_order['Build']['AdditionalMounts'] = self.additional_mounts
        self.work_order['Build']['Output'] = self.image_name if self.image_name else "image.sif"
        self.work_order['Build']['Tags'] = self.image_tags
        self.work_order['Build']['Flags'] = dict()
        if self.fix_permissions:
            self.work_order['Build']['Flags']['Switches'] = ["--fix-perms"]
        if self.library:
            self.work_order['Build']['Flags']['--library'] = self.library
        if self.section:
            self.work_order['Build']['Flags']['--section'] = self.section
        return self.work_order

    def pre_creation(self, platform: 'IPlatform') -> None:
        """
        Pre-Creation item.

        Args:
            platform: Platform object

        Returns:
            None
        """
        if self.name is None:
            self.name = "Singularity Build"
            if self.definition_file:
                self.name += f" of {PurePath(self.definition_file).name}"
        super(SingularityBuildWorkItem, self).pre_creation(platform)
        self.__add_common_assets()
        self._prep_work_order_before_create()

    def __add_common_assets(self):
        """
        Add common assets which in this case is the singularity definition file.

        Returns:
            None
        """
        self.render_template()
        if self.definition_file:
            opts = dict(content=self.__rendered_template) if self.is_template else dict(absolute_path=self.definition_file)
            self.assets.add_or_replace_asset(Asset(filename="Singularity.def", **opts))
        elif self.definition_content:
            opts = dict(content=self.__rendered_template if self.is_template else self.definition_content)
            self.assets.add_or_replace_asset(Asset(filename="Singularity.def", **opts))

    def __fetch_finished_asset_collection(self, platform: 'IPlatform') -> Union[AssetCollection, None]:
        """
        Fetch the Singularity asset collection we created.

        Args:
            platform: Platform to fetch from.

        Returns:
            Asset Collection or None
        """
        comps_workitem = self.get_platform_object(force=True)
        acs = comps_workitem.get_related_asset_collections(RelationType.Created)
        if acs:
            self.asset_collection = AssetCollection.from_id(acs[0].id, platform=platform if platform else self.platform)
            if IdmConfigParser.is_output_enabled():
                user_logger.log(SUCCESS, f"Created Singularity image as Asset Collection: {self.asset_collection.id}")
                user_logger.log(SUCCESS, f"View AC at {self.platform.get_asset_collection_link(self.asset_collection)}")
            return self.asset_collection
        return None

    def run(self, wait_until_done: bool = True, platform: 'IPlatform' = None, wait_on_done_progress: bool = True, **run_opts) -> Optional[AssetCollection]:
        """
        Run the build.

        Args:
            wait_until_done: Wait until build completes
            platform: Platform to run on
            wait_on_done_progress: Show progress while waiting
            **run_opts: Extra run options

        Returns:
            Asset collection that was created if successful
        """
        p = super()._check_for_platform_from_context(platform)
        opts = dict(wait_on_done_progress=wait_on_done_progress, wait_until_done=wait_until_done, platform=p, wait_progress_desc=f"Waiting for build of Singularity container: {self.name}")
        ac = self.find_existing_container(self, platform=p)
        if ac is None or self.force:
            super().run(**opts)
            ac = self.asset_collection

        else:
            if IdmConfigParser.is_output_enabled():
                user_logger.log(SUCCESS, f"Existing build of image found with Asset Collection ID of {ac.id}")
                user_logger.log(SUCCESS, f"View AC at {self.platform.get_asset_collection_link(ac)}")
            # Set id to None
            self.uid = None
            if ac:
                self.image_tags = ac.tags
            self.asset_collection = ac
            # how do we get id for original work item from AC?
            self.status = EntityStatus.SUCCEEDED

        save_sif_asset_md5_from_ac_id(ac.id)
        return self.asset_collection

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None, platform: 'IPlatform' = None, wait_progress_desc: str = None) -> Optional[AssetCollection]:
        """
        Waits on Singularity Build Work item to finish and fetches the resulting asset collection.

        Args:
            wait_on_done_progress: When set to true, a progress bar will be shown from the item
            timeout: Timeout for waiting on item. If none, wait will be forever
            refresh_interval: How often to refresh progress
            platform: Platform
            wait_progress_desc: Wait Progress Description Text

        Returns:
            AssetCollection created if item succeeds
        """
        # wait on related items before we wait on our item
        p = super()._check_for_platform_from_context(platform)
        opts = dict(wait_on_done_progress=wait_on_done_progress, timeout=timeout, refresh_interval=refresh_interval, platform=p, wait_progress_desc=wait_progress_desc)

        super().wait(**opts)
        if self.status == EntityStatus.SUCCEEDED:
            return self.__fetch_finished_asset_collection(p)
        return None

    def get_id_filename(self, prefix: str = None) -> str:
        """
        Determine the id filename. Mostly used when use does not provide one.

        The logic is combine prefix and either
        * definition file minus extension
        * image url using with parts filtered out of the name.

        Args:
            prefix: Optional prefix.

        Returns:
            id file name

        Raises:
            ValueError - When the filename cannot be calculated
        """
        if prefix is None:
            prefix = ''
        if self.definition_file:
            base_name = PurePath(self.definition_file).name.replace(".def", ".id")
            if prefix:
                base_name = f"{prefix}{base_name}"
            filename = str(PurePath(self.definition_file).parent.joinpath(base_name))
        elif self.image_url:
            filename = re.sub(r"(docker|shub)://", "", self.image_url).replace(":", "_")
            if filename:
                filename = f"{prefix}{filename}"
        else:
            raise ValueError("Could not calculate the filename. Please specify one")
        if not filename.endswith(".id"):
            filename += ".id"

        return filename

    def to_id_file(self, filename: Union[str, PathLike] = None, save_platform: bool = False):
        """
        Create an ID File.

        If the filename is not provided, it will be calculate for definition files or for docker pulls

        Args:
            filename: Filename
            save_platform: Save Platform info to file as well

        Returns:
            None
        """
        if filename is None:
            filename = self.get_id_filename(prefix='builder.')
        super(SingularityBuildWorkItem, self).to_id_file(filename, save_platform)
