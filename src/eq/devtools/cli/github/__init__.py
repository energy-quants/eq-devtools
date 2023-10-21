import click

from .packages import packages


__all__ = ("github",)


@click.group()
def github():
    pass


github.add_command(packages)
