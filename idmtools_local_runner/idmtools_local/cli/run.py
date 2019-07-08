from colorama import init
from idmtools_local.cli.base import cli

# our entrypoint for our cli
if __name__ == '__main__':
    init()
    from idmtools_local.cli.simulation import *
    from idmtools_local.cli.experiment import *
    cli()