from click.testing import CliRunner


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


def run_command(*args, start_command=None):
    if start_command is None:
        start_command = []
    from idmtools_cli.main import start
    from idmtools_cli.cli import cli
    start()
    runner = CliRunner()
    final_command = start_command + list(args) if len(args) else start_command
    result = runner.invoke(cli, final_command)
    return result
