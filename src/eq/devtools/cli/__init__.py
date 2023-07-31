import click

from .. import __version__
from ._conda import conda
from ._test import test


__all__ = (
    "cli",
)


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


cli.add_command(test)
cli.add_command(conda)
