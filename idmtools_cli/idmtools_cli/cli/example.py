import json
import click
from idmtools.utils.gitrepo import GitRepo, REPO_OWNER, GITHUB_HOME
from idmtools_cli.cli.entrypoint import cli

examples_downloaded = []


@cli.group()
def example():
    pass


@example.command()
def list():
    """
    List idmtools examples available

    Returns: display examples
    """
    urls = get_plugins_example_urls()
    print(json.dumps(urls, indent=3))


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
        download_plugin_examples('User Examples', url, output)
        exit()

    plugins_example_urls = get_plugins_example_urls()

    for plugin, example_list in plugins_example_urls.items():
        download_plugin_examples(plugin, example_list, output)

    print(f"✔ Download complete!")


def get_plugins_example_urls():
    return {'a': 'test_url_1', 'b': 'test_url_2', 'c': ['test_url_1', 'test_url_2', 'test_url_3', 'test_url_4']}

    from idmtools.registry.master_plugin_registry import MasterPluginRegistry
    pm = MasterPluginRegistry()
    plugins = pm.get_plugins()
    plugin_map = pm.get_plugin_map()
    # print(pm)
    # print(plugins)
    print(plugin_map)

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

    print('Has example plugins:\n\n', json.dumps(example_plugins, indent=3))

    return example_plugins


def download_plugin_examples(plugin, example_list, output):
    # print(plugin, example_list)
    # print(examples_downloaded)
    # print('--------------------')
    if not isinstance(example_list, list):
        example_list = [example_list]

    click.echo(f"\nDownloading Examples for '{plugin}'")
    # if len(example_list) == 1:
    #     click.echo(f'Example Url: {example_list[0]}')
    # click.echo(f'Local Folder: {output}')

    gr = GitRepo()
    for url in example_list:
        if url not in examples_downloaded:
            click.echo(f'Example Url: {url}')
            click.echo(f'Local Folder: {output}')
            examples_downloaded.append(url)
            # gr.download(path_to_repo=url, output_dir=output)
        else:
            print(f'Ignored duplicate: {url}')
    print(f"✔ {plugin}: Download complete.\n")
