import click


__all__ = ("test",)


@click.group()
def test():
    pass


@test.command()
@click.option(
    "--name",
    help="The name of the person to greet.",
    type=click.STRING,
)
def greet(name: str):
    click.echo(f"Hello {name}!")
