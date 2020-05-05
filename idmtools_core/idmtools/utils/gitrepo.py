import os
import sys
import json
import shutil
import urllib

import re
import urllib.request
import signal
import argparse
from colorama import Fore, Style, init

import github3
from getpass import getpass

"""
https://github.com/dustin/py-github/tree/master/github

https://api.github.com/repos/dustin/py-github/contents/github?ref=master
"""


class GitRepo:
    class BadCredentials(Exception):
        pass

    class AuthorizationError(Exception):
        pass

    class UnknownRepository(Exception):
        pass

    REPO_OWNER = 'InstituteforDiseaseModeling'
    REPO_NAME = 'idmtools'
    TOKEN_FILE = '.token.txt'
    AUTH_TOKEN = None  # allows subclasses to bypass interactive login if overridden

    # AUTH_TOKEN = '2698a4397820dfdcb898592f5e50362977211981'

    def __init__(self, repo_owner=None, repo_name=None):
        self.repo_owner = repo_owner or self.REPO_OWNER
        self.repo_name = repo_name or self.REPO_NAME
        self._path_to_repo = './'
        self._branch = 'master'

    @property
    def repo_path(self):
        return f'https://{self.repo_owner}/{self.repo_name}'

    @property
    def api_path(self):
        return f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self._path_to_repo}?ref={self._branch}'

    def list_public_repos(self, repo_owner=None, raw=False):
        import requests

        api_url = f'https://api.github.com/users/{repo_owner if repo_owner else self.repo_owner}/repos'

        resp = requests.get(api_url)
        if resp.status_code != 200:
            # return None
            raise Exception(f'Failed to retrieve Repos: {api_url}')

        repo_list = resp.json()

        if raw:
            return repo_list
        else:
            return [r['full_name'] for r in repo_list]

    def download(self, path_to_repo='./', branch='master', output_dir="./"):
        """ Downloads the files and directories in repo_url. If flatten is specified, the contents of any and all
         sub-directories will be pulled upwards into the root folder. """

        self._path_to_repo = path_to_repo
        self._branch = branch

        # generate the url which returns the JSON data
        api_url = self.api_path
        download_dirs = self._path_to_repo

        # To handle file names.
        dir_out = output_dir

        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            response = urllib.request.urlretrieve(api_url)  # Retrieve a URL into a temporary location on disk.
        except KeyboardInterrupt:
            # when CTRL+C is pressed during the execution of this script,
            # bring the cursor to the beginning, erase the current line, and dont make a new line
            # print_text("✘ Got interrupted", "red", in_place=True)
            sys.exit()


        # make a directory with the name which is taken from
        # the actual repo
        os.makedirs(dir_out, exist_ok=True)

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
                    urllib.request.urlretrieve(data["download_url"], os.path.join(dir_out, data["name"]))
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
                file_name = file["name"]

                path = file["path"]

                # os.makedirs(os.path.dirname(path), exist_ok=True)   # zdu: bug: not consider dir_out
                os.makedirs(os.path.dirname(os.path.join(dir_out, path)),
                            exist_ok=True)  # almost right but add sxtra level githug

                if file_url is not None:
                    try:
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        # download the file
                        # urllib.request.urlretrieve(file_url, path)  # zdu: bug: not consider dir_out
                        urllib.request.urlretrieve(file_url, os.path.join(dir_out, path))

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
                    self.download(path, branch, dir_out)

        return total_files


def demo1():
    # url = 'https://github.com/dustin/py-github'     # not working
    url = 'https://github.com/dustin/py-github/tree/master/github'  # working
    # url = 'https://github.com/InstituteforDiseaseModeling/idmtools/tree/master/examples/load_lib'   # 404 Not Found

    flatten = False
    output_dir = 'C:\Temp\Temp'

    gr = GitRepo('dustin', 'py-github')

    total_files = gr.download(path_to_repo='github', output_dir=output_dir, flatten=False, )

    # print_text("✔ Download complete", "green", in_place=True)
    print("✔ Download complete")


def demo2():
    gr = GitRepo('dustin', 'py-github')
    public_repos = gr.list_public_repos('InstituteforDiseaseModeling')
    print('\n'.join(public_repos))


if __name__ == '__main__':
    demo1()
    exit()

    demo2()
    exit()
