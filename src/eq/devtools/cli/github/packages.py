from functools import partial

import click
import msgspec
import trio
import wrapt
from rich import print_json
from rich.pretty import pprint

from eq.devtools.github import packages as pkgs


@click.group()
def packages():
    pass


@wrapt.decorator
def run_async(async_fn, instance, args, kwargs):
    json = kwargs.pop("json", False)
    res = trio.run(partial(async_fn, *args, **kwargs))
    if json:
        json = msgspec.json.encode(res).decode("utf-8")
        print_json(json)
    else:
        if res is not None:
            pprint(res)


@packages.command(name="list")
@click.option(
    "--owner",
    type=str,
    required=True,
    help="The owner to list packages for.",
)
@click.option(
    "--json",
    type=str,
    is_flag=True,
    help="Whether to print the result as JSON.",
)
@run_async
async def list_packages(owner: str):
    res = await pkgs.list_packages(owner=owner)
    return res


@packages.command(name="delete")
@click.option(
    "--owner",
    type=str,
    required=True,
    help="The owner of the package to delete.",
)
@click.option(
    "--package",
    type=str,
    required=True,
    help="The name of the package to delete.",
)
@click.option(
    "--json",
    type=str,
    is_flag=True,
    help="Whether to print the result as JSON.",
)
@click.option(
    "--ids",
    type=str,
    required=True,
    help="The (comma-separated) version ids of the package to delete.",
)
@run_async
async def delete(
    owner: str,
    package: str,
    ids: list[int],
    limiter: trio.CapacityLimiter = None,
):
    deleted = []
    limiter = limiter or trio.CapacityLimiter(50)
    async with trio.open_nursery() as nursery:
        for version_id in ids.split(","):
            version_id = version_id.strip()
            if not version_id:
                continue
            version_id = int(version_id)
            async with limiter:
                nursery.start_soon(
                    partial(
                        pkgs.delete_package_version,
                        owner=owner,
                        package=package,
                        version_id=version_id,
                    )
                )
            deleted.append(version_id)

    return dict(deleted=deleted, errors={})


@packages.command(name="cleanup")
@click.option(
    "--owner",
    type=str,
    required=True,
    help="The owner of the package to delete.",
)
@click.option(
    "--package",
    type=str,
    required=True,
    help="The name of the package to delete.",
)
@click.option(
    "--max-age",
    type=int,
    default=7,
    help="The age (in days) after which the package may be deleted.",
)
@click.option(
    "--json",
    type=str,
    is_flag=True,
    help="Whether to print the result as JSON.",
)
@run_async
async def cleanup(
    owner: str,
    package: str,
    max_age: int,
):
    deleted = await pkgs.cleanup_package_versions(
        owner = owner,
        package = package,
        tags_to_keep = ['latest', r'\d+\.\d+\.\d+'],
        max_age = max_age,
        max_parallel=30,
    )
    return dict(deleted=deleted, errors={})
