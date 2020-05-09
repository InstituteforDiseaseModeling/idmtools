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
    List idmtools examples available

    Returns: display examples
    """
    urls = get_plugins_example_urls()
    # print(json.dumps(urls, indent=3))

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
        repo: repo name

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
            download_example('', url, output)
            secho("✔ Download successfully!", fg="bright_green")
        else:
            secho("Aborted...", fg="bright_red")
        exit()

    option, example_dict = choice()
    secho(f"This is your selection: {option}", fg="bright_blue")

    # If we decide to go ahead -> write to file
    if click.confirm("Do you want to go ahead to download examples?", default=True):
        if 'all' in option:
            # for url in example_dict.values():
            for i in range(1, len(example_dict) + 1):
                download_example(i, example_dict[i], output)
        else:
            for i in option:
                download_example(i, example_dict[i], output)

        secho("✔ Download successfully!", fg="bright_green")
    else:
        secho("Aborted...", fg="bright_red")


def download_example(option, url, output):
    click.echo(f"\nDownloading Examples #{option}: '{url}'")
    click.echo(f'Local Folder: {output}')

    gr = GitRepo()
    # gr.download(path_to_repo=url, output_dir=output)


def get_plugins_example_urls():
    """
    Collect all idmtools examples

    Returns: examples urls as dict
    """
    # return {'a': 'test_url_1', 'b': 'test_url_2', 'c': ['test_url_1', 'test_url_2', 'test_url_3', 'test_url_4']}

    from idmtools.registry.master_plugin_registry import MasterPluginRegistry
    pm = MasterPluginRegistry()
    plugin_map = pm.get_plugin_map()

    example_plugins = {}
    for spec_name, plugin in plugin_map.items():
        try:
            # print('-----------------------------')
            # print(spec_name, plugin)
            plugin_url_list = plugin.get_example_urls()
            if len(plugin_url_list) > 0:
                example_plugins[spec_name] = plugin_url_list
        except Exception as ex:
            print(ex)

    return example_plugins


def choice():
    """
    Prompt user for example selections
    
    Returns: True/False and results
    """
    urls = get_plugins_example_urls()
    # print(json.dumps(urls, indent=3))

    url_list = []
    for u in urls.values():
        url_list.extend(u)
    url_list = list(set(url_list))
    url_list = sorted(url_list, reverse=False)
    # print('\n'.join(url_list))

    example_dict = {}
    for i in range(len(url_list)):
        example_dict[i + 1] = url_list[i]
    # print(json.dumps(example_dict, indent=3))

    file_list = [f'    {i}. {url}' for i, url in example_dict.items()]
    print('Example List:')
    print('\n'.join(file_list))

    num_set = set(range(1, len(url_list) + 1))
    while True:
        user_input = click.prompt(
            f"\nSelect examples (multiple) for download (all or 1-{len(url_list)} separated by space)", type=str,
            default='all',
            prompt_suffix=f": {Fore.GREEN}")
        valid, result = validate(user_input, num_set)

        if valid:
            user_input = result
            break

        # Else display the error message
        secho(f'This is not correct choice: {result}', fg="bright_red")

    # print(user_input)
    return user_input, example_dict


def validate(user_input: object, num_set: set):
    """
    Validate user_input against num_set
    Args:
        user_input: user input
        num_set: test against this set

    Returns: True/False and result
    """
    nums = user_input.lower().strip().split(' ')
    # print(nums)
    # remove empty space
    nums = list(filter(None, nums))
    # print(nums)
    nums = [int(a) if a.isdigit() else a for a in nums]
    extra = set(nums) - num_set - {'all'}

    if len(extra) == 0 and len(nums) > 0:
        if 'all' in nums:
            nums = ['all']
        return True, nums
    else:
        return False, list(extra)
