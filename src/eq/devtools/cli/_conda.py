from pathlib import Path

import click

from eq.devtools.conda import render_recipe


__all__ = (
    "conda",
)


@click.group()
def conda():
    pass


@conda.command()
@click.option(
    "--version",
    type=str,
    required=True,
    help="The version of the package.",
)
@click.option(
    "--build-num",
    type=int,
    default=0,
    help="The build number of the package.",
)
@click.option(
    "--pyproject-file",
    type=str,
    default="./pyproject.toml",
    help="The filepath of the `pyproject.toml` file",
)
@click.option(
    "--output-path",
    type=str,
    default="./.build/conda/recipe.yaml",
)
@click.option(
    "--debug/--no-debug",
    default=True,
)
def render(
    version: str,
    build_num: int,
    pyproject_file: str,
    output_path: str,
    debug: bool,
) -> None:
    """Renders a Conda recipe from a `pyproject.toml` file."""
    render_recipe(
        version=version,
        build_number=build_num,
        pyproject_file=pyproject_file,
        output_path=output_path,
        debug=debug,
    )