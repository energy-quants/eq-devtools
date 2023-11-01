from typing import Optional

import click

from eq.devtools.conda import (
    build_package,
    publish_oci_artifact,
    render_recipe,
)


__all__ = (
    "conda",
)


@click.group()
def conda():
    pass


@conda.command(name="render")
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
    default="./.build/conda/recipe/recipe.yaml",
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


@conda.command(name="build")
@click.option(
    "--recipe-file",
    type=Optional[str],
    default=None,
)
@click.option(
    "--build-num",
    type=int,
    default=0,
    help="The build number of the package.",
)
@click.option(
    "--output-path",
    type=str,
    default="./.build/conda/dist",
)
@click.option(
    "--debug/--no-debug",
    default=True,
)
def build(
    recipe_file,
    build_num,
    output_path,
    debug,
) -> None:
    """Build a conda package for the current project."""
    build_package(
        build_number=build_num,
        recipe_file=recipe_file,
        output_path=output_path,
        debug=debug,
    )


@conda.command(name="publish")
@click.option(
    "--filepath", type=str, help="The filepath to the `.conda` package to publish."
)
@click.option(
    "--owner",
    type=str,
    help="The GitHub user or organisation to publish the package to.",
)
@click.option(
    "--tag",
    type=str,
    default=None,
    help="An optional tag to use instead of the package version.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="A flag to enable verbose output for the `powerloader` command.",
)
@click.option(
    "--token",
    type=Optional[str],
    default=None,
    help=(
        "The GitHub token to use. "
        "If not specified, the `GITHUB_TOKEN` env var will be used."
    ),
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
)
def publish(
    filepath,
    owner,
    tag,
    verbose,
    token,
    debug,
) -> None:
    """Publish a conda package as an OCI artifact to `ghcr.io`."""
    publish_oci_artifact(
        filepath=filepath,
        owner=owner,
        tag=tag,
        verbose=verbose,
        token=token,
        debug=debug,
    )
