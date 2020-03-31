import os
import json
from urllib import request
from pkg_resources import parse_version
from packaging.version import parse
from html.parser import HTMLParser


class LinkHTMLParser(HTMLParser):
    previous_tag = None
    pkg_version = []

    def handle_starttag(self, tag, attrs):
        self.previous_tag = tag
        if tag != 'a':
            return

        attr = dict(attrs)
        v = attr['href']
        v = v.rstrip('/')
        self.pkg_version.append(v)


def get_latest_version_from_pypi(pkg_name, display_all=False):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """
    url = f'https://pypi.python.org/pypi/{pkg_name}/json'
    try:
        releases = json.loads(request.urlopen(url).read())['releases']
    except Exception as ex:
        return None

    all_releases = sorted(releases, key=parse_version, reverse=True)

    if display_all:
        print(all_releases)

    release_versions = [ver for ver in all_releases if not parse(ver).is_prerelease]
    latest_version = release_versions[0]

    return latest_version


def get_latest_package_version_from_artifactory(pkg_name, display_all=False):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """

    pkg_path = 'https://packages.idmod.org/artifactory/list/idm-pypi-production/'
    pkg_url = os.path.join(pkg_path, pkg_name)
    return get_latest_version_from_site(pkg_url, display_all)


def get_latest_version_from_site(pkg_url, display_all=False):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """
    import requests

    resp = requests.get(pkg_url)
    if resp.status_code == 404:
        return None

    htmlStr = resp.text

    parser = LinkHTMLParser()
    parser.feed(htmlStr)
    releases = parser.pkg_version
    releases = [v for v in releases if not v.startswith('.')]

    all_releases = sorted(releases, key=parse_version, reverse=True)

    if display_all:
        print(all_releases)

    release_versions = [ver for ver in all_releases if not parse(ver).is_prerelease]
    latest_version = release_versions[0] if release_versions else None

    return latest_version
