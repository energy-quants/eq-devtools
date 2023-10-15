import click

from .. import __version__
from ._conda import conda
from .github import github
from ._test import test


__all__ = ("cli",)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def cli():
    pass


cli.add_command(test)
cli.add_command(conda)
cli.add_command(github)
