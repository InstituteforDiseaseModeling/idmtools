import os
import sys
import json
import urllib.request
from dataclasses import dataclass, field

REPO_OWNER = 'InstituteforDiseaseModeling'
REPO_NAME = 'idmtools'
GITHUB_HOME = 'https://github.com'
GITHUB_API_HOME = 'https://api.github.com'


@dataclass
class GitRepo:
    repo_owner: str = field(default=None)
    repo_name: str = field(default=None)
    _branch: str = field(default='master', init=False, repr=False)
    _path_to_repo: str = field(default='', init=False, repr=False)
    _download_info: bool = field(default=True, init=False, repr=False)

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
        Construct api url for the examples for download
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
        import re
        re_match = re.compile("https://github.com/(.+?)/(.+?)/(tree|blob)/(.+?)/(.*)")

        # extract the owner, repo, branch and example path
        example_url = url.strip()
        result = re_match.search(example_url)
        if result is None:
            ex_text = f'Please Verify URL Format: https://github.com/<owner>/<repo>/(tree|blob)/<branch>/<path_to_repo>'
            raise Exception(f'Your Example URL: {url}\n{ex_text}')

        # update repo with new info
        self.repo_owner = result.group(1)
        self.repo_name = result.group(2)
        self._branch = branch if branch else result.group(4)
        self._path_to_repo = result.group(5)

    def list_public_repos(self, repo_owner=None, raw=False):
        """
        Utility method to retrive all public repos
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
            raise Exception(f'Failed to retrieve Repos: {api_url}')

        # get repos as json
        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [r['full_name'] for r in repo_list]

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
            response = urllib.request.urlretrieve(self.api_example_url)  # Retrieve a URL into a temporary location on disk.
        except KeyboardInterrupt:
            # when CTRL+C is pressed during the execution of this script,
            # bring the cursor to the beginning, erase the current line, and dont make a new line
            print("✘ Got interrupted")
            sys.exit()

        with open(response[0], "r") as f:
            data = json.load(f)

            # If the data is a file, download it as one.
            if isinstance(data, dict) and data["type"] == "file":
                try:
                    # download the file
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(data["download_url"], os.path.join(output_dir, data["name"]))
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    # print_text("Downloaded: " + Fore.WHITE + "{}".format(data["name"]), "green", in_place=True)
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
                os.makedirs(os.path.dirname(os.path.join(output_dir, path)), exist_ok=True)

                if file_url is not None:
                    try:
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        # download the file
                        urllib.request.urlretrieve(file_url, os.path.join(output_dir, path))
                    except KeyboardInterrupt:
                        # when CTRL+C is pressed during the execution of this script,
                        # bring the cursor to the beginning, erase the current line, and dont make a new line
                        print("✘ Got interrupted", )
                        sys.exit()
                else:
                    self.download(path, output_dir, branch)
