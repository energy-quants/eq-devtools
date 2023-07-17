import click

from .. import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.option(
    "--name",
    help="The name of the person to greet.",
    type=click.STRING,
)
def greet(name: str):
    click.echo(f"Hello {name}!")

