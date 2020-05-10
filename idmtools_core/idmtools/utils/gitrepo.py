import os
import sys
import json
import urllib.request
from dataclasses import dataclass, field

REPO_OWNER = 'institutefordiseasemodeling'
REPO_NAME = 'idmtools'
GITHUB_HOME = 'https://github.com'
GITHUB_API_HOME = 'https://api.github.com'


@dataclass
class GitRepo:
    repo_owner: str = field(default=None)
    repo_name: str = field(default=None)
    _branch: str = field(default='master', init=False, repr=False)
    _path_to_repo: str = field(default='', init=False, repr=False)
    _download_info: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        self.repo_owner = self.repo_owner or REPO_OWNER
        self.repo_name = self.repo_name or REPO_NAME

    @property
    def path_to_repo(self):
        return self._path_to_repo

    @property
    def branch(self):
        return self._branch

    @property
    def repo_home_url(self):
        """
        Construct repo home url
        Returns: repo home url
        """
        return f'{GITHUB_HOME}/{self.repo_owner}/{self.repo_name}'

    @property
    def repo_example_url(self):
        """
        Construct repo example url
        Returns: repo example url
        """
        return f'{self.repo_home_url}/tree/{self._branch}/{self._path_to_repo}'

    @property
    def api_example_url(self):
        """
        Construct api url of the examples for download
        Returns: api url
        """
        return f'{GITHUB_API_HOME}/repos/{self.repo_owner}/{self.repo_name}/contents/{self._path_to_repo}?ref={self._branch}'

    def parse_url(self, url, branch=None):
        """
        Parse url for owner, repo, branch and example path
        Args:
            url: example url
            branch: user branch to replace the branch in url

        Returns: None
        """
        default_branch = 'master'
        ex_text = f'Please Verify URL Format: \nhttps://github.com/<owner>/<repo>/(tree|blob)/<branch>/<path_to_repo>\nor\nhttps://github.com/<owner>/<repo>/'

        example_url = url.lower().strip().rstrip('/')
        url_chunks = example_url.replace(f'{GITHUB_HOME}/', '').split('/')

        if len(url_chunks) < 2 or (len(url_chunks) >= 3 and url_chunks[2] not in ['tree', 'blob']):
            raise Exception(f'Your Example URL: {url}\n{ex_text}')

        self.repo_owner = url_chunks[0]
        self.repo_name = url_chunks[1]

        if len(url_chunks) <= 3:
            self._branch = branch if branch else default_branch
            self._path_to_repo = ''
        else:
            self._branch = branch if branch else url_chunks[3] if url_chunks[3] else default_branch
            self._path_to_repo = '/'.join(url_chunks[4:])

    def list_public_repos(self, repo_owner=None, raw=False):
        """
        Utility method to retrieve all public repos
        Args:
            repo_owner: the owner of the repo
            raw: bool - return rwo data or simplified list

        Returns: repo list
        """
        import requests

        # build api url
        api_url = f'{GITHUB_API_HOME}/users/{repo_owner if repo_owner else self.repo_owner}/repos'

        resp = requests.get(api_url)
        if resp.status_code != 200:
            raise Exception(f'Failed to retrieve: {api_url}')

        # get repos as json
        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [r['full_name'] for r in repo_list]

    def list_repo_tags(self, repo_owner=None, repo_name=None, raw=False):
        """
        Utility method to retrieve all tags of the repo
        Args:
            repo_owner: the owner of the repo
            repo_name: the name of repo
            raw: bool - return raw data or simplified list

        Returns: the tag list of the repo
        """
        import requests

        # build api url
        api_url = f'{GITHUB_API_HOME}/repos/{repo_owner if repo_owner else self.repo_owner}/{repo_name if repo_name else self.repo_name}/tags'

        resp = requests.get(api_url)
        if resp.status_code != 200:
            raise Exception(f'Failed to retrieve: {api_url}')

        # get repos as json
        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [r['name'] for r in repo_list]

    def list_repo_releases(self, repo_owner=None, repo_name=None, raw=False):
        """
        Utility method to retrieve all releases of the repo
        Args:
            repo_owner: the owner of the repo
            repo_name: the name of repo
            raw: bool - return raw data or simplified list

        Returns: the release list of the repo
        """
        import requests

        # build api url
        api_url = f'{GITHUB_API_HOME}/repos/{repo_owner if repo_owner else self.repo_owner}/{repo_name if repo_name else self.repo_name}/releases'

        resp = requests.get(api_url)
        if resp.status_code != 200:
            raise Exception(f'Failed to retrieve: {api_url}')

        # get repos as json
        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [f"{r['tag_name']} at {r['published_at']}" for r in repo_list]

    def download(self, path_to_repo='', output_dir="./", branch='master'):
        """
        Download files with example url provided
        Args:
            path_to_repo: local file path to the repo
            output_dir: user local folder to download files to
            branch: specify branch for files download from

        Returns: None
        """

        if path_to_repo.startswith('https://'):
            self.parse_url(path_to_repo)
        else:
            self._path_to_repo = path_to_repo
            self._branch = branch

        if not os.path.exists(output_dir):
            raise Exception(f"output_dir does not exist: {output_dir}")

        # First time display download url and local destination info
        if self._download_info:
            print(f'Download Examples From: {self.repo_example_url}')
            print(f'Local Destination: {os.path.abspath(output_dir)}')
            self._download_info = False

        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            response = urllib.request.urlretrieve(self.api_example_url)
        except KeyboardInterrupt:
            # when CTRL+C is pressed during the execution of this script,
            # bring the cursor to the beginning, erase the current line, and dont make a new line
            print("✘ Got interrupted")
            sys.exit()

        download_dir = os.path.join(output_dir, self.repo_name)
        with open(response[0], "r") as f:
            data = json.load(f)

            # If the data is a file, download it as one.
            if isinstance(data, dict) and data["type"] == "file":
                try:
                    # download the file
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(data["download_url"], os.path.join(download_dir, data["name"]))
                    return
                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print("✘ Got interrupted", )
                    sys.exit()

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
                        print("✘ Got interrupted", )
                        sys.exit()
                else:
                    self.download(path, output_dir, branch)
