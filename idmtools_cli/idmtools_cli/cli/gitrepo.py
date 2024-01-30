"""Define the gitrepo group cli command."""
import os
import json
from logging import getLogger
import click
from click import secho
from colorama import Fore
from typing import Optional, List

from idmtools.core.logging import SUCCESS
from idmtools_cli.cli.entrypoint import cli
from idmtools_cli.utils.gitrepo import GitRepo, REPO_OWNER, GITHUB_HOME, REPO_NAME
from idmtools.registry.master_plugin_registry import MasterPluginRegistry

user_logger = getLogger('user')


@cli.group(short_help="Contains commands related to examples download")
def gitrepo():
    """Contains command to download examples."""
    pass


@gitrepo.command()
@click.option('--raw', default=False, type=bool, help="Files in detail")
def view(raw: Optional[bool]):
    """
    Display all idmtools available examples.

    Args:
        raw: True/False - display results in details or simplified format
    """
    list_examples(raw)


def list_examples(raw: bool):
    """
    Display all idmtools available examples.

    Args:
        raw: True/False - display results in details or simplified format
    """
    examples = get_plugins_examples()
    if raw:
        user_logger.info(json.dumps(examples, indent=3))
        exit(0)
    for plugin, urls in examples.items():
        user_logger.info(f'\n{plugin}')
        urls = [urls] if isinstance(urls, str) else urls
        url_list = [f'    - {url}' for url in urls]
        user_logger.info('\n'.join(url_list))


# alias under examples
@cli.group(help="Display a list of examples organized by plugin type")
def examples():
    """Examples group command. alias for gitrepo command."""
    pass


@examples.command(name='list', help="List examples available")
@click.option('--raw', default=False, type=bool, help="Files in detail")
def list_m(raw: Optional[bool]):
    """Alternate path for gitrepo."""
    list_examples(raw)


@gitrepo.command()
@click.option('--owner', default=REPO_OWNER, help="Repo owner")
@click.option('--page', default=1, help="Pagination")
def repos(owner: Optional[str], page: Optional[int]):
    """
    Display all public repos of the owner.

    Args:
        owner: Repo owner
        page: Result pagination
    """
    gr = GitRepo(owner)
    try:
        repos = gr.list_public_repos(page=page)
    except Exception as ex:
        secho(str(ex), fg="yellow")
        exit(1)
    repos_full = [f'    - {GITHUB_HOME}/{r}' for r in repos]
    user_logger.log(SUCCESS, f"GitHub Owner: {gr.repo_owner}")
    user_logger.info('\n'.join(repos_full))


@gitrepo.command()
@click.option('--owner', default=REPO_OWNER, help="Repo owner")
@click.option('--repo', default=REPO_NAME, help="Repo name")
def releases(owner: Optional[str], repo: Optional[str]):
    """
    Display all the releases of the repo.

    Args:
        owner: Repo owner
        repo: Repo name
    """
    gr = GitRepo(owner, repo)
    try:
        rels = gr.list_repo_releases()
    except Exception as ex:
        secho(str(ex), fg="yellow")
        exit(1)
    rels_list = [f' - {r}' for r in rels]
    secho(f'The Repo: {gr.repo_home_url}', fg="green")
    user_logger.info('\n'.join(rels_list))


@gitrepo.command()
@click.option('--url', required=True, help="Repo files url")
@click.option('--raw', default=False, type=bool, help="Display files in detail")
def peep(url: Optional[str], raw: Optional[bool]):
    """
    Display all current files/dirs of the repo folder (not recursive).

    Args:
        url: GitHub repo files url (required)
        raw: Display details or not
    """
    user_logger.info(f'Peep: {url}')
    user_logger.info('Processing...')
    try:
        result = GitRepo().peep(url)
    except Exception as ex:
        secho(f'Failed to access: {url}', fg="yellow")
        user_logger.error(ex)
        exit(1)

    secho(f"Item Count: {len(result)}", fg="green")
    if raw:
        user_logger.info(json.dumps(result, indent=3))
        exit(0)

    for file in result:
        if file['type'] == 'dir':
            secho(f"    - {file['name']}", fg="yellow")
        else:
            secho(f"    - {file['name']}")


@gitrepo.command()
@click.option('--type', default=None, multiple=True, help="Download examples by type (COMPSPlatform, PythonTask, etc)")
@click.option('--url', default=None, multiple=True, help="Repo files url")
@click.option('--output', default='./', help="Files download destination")
def download(type: Optional[str], url: Optional[str], output: Optional[str]):
    """
    Download files from GitHub repo to user location.

    Args:
        type: Object type (COMPSPlatform, PythonTask, etc)
        url: GitHub repo files url
        output: Local folder

    Returns: Files download count
    """
    download_github_repo(output, url, example_types=type)


@examples.command(name='download')
@click.option('--type', default=None, multiple=True, help="Download examples by type (COMPSPlatform, PythonTask, etc)")
@click.option('--url', default=None, multiple=True, help="Repo files url")
@click.option('--output', default='./', help="Files download destination")
def download_alias(type: Optional[str], url: Optional[List[str]], output: Optional[str]):
    """
    Download examples from specified location.

    Args:
        type: Object type (COMPSPlatform, PythonTask, etc)
        url: GitHub repo files url
        output: Local folder

    Returns: Files download count
    """
    download_github_repo(output, url, example_types=list(type))


def download_github_repo(output, urls: List[str], example_types: List[str] = None):
    """
    Download github repo.

    Args:
        output: Output folder
        urls: Urls to download
        example_types: List of example types to download

    Returns:
        None
    """
    total = 0
    if example_types:
        urls = list(urls)
        urls.extend(get_examples_by_types(list(example_types)))
    urls = list(filter(None, urls)) if urls else None
    option, file_dict = choice(urls)
    secho(f"This is your selection: {option}", fg="bright_blue")
    # If we decide to go ahead -> write to file
    if click.confirm("Do you want to go ahead to download files?", default=True):
        simplified_option, duplicated = remove_duplicated_files(option, file_dict)
        secho(f'Removed duplicated files: {duplicated}', fg="bright_red")
        for i in simplified_option:
            total += download_file(i, file_dict[i], output)

        secho(f"Total Files: {total}", fg="yellow")
        secho("Download successfully!", fg="bright_green")
    else:
        secho("Aborted...", fg="bright_red")


def get_examples_by_types(example_types: List[str]) -> List[str]:
    """
    Get examples from Plugins.

    Args:
        example_types: List of types(plugins) to pull examples from

    Returns:
        List of strings to download
    """
    items = get_plugins_examples()
    result = []
    for example in example_types:
        if example in items:
            result.extend(items[example])
        else:
            user_logger.warning(f"Cannot find example type {example}")
    return result


def download_file(option: int, url: str, output: str):
    """
    Use GitRepo utility to download files.

    Args:
        option: file index
        url: file url
        output: local folder to save files

    Returns:
        file count
    """
    # Display file information
    click.echo(f"\nDownloading Files {option if option else ''}: '{url}'")
    click.echo(f'Local Folder: {os.path.abspath(output)}')
    secho('Processing...')

    # Start to download files
    gr = GitRepo()
    total = gr.download(path=url, output_dir=output)
    return total


def get_plugins_examples():
    """
    Collect all idmtools files.

    Returns:
        files urls as dict

    Notes:
        test_examples = {
         'TestA': 'https://github.com/dustin/py-github/tree/main/github/data',
         'TestB': 'https://github.com/dustin/py-github/tree/main/github',
         'TestC': 'https://github.com/dustin/py-github/tree/main/github/__init__.py',
         'TestD': ['https://github.com/dustin/py-github/tree/main/github',
                   'https://github.com/dustin/py-github/tree/main/github/data']
        }
    """
    # Collect all idmtools examples
    plugin_map = MasterPluginRegistry().get_plugin_map()

    example_plugins = {}
    for spec_name, plugin in plugin_map.items():
        try:
            plugin_url_list = plugin.get_example_urls()
            if len(plugin_url_list) > 0:
                example_plugins[spec_name] = plugin_url_list
        except Exception as ex:
            user_logger.error(ex)

    return example_plugins


def choice(urls: list = None):
    """
    Take urls as user selection or prompt user for file selections.

    Args:
        urls: user provided files

    Returns: True/False and results (List)
    """
    if urls is None:
        files = get_plugins_examples()

        # Collect all files and remove duplicates
        url_list = []
        for exp_urls in files.values():
            exp_urls = [exp_urls] if isinstance(exp_urls, str) else exp_urls
            url_list.extend(list(map(str.lower, exp_urls)))
    else:
        url_list = urls

    # Remove duplicates
    url_list = list(set(url_list))
    # Soring urls
    url_list = sorted(url_list, reverse=False)

    # Provide index to each file
    file_dict = {}
    for i in range(len(url_list)):
        file_dict[i + 1] = url_list[i]

    # Pre-view files for user to select
    file_list = [f'    {i}. {url}' for i, url in file_dict.items()]
    user_logger.info('File List:')
    user_logger.info('\n'.join(file_list))

    if urls:
        # Return without user prompt for selection
        return ['all'], file_dict

    # Make sure user makes correct selection
    choice_set = set(range(1, len(url_list) + 1))
    choice_set.add('all')
    while True:
        user_input = click.prompt(
            f"\nSelect files (multiple) for download (all or 1-{len(url_list)} separated by space)", type=str,
            default='all',
            prompt_suffix=f": {Fore.GREEN}")
        valid, result = validate(user_input, choice_set)

        if valid:
            user_input = sorted(result, reverse=False)
            break

        # Else display the error message
        secho(f'This is not correct choice: {result}', fg="bright_red")

    # Return user selection and indexed files
    return user_input, file_dict


def validate(user_input: object, choice_set: set):
    """
    Validate user_input against num_set.

    Args:
        user_input: user input
        choice_set: test against this set

    Returns: True/False and result (List)
    """
    # Normalize user selection
    selection = user_input.lower().strip().split(' ')
    selection = list(filter(None, selection))
    selection = [int(a) if a.isdigit() else a for a in selection]

    # Find difference
    extra = set(selection) - choice_set

    # Return True/False along with selection details
    if len(extra) == 0 and len(selection) > 0:
        if 'all' in selection:
            selection = ['all']
        return True, selection
    else:
        return False, list(extra)


def remove_duplicated_files(user_selected: list, file_dict: dict):
    """
    Removed duplicated files.

    Args:
        user_selected: user selection
        file_dict: all files

    Returns: simplified selection, duplicated selection
    """
    if 'all' in user_selected:
        user_selected = range(1, len(file_dict) + 1)

    duplicated_selection = []
    for i in range(len(user_selected)):
        pre = [] if i == 0 else user_selected[0:i]
        if any([file_dict[user_selected[i]].startswith(file_dict[j]) for j in pre]):
            duplicated_selection.append(user_selected[i])

    simplified_selection = [i for i in user_selected if i not in duplicated_selection]
    return simplified_selection, duplicated_selection
