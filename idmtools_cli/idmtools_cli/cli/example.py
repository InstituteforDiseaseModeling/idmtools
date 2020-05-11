import os
import json
import click
from click import secho
from colorama import Fore, Style
from idmtools.utils.gitrepo import GitRepo, REPO_OWNER, GITHUB_HOME, REPO_NAME
from idmtools_cli.cli.entrypoint import cli

examples_downloaded = []


@cli.group()
def example():
    pass


@example.command()
def view():
    """
    List idmtools available examples

    Returns: display examples
    """
    urls = get_plugins_example_urls()

    for plugin, files in urls.items():
        print('\n', plugin)
        files = [files] if isinstance(files, str) else files
        file_list = [f'    - {url}' for url in files]
        print('\n'.join(file_list))


@example.command()
@click.option('--owner', default=REPO_OWNER, help="Repo Owner")
def repos(owner=None):
    """
    List owner all public repos
    Args:
        owner: repo owner

    Returns: display public repos
    """
    gr = GitRepo(owner)
    repos = gr.list_public_repos()
    repos_full = [f'{GITHUB_HOME}/{r}' for r in repos]
    print('\n - '.join(repos_full))


@example.command()
@click.option('--owner', default=REPO_OWNER, help="Repo Owner")
@click.option('--repo', default=REPO_NAME, help="Repo Name")
def releases(owner=None, repo=None):
    """
    List all the releases of the repo
    Args:
        owner: repo owner
        repo: repo name

    Returns: the list of repo releases
    """
    gr = GitRepo(owner, repo)
    releases = gr.list_repo_releases()
    releases_list = [f' - {r}' for r in releases]
    print(f'The Repo: {gr.repo_home_url}')
    print('\n'.join(releases_list))


@example.command()
@click.option('--owner', default=REPO_OWNER, help="Repo Owner")
@click.option('--repo', default=REPO_NAME, help="Repo Name")
def tags(owner=None, repo=None):
    """
    List all the tags of the repo
    Args:
        owner: repo owner
        repo: repo name

    Returns: the list of repo tags
    """
    gr = GitRepo(owner, repo)
    tags = gr.list_repo_tags()
    tags_list = [f' - {r}' for r in tags]
    print(f'The Repo: {gr.repo_home_url}')
    print('\n'.join(tags_list))


@example.command()
@click.option('--url', required=True, help="Repo Examples Url")
@click.option('--raw', default=False, type=bool, help="Files in detail")
def peep(url, raw):
    """
    List all the tags of the repo
    Args:
        url: GitHub Repo examples url (required)
        raw: display details or not

    Returns: the list of current files/dirs (not recursive)
    """
    print(f'Peep: {url}')
    print('Processing...')
    result = GitRepo().peep(url)

    secho(f"Item Count: {len(result)}", fg="green")
    if raw:
        print(json.dumps(result, indent=3))
        exit(0)

    for file in result:
        if file['type'] == 'dir':
            secho(f"    - {file['name']}", fg="yellow")
        else:
            secho(f"    - {file['name']}")


@example.command()
@click.option('--url', default=None, help="Repo Examples Url")
@click.option('--output', default='./', help="Examples Download Destination")
def download(url, output):
    """
    Download examples from GitHub repo to user location

    Args:
        url: GitHub Repo examples url
        output: Local folder

    Returns: None
    """
    examples_downloaded.clear()

    if url:
        secho(f"Example you want to doanload: \n  {url}", fg="bright_blue")
        if click.confirm("Do you want to go ahead to download examples?", default=True):
            download_example(None, url, output)
            secho("✔ Download successfully!", fg="bright_green")
        else:
            secho("Aborted...", fg="bright_red")
        exit()

    option, example_dict = choice()
    secho(f"This is your selection: {option}", fg="bright_blue")

    # If we decide to go ahead -> write to file
    if click.confirm("Do you want to go ahead to download examples?", default=True):
        if 'all' in option:
            for i in range(1, len(example_dict) + 1):
                download_example(i, example_dict[i], output)
        else:
            for i in option:
                download_example(i, example_dict[i], output)

        secho("✔ Download successfully!", fg="bright_green")
    else:
        secho("Aborted...", fg="bright_red")


def download_example(option: int, url: str, output: str):
    """
    Use GitRepo utility to download examples
    Args:
        option: example index
        url: example url
        output: local folder to save examples

    Returns: None
    """
    # Display file information
    click.echo(f"\nDownloading Examples {option if option else ''}: '{url}'")
    click.echo(f'Local Folder: {os.path.abspath(output)}')
    secho('Processing...')

    # Start to download files
    gr = GitRepo()
    gr.download(path_to_repo=url, output_dir=output)


def get_plugins_example_urls():
    """
    Collect all idmtools examples

    Returns: examples urls as dict
    """
    # return {'A': 'test_url_1', 'B': 'test_url_2', 'C': ['test_url_1', 'test_url_2', 'test_url_3', 'test_url_4']}

    from idmtools.registry.master_plugin_registry import MasterPluginRegistry
    plugin_map = MasterPluginRegistry().get_plugin_map()

    example_plugins = {}
    for spec_name, plugin in plugin_map.items():
        try:
            plugin_url_list = plugin.get_example_urls()
            if len(plugin_url_list) > 0:
                example_plugins[spec_name] = plugin_url_list
        except Exception as ex:
            print(ex)

    return example_plugins


def choice():
    """
    Prompt user for example selections

    Returns: True/False and results (List)
    """
    urls = get_plugins_example_urls()

    # Collect all examples and remove duplicates
    url_list = []
    for u in urls.values():
        url_list.extend(u)
    url_list = list(set(url_list))
    url_list = sorted(url_list, reverse=False)

    # Provide index to each example
    example_dict = {}
    for i in range(len(url_list)):
        example_dict[i + 1] = url_list[i]

    # Pre-view examples for user to select
    file_list = [f'    {i}. {url}' for i, url in example_dict.items()]
    print('Example List:')
    print('\n'.join(file_list))

    # Make sure user makes correct selection
    choice_set = set(range(1, len(url_list) + 1))
    choice_set.add('all')
    while True:
        user_input = click.prompt(
            f"\nSelect examples (multiple) for download (all or 1-{len(url_list)} separated by space)", type=str,
            default='all',
            prompt_suffix=f": {Fore.GREEN}")
        valid, result = validate(user_input, choice_set)

        if valid:
            user_input = result
            break

        # Else display the error message
        secho(f'This is not correct choice: {result}', fg="bright_red")

    # Return user selection and indexed examples
    return user_input, example_dict


def validate(user_input: object, choice_set: set):
    """
    Validate user_input against num_set
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
