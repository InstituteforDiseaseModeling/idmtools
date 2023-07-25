"""
Utilities for getting information and examples from gitrepos.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import sys
import json
from logging import getLogger
import requests
import urllib.request
from click import secho
from dataclasses import dataclass, field
logger = getLogger(__name__)
user_logger = getLogger('user')

REPO_OWNER = 'institutefordiseasemodeling'
REPO_NAME = 'idmtools'
GITHUB_HOME = 'https://github.com'
GITHUB_API_HOME = 'https://api.github.com'


@dataclass
class GitRepo:
    """
    GitRepo allows interaction with remote git repos, mainly for examples.
    """
    repo_owner: str = field(default=None)
    repo_name: str = field(default=None)
    _branch: str = field(default='main', init=False, repr=False)
    _path: str = field(default='', init=False, repr=False)
    _verbose: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        """
        Initialize GitRepo.

        If repo_owner or repo_name is None, the defaults REPO_OWNER and REPO_NAME

        Returns:
            None
        """
        self.repo_owner = self.repo_owner or REPO_OWNER
        self.repo_name = self.repo_name or REPO_NAME

    @property
    def path(self):
        """
        Path property.

        Returns:
            Return path property
        """
        return self._path

    @property
    def branch(self):
        """
        Branch property.

        Returns:
            Return branch property
        """
        return self._branch

    @property
    def verbose(self):
        """
        Return verbose property.

        Returns:
            Return verbose property
        """
        return self._verbose

    @property
    def repo_home_url(self):
        """
        Construct repo home url.

        Returns: repo home url
        """
        return f'{GITHUB_HOME}/{self.repo_owner}/{self.repo_name}'

    @property
    def repo_example_url(self):
        """
        Construct repo example url.

        Returns: repo example url
        """
        return f'{self.repo_home_url}/tree/{self._branch}/{self._path}'

    @property
    def api_example_url(self):
        """
        Construct api url of the examples for download.

        Returns: api url
        """
        return f'{GITHUB_API_HOME}/repos/{self.repo_owner}/{self.repo_name}/contents/{self._path}?ref={self._branch}'

    def parse_url(self, url: str, branch: str = None, update: bool = True):
        """
        Parse url for owner, repo, branch and example path.

        Args:
            url: example url
            branch: user branch to replace the branch in url
            update: True/False - update repo or not

        Returns: None
        """
        default_branch = 'main'
        ex_text = 'Please Verify URL Format: \nhttps://github.com/<owner>/<repo>/(tree|blob)/<branch>/<path>\nor\nhttps://github.com/<owner>/<repo>/'

        example_url = url.lower().strip().rstrip('/')
        url_chunks = example_url.replace(f'{GITHUB_HOME}/', '').split('/')

        if len(url_chunks) < 2 or (len(url_chunks) >= 3 and url_chunks[2] not in ['tree', 'blob']):
            raise Exception(f'Your Example URL: {url}\n{ex_text}')

        repo_owner = url_chunks[0]
        repo_name = url_chunks[1]

        if len(url_chunks) <= 3:
            _branch = branch if branch else default_branch
            _path = ''
        else:
            _branch = branch if branch else url_chunks[3] if url_chunks[3] else default_branch
            _path = '/'.join(url_chunks[4:])

        if update:
            self.repo_owner = repo_owner
            self.repo_name = repo_name
            self._branch = _branch
            self._path = _path
        else:
            return {'repo_owner': repo_owner, 'repo_name': repo_name, 'branch': _branch, 'path': _path}

    def list_public_repos(self, repo_owner: str = None, page: int = 1, raw: bool = False):
        """
        Utility method to retrieve all public repos.

        Args:
            repo_owner: the owner of the repo
            page: pagination of results
            raw: bool - return rwo data or simplified list

        Returns: repo list
        """
        # build api url
        api_url = f'{GITHUB_API_HOME}/users/{repo_owner if repo_owner else self.repo_owner}/repos'

        if page:
            api_url = f'{api_url}?page={page}'

        resp = requests.get(api_url)
        if resp.status_code != 200:
            raise Exception(f'Failed to access: {api_url}')

        # get repos as json
        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [r['full_name'] for r in repo_list]

    def list_repo_releases(self, repo_owner: str = None, repo_name: str = None, raw: bool = False):
        """
        Utility method to retrieve all releases of the repo.

        Args:
            repo_owner: the owner of the repo
            repo_name: the name of repo
            raw: bool - return raw data or simplified list

        Returns: the release list of the repo
        """
        # build api url
        api_url = f'{GITHUB_API_HOME}/repos/{repo_owner if repo_owner else self.repo_owner}/{repo_name if repo_name else self.repo_name}/releases'

        # make api call
        resp = requests.get(api_url)
        if resp.status_code != 200:
            raise Exception(f'Failed to access: {api_url}')

        # get repos as json
        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [f"{r['tag_name']} at {r['published_at']}" for r in repo_list]

    def download(self, path: str = '', output_dir: str = "./", branch: str = 'main') -> int:
        """
        Download files with example url provided.

        Args:
            path: local file path to the repo
            output_dir: user local folder to download files to
            branch: specify branch for files download from

        Returns: total file count downloaded
        """
        if path.startswith('https://'):
            self.parse_url(path)
        else:
            self._path = path
            self._branch = branch

        if not os.path.exists(output_dir):
            raise Exception(f"output_dir does not exist: {output_dir}")

        # First time display download url and local destination info
        if self.verbose:
            user_logger.info(f'Download Examples From: {self.repo_example_url}')
            user_logger.info(f'Local Destination: {os.path.abspath(output_dir)}')
            user_logger.info('Processing...')
            self._verbose = False

        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            response = urllib.request.urlretrieve(self.api_example_url)
        except KeyboardInterrupt:
            # when CTRL+C is pressed during the execution of this script,
            # bring the cursor to the beginning, erase the current line, and dont make a new line
            user_logger.error("✘ Got interrupted")
            sys.exit()
        except Exception as ex:
            secho(f'Failed to access: {self.api_example_url}', fg="yellow")
            logger.exception(ex)
            exit(1)

        download_dir = os.path.join(output_dir, self.repo_name)

        # total files count
        total_files = 0
        with open(response[0], "r") as f:
            data = json.load(f)

        if isinstance(data, dict) and data["type"] == "file":
            # create folder when necessary
            path = data["path"]
            os.makedirs(os.path.dirname(os.path.join(download_dir, path)), exist_ok=True)

            try:
                # download the file
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(data["download_url"], os.path.join(download_dir, path))
                return 1
            except KeyboardInterrupt:
                # when CTRL+C is pressed during the execution of this script,
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                user_logger.error("✘ Got interrupted", )
                sys.exit()
            except Exception as ex:
                secho(f'Failed to access: {self.api_example_url}', fg="yellow")
                user_logger.error(ex)
                exit(1)

        total_files += len([f for f in data if f['type'] == 'file'])

        for file in data:
            file_url = file["download_url"]
            path = file["path"]

            # create folder when necessary
            os.makedirs(os.path.dirname(os.path.join(download_dir, path)), exist_ok=True)

            if file_url is not None:
                try:
                    # download the file
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(file_url, os.path.join(download_dir, path))
                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    user_logger.error("✘ Got interrupted", )
                    sys.exit()
            else:
                total_files += self.download(path, output_dir, branch)

        return total_files

    def peep(self, path: str = '', branch: str = 'main'):
        """
        Download files with example url provided.

        Args:
            path: local file path to the repo
            branch: specify branch for files download from

        Returns: None
        """
        if path.startswith('https://'):
            repo_meta = self.parse_url(path, branch, False)
        else:
            self._path = path
            self._branch = branch
            repo_meta = {'repo_owner': self.repo_owner, 'repo_name': self.repo_name, 'branch': branch or self.branch,
                         'path': path or self.path}

        try:
            api_example_url = f"{GITHUB_API_HOME}/repos/{repo_meta['repo_owner']}/{repo_meta['repo_name']}/contents/{repo_meta['path']}?ref={repo_meta['branch']}"
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            response = urllib.request.urlretrieve(api_example_url)
        except KeyboardInterrupt:
            # when CTRL+C is pressed during the execution of this script,
            # bring the cursor to the beginning, erase the current line, and dont make a new line
            user_logger.error("✘ Got interrupted")
            sys.exit()

        result = []
        with open(response[0], "r") as f:
            data = json.load(f)

        if isinstance(data, dict):
            d = {'type': data['type'], 'name': data['path'], 'path': data['path'], 'html_url': data['html_url']}
            result.append(d)
        else:
            for file in data:
                d = {'type': file['type'], 'name': file['name'], 'path': file['path'], 'html_url': file['html_url']}
                result.append(d)

        return result
