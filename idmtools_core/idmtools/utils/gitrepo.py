import os
import sys
import json
import urllib.request
import signal
import argparse
from colorama import Fore, Style, init

REPO_OWNER = 'InstituteforDiseaseModeling'
REPO_NAME = 'idmtools'
API_HOME = 'https://api.github.com'


class GitRepo:
    class UnknownRepository(Exception):
        pass

    def __init__(self, repo_owner=None, repo_name=None):
        self.repo_owner = repo_owner or REPO_OWNER
        self.repo_name = repo_name or REPO_NAME
        self._path_to_repo = ''
        self._branch = 'master'

    @property
    def repo_url(self):
        return f'https://{self.repo_owner}/{self.repo_name}'

    @property
    def api_url(self):
        return f'{API_HOME}/repos/{self.repo_owner}/{self.repo_name}/contents/{self._path_to_repo}?ref={self._branch}'

    def parse_url(self, url, branch=None):
        """
        From the given url, produce a URL that is compatible with Github's REST API. Can handle blob or tree paths.
        """
        import re
        re_match = re.compile("https://github.com/(.+?)/(.+?)/(tree|blob)/(.+?)/(.*)")

        # extract the branch name from the given url (e.g master)
        result = re_match.search(url)
        if result is None:
            # print(f'Your Example URL: {url}')
            ex_text = f'Please Verify URL Format: https://github.com/<owner>/<repo>/(tree|blob)/<branch>/<path_to_repo>'
            raise Exception(f'Your Example URL: {url}\n{ex_text}')

        self.repo_owner = result.group(1)
        self.repo_name = result.group(2)
        self._branch = branch if branch else result.group(4)
        self._path_to_repo = result.group(5)

    def list_public_repos(self, repo_owner=None, raw=False):
        import requests

        api_url = f'{API_HOME}/users/{repo_owner if repo_owner else self.repo_owner}/repos'

        resp = requests.get(api_url)
        if resp.status_code != 200:
            # return None
            raise Exception(f'Failed to retrieve Repos: {api_url}')

        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [r['full_name'] for r in repo_list]

    def download(self, path_to_repo='', output_dir="./", branch='master'):
        """ Downloads the files and directories in repo_url. If flatten is specified, the contents of any and all
         sub-directories will be pulled upwards into the root folder. """

        if path_to_repo.startswith('https://'):
            self.parse_url(path_to_repo)
        else:
            self._path_to_repo = path_to_repo
            self._branch = branch

        if not os.path.exists(output_dir):
            raise Exception(f"output_dir does not exist: {output_dir}")

        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            response = urllib.request.urlretrieve(self.api_url)  # Retrieve a URL into a temporary location on disk.
        except KeyboardInterrupt:
            # when CTRL+C is pressed during the execution of this script,
            # bring the cursor to the beginning, erase the current line, and dont make a new line
            # print_text("✘ Got interrupted", "red", in_place=True)
            sys.exit()

        # total files count
        total_files = 0

        with open(response[0], "r") as f:
            data = json.load(f)
            # getting the total number of files so that we
            # can use it for the output information later
            total_files += len(data)

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

                    return total_files
                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    # print_text("✘ Got interrupted", 'red', in_place=False)
                    sys.exit()

            for file in data:
                file_url = file["download_url"]
                path = file["path"]

                os.makedirs(os.path.dirname(os.path.join(output_dir, path)), exist_ok=True)

                if file_url is not None:
                    try:
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        # download the file
                        urllib.request.urlretrieve(file_url, os.path.join(output_dir, path))

                        # bring the cursor to the beginning, erase the current line, and dont make a new line
                        # print_text("Downloaded: " + Fore.WHITE + "{}".format(file_name), "green", in_place=False,
                        #            end="\n",
                        #            flush=True)

                    except KeyboardInterrupt:
                        # when CTRL+C is pressed during the execution of this script,
                        # bring the cursor to the beginning, erase the current line, and dont make a new line
                        # print_text("✘ Got interrupted", 'red', in_place=False)
                        sys.exit()
                else:
                    self.download(path, output_dir, branch)

        return total_files

