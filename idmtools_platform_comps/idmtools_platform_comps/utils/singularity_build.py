from dataclasses import dataclass, field, InitVar
from typing import List, Dict
from urllib.parse import urlparse
from uuid import UUID
from idmtools.assets import AssetCollection
from idmtools.assets.file_list import FileList
from idmtools_platform_comps.ssmt_work_items.comps_workitems import InputDataWorkItem
from idmtools_platform_comps.utils.package_version import get_latest_docker_image_from_artifactory

# {
#   "WorkItem_Type": "ImageBuilderWorker",
#   "Build": {
#     "Type": "singularity",
#     "Input": "docker://docker-production.packages.idmod.org/idm/dtk-ubuntu-py3.7-mpich3.3-runtime:20.04.09",
#     "Flags": {
#       "--section": [
#         "all"
#       ],
#       "--library": "https://library.sylabs.io",
#       "Switches": [
#         "--fix-perms",
#         "--force"
#       ]
#     },
#     "Output": "dtk-ubuntu-py3.7-mpich3.3-runtime.sif",
#     "Tags": {
#       "NumericValue": 42,
#       "StringValue": "foobar",
#       "JustTag": null
#     },
#     "AdditionalMounts": [
#       "/shared"
#     ],
#     "StaticEnvironment": {
#       "FOO": "BAR"
#     }
#   }
# }


@dataclass(repr=False)
class SingularityBuildWorkItem(InputDataWorkItem):
    #: Path to definition file
    definition_file: str = field(default=None)
    #: Image Url
    image_url: InitVar[str] = None
    #: Destination image name
    image_name: str = field(default="image.sif")
    #: Name of the workitem
    name: str = field(default=None)
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

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, image_url: str):
        if self.name is None:
            self.name = "Singularity build"
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files)

        self.image_url = image_url if isinstance(image_url, str) else None

    def get_container_info(self) -> Dict[str, str]:
        pass

    @property
    def image_url(self):
        return self._image_url

    @image_url.setter
    def image_url(self, value: str):
        url_info = urlparse(value)
        if url_info.scheme == "docker":
            if "packages.idmod.org" in value:
                path = "/".join(url_info.path.split(":")) if ":" in url_info.path else url_info.path
                url = get_latest_docker_image_from_artifactory(path)
            # fetch the info on the version
            pass
        pass



