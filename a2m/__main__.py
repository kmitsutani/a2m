from pathlib import Path
import click
import sys
from traceback import print_tb

from a2m.config import parse_config
from a2m.initialize import initialize
from a2m.emit import emit as emit_func

@click.group()
def cli():
    pass

@cli.command()
def init():
    initialize()

@cli.command()
@click.option('--config', '-c', type=Path,
              default=Path("~/.cache/a2m/config.yml"))
def emit(config):
    config = config.expanduser().absolute()
    emit_func(config)


@cli.command()
@click.option('--config', '-c', type=Path,
              default=Path("~/.cache/a2m/config.yml"))
def check_config(config):
    tb = ""
    try:
        parse_config(config, debug=True)
        print('OK')
    except:
        exc, etype, tb = sys.exc_info()
        print(exc, etype)
        print_tb(tb)

@cli.command()
def init_systemd_conf():
    pass

if __name__ == '__main__':
    cli()
