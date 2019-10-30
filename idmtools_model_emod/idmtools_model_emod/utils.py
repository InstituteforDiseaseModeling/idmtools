import os
import stat
from enum import Enum
from getpass import getpass
from logging import getLogger

# TODO Make this configurable
from typing import Tuple

BAMBOO_URL = 'http://idm-bamboo.internal.idm.ctr:8085'
ERADICATION_GIT_URL_TEMPLATE = 'https://github.com/InstituteforDiseaseModeling/EMOD/releases/download/v{}/Eradication{}'
ERADICATION_BAMBOO_URL_TEMPLATE = BAMBOO_URL + '/artifact/{}/shared/build-{}Eradication.exe/build/x64' \
                                               '/Release/Eradication/Eradication{}'
KEYRING_SERVICE_ID = 'IDMTOOLS_BAMBOO'
KEYRING_USERNAME_KEY = 'IDMTOOL_BAMBOO_USER'
logger = getLogger(__name__)


class EradicationPlatformExtension(Enum):
    LINUX = ''
    Windows = 'exe'


class EradicationBambooBuilds(Enum):
    GENERIC = 'DTKGEN-DTKRELLNX'
    DENGUE = 'DTKACTDENGUE-DTKACTDENGUERELLNX',
    EMOD_RELEASE = 'EMODREL-SCONSRELLNX'
    FP = 'DTKFP-SCONSRELLNX'
    HIV = 'DTKHIVONGOING-HIVOGSCONSRELNX'
    MALARIA = 'DTKACTIVEMALBRANCH-DTKACTMALRELLNX'
    RELEASE = 'DTKREL-SCONSRELLNX'
    TBHIV = 'DTKACTTBHIV-SCONSLNXALL'
    TYPHOD = 'DTKACTIVETFBRANCH-DTKACTTFRELLNXTF'


def get_github_eradication_url(version: str,
                               extension: EradicationPlatformExtension = EradicationPlatformExtension.LINUX) -> str:
    """
    Get the github eradication url for specified release

    Args:
        version: Release to fetch
        extension: Optional extensions. Defaults to Linux(None)
    Returns:
        Url of eradication release
    """

    return ERADICATION_GIT_URL_TEMPLATE.format(version, extension.value)


def get_bamboo_eradication_url(plan: EradicationBambooBuilds, build_number,
                               extension: EradicationPlatformExtension = EradicationPlatformExtension.LINUX) -> str:
    """
    Get the bamboo eradication url for plan and build number
    Args:
        plan: Bamboo Plan key. see :ref:`EradicationBambooBuilds` for supported build
        build_number: Bamboo build number
        extension: Optional extensions. Defaults to Linux(None)
    Returns:
        Url for Eradication plan/build number
    """
    return ERADICATION_BAMBOO_URL_TEMPLATE.format(plan.value, build_number, extension)


def get_bamboo_creds() -> Tuple[str, str]:
    """
    Get the Username and Password for bamboo using keyring

    Returns:
        Username, Password for bamboo
    """
    import keyring
    username = keyring.get_password(f'{BAMBOO_URL}_USER', "username")
    if username is None:
        username = input("Bamboo User:")
        keyring.set_password(f'{BAMBOO_URL}_USER', "username", username)
    password = keyring.get_password(BAMBOO_URL, username)
    if password is None:
        password = getpass("Password:")
        keyring.set_password(BAMBOO_URL, username, password)
    return username, password


def get_bamboo_client() -> 'Bamboo':  # noqa F821
    """
    Creates the bamboo API client

    Returns:
        BambooClient
    """
    from atlassian import Bamboo
    username, password = get_bamboo_creds()
    client = Bamboo(url=BAMBOO_URL, username=username, password=password)
    return client


def get_bamboo_latest_successful(plan: EradicationBambooBuilds, client: 'Bamboo' = None,  # noqa F821
                                 extension: EradicationPlatformExtension = EradicationPlatformExtension.LINUX):
    """
    Get the url for Eradication from the last successful build of the specified bamboo plan

    Args:
        plan: Bamboo Plan key. see :ref:`EradicationBambooBuilds` for supported build
        client: Optional bamboo client
        extension: Optional extensions. Defaults to Linux(None)

    Raises:
        FileNotFoundError: When a plan or successful build cannot be found
    Returns:
        Url of latest eradication exe
    """
    if client is None:
        client = get_bamboo_client()
    project, short = plan.value.split('-')
    results = list(client.results(project, short))
    for result in results:
        if result['buildState'] == 'Successful':
            logger.info(f'Found Successful build for plan {plan.value} with build number {result["buildNumber"]}')
            return get_bamboo_eradication_url(plan, result['buildNumber'], extension)
    raise FileNotFoundError(f"Could not find a successful build for plan {plan.value}. Please check plan name again")


def download_latest_bamboo(plan: EradicationBambooBuilds, out_path: str, client: 'Bamboo' = None,  # noqa F821
                           extension: EradicationPlatformExtension = EradicationPlatformExtension.LINUX) -> str:
    """
    Downloads the latest successful build for an Eradication Bamboo Plan to specified path

    Args:
        plan: Bamboo Plan key. see :ref:`EradicationBambooBuilds` for supported build
        out_path: Output path to save file
        client: Optional bamboo client. Useful when fetching more than one bamboo build
        extension: Optional extensions. Defaults to Linux(None)

    Returns:
        Returns output string
    """
    import requests
    if client is None:
        client = get_bamboo_client()
    url = get_bamboo_latest_successful(plan, client, extension)
    username, password = get_bamboo_creds()

    with requests.get(url, auth=(username, password), stream=True) as r:
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    # ensure on linux we make it executable
    if os.name != 'nt':
        st = os.stat(out_path)
        os.chmod(out_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return out_path


ERADICATION_213 = get_github_eradication_url('2.13.0')
ERADICATION_218 = get_github_eradication_url('2.18.0')
ERADICATION_220 = get_github_eradication_url('2.20.0')
