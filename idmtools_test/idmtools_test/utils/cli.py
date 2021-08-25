from typing import List, Dict

from click.testing import CliRunner, Result


def get_subcommands_from_help_result(result):
    lines = striped_cli_output_lines(result)
    found_commands_header = False
    while not found_commands_header:
        nex = lines.pop(0)
        if nex == "Commands:":
            found_commands_header = True
    # filter down to just the name
    lines = [l.split(None, 1)[0].strip() for l in lines]
    return lines


def striped_cli_output_lines(result):
    return list(filter(lambda x: len(x), map(str.strip, result.output.split('\n'))))


def invoke_command(*args, start_command=None, mix_stderr: bool = True, env: Dict[str, str] = None):
    if env is None:
        env = dict()
    if start_command is None:
        start_command = []
    from idmtools_cli.main import start
    from idmtools_cli.cli.entrypoint import cli
    start()
    runner = CliRunner(mix_stderr=mix_stderr)
    final_command = start_command + list(args) if len(args) else start_command
    result = runner.invoke(cli, final_command)
    return result


def run_command(*args: str, start_command: List[str] = None, base_command: str = None, mix_stderr: bool = True, env: Dict[str, str] = None) -> Result:
    if start_command is None:
        start_command = []
    if base_command:
        start_command.append(base_command)
    return invoke_command(*args, start_command=start_command, mix_stderr=mix_stderr, env=env)
