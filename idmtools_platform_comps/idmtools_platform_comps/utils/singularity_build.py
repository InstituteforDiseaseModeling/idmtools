from dataclasses import dataclass, field
from typing import List, Dict
from idmtools.assets import AssetCollection
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

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
class SingularityBuildWorkItem(SSMTWorkItem):
    #: Path to definition file
    definition_file: str = field(default=None)
    #: Image Url
    image_url: str = field(default=None)
    #: Destination image name
    image_name: str = field(default="image.sif")
    #: Name of the workitem
    name: str = field(default=None)

    #: Allows you to set a different library. (The default library is “https://library.sylabs.io”). See https://sylabs.io/guides/3.5/user-guide/cli/singularity_build.html
    library: str = field(default=None)

    #: only run specific section(s) of deffile (setup, post, files, environment, test, labels, none) (default [all])
    section: List[str] = field(default_factory=lambda: ['all'])

    #: build using user namespace to fake root user (requires a privileged installation)
    fix_permissions: bool = field(default=False)

    # AssetCollection created by build
    asset_collection: AssetCollection = field(default=None)

    #: Additional Mounts
    additional_mounts: List[str] = field(default_factory=list)

    #: Environment vars for remote build
    environment_variables: Dict[str, str] = field(default_factory=dict)

    def get_container_info(self) -> Dict[str, str]:
        pass

