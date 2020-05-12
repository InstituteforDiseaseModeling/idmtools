import os
import json
import click
from click import secho
from colorama import Fore
from idmtools.utils.gitrepo import GitRepo, REPO_OWNER, GITHUB_HOME, REPO_NAME
from idmtools_cli.cli.entrypoint import cli


@cli.group()
def example():
    pass


@example.command()
@click.option('--raw', default=False, type=bool, help="Files in detail")
def view(raw):
    """
    List idmtools available examples

    Returns: display examples
    """
    examples = get_plugins_examples()

    if raw:
        print(json.dumps(examples, indent=3))
        exit(0)

    for plugin, urls in examples.items():
        print('\n', plugin)
        urls = [urls] if isinstance(urls, str) else urls
        url_list = [f'    - {url}' for url in urls]
        print('\n'.join(url_list))


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
    repos_full = [f'    - {GITHUB_HOME}/{r}' for r in repos]
    print(f"GitHub Owner: {gr.repo_owner}")
    print('\n'.join(repos_full))


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
    rels = gr.list_repo_releases()
    rels_list = [f' - {r}' for r in rels]
    print(f'The Repo: {gr.repo_home_url}')
    print('\n'.join(rels_list))


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

    secho(f"{url}", fg="blue")
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
@click.option('--url', default=None, multiple=True, help="Repo Examples Url")
@click.option('--output', default='./', help="Examples Download Destination")
def download(url, output):
    """
    Download examples from GitHub repo to user location

    Args:
        url: GitHub Repo examples url
        output: Local folder

    Returns: None
    """
    total = 0
    urls = list(filter(None, url)) if url else None
    option, example_dict = choice(urls)
    secho(f"This is your selection: {option}", fg="bright_blue")

    # If we decide to go ahead -> write to file
    if click.confirm("Do you want to go ahead to download examples?", default=True):
        simplified_option, duplicated = remove_duplicated_examples(option, example_dict)
        secho(f'Removed duplicated examples: {duplicated}', fg="bright_red")
        # secho(f'Simplified Selection: {simplified_option}', fg="bright_green")
        # exit()
        for i in simplified_option:
            total += download_example(i, example_dict[i], output)

        secho(f"Total Files: {total}", fg="yellow")
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

    Returns: file count
    """
    # Display file information
    click.echo(f"\nDownloading Examples {option if option else ''}: '{url}'")
    click.echo(f'Local Folder: {os.path.abspath(output)}')
    secho('Processing...')

    # Start to download files
    gr = GitRepo()
    total = gr.download(path=url, output_dir=output)
    return total


def get_plugins_examples():
    """
    Collect all idmtools examples

    Returns: examples urls as dict
    """

    # test_examples = {
    #     'A': 'https://github.com/dustin/py-github/tree/master/github/data',
    #     'B': 'https://github.com/dustin/py-github/tree/master/github',
    #     'C': 'https://github.com/dustin/py-github/tree/master/github/__init__.py',
    #     'D': ['https://github.com/dustin/py-github/tree/master/github',
    #           'https://github.com/dustin/py-github/tree/master/github/data'],
    #     'E': [
    #         'https://github.com/dustin/py-github/tree/master/github/data',
    #         'https://github.com/dustin/py-github/tree/master/repo/data/util.py',
    #         'https://github.com/dustin/py-github/tree/master/repo/data',
    #         'https://github.com/dustin/py-github/tree/master/github',
    #         'https://github.com/dustin/py-github/tree/master/github/test',
    #         'https://github.com/dustin/py-github/tree/master/github/__init__.py'
    #     ]
    # }
    # return test_examples

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


def choice(urls: list = None):
    """
    Take urls as user selection or prompt user for example selections
    Args:
        urls: user provided examples

    Returns: True/False and results (List)
    """
    if urls is None:
        examples = get_plugins_examples()

        # Collect all examples and remove duplicates
        url_list = []
        for exp_urls in examples.values():
            exp_urls = [exp_urls] if isinstance(exp_urls, str) else exp_urls
            url_list.extend(list(map(str.lower, exp_urls)))
    else:
        url_list = urls

    # Remove duplicates
    url_list = list(set(url_list))

    # Soring urls
    url_list = sorted(url_list, reverse=False)
    # url_list = sorted(url_list, key=len, reverse=False)

    # Provide index to each example
    example_dict = {}
    for i in range(len(url_list)):
        example_dict[i + 1] = url_list[i]

    # Pre-view examples for user to select
    file_list = [f'    {i}. {url}' for i, url in example_dict.items()]
    print('Example List:')
    print('\n'.join(file_list))

    if urls:
        # No user prompt for selection
        return ['all'], example_dict

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
            user_input = sorted(result, reverse=False)
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


def remove_duplicated_examples(user_selected: list, example_dict: dict):
    """
    Removed duplicated examples
    Args:
        user_selected: user selection
        example_dict: all examples

    Returns: simplified selection, duplicated selection
    """
    if 'all' in user_selected:
        user_selected = range(1, len(example_dict) + 1)

    duplicated_selection = []
    for i in range(len(user_selected)):
        pre = [] if i == 0 else user_selected[0:i]
        if any([example_dict[user_selected[i]].startswith(example_dict[j]) for j in pre]):
            duplicated_selection.append(user_selected[i])

    simplified_selection = [i for i in user_selected if i not in duplicated_selection]
    return simplified_selection, duplicated_selection
