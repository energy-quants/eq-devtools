import re
from datetime import date as Date
from functools import partial
from typing import cast
from urllib.parse import quote_plus

import trio

from .api import (
    Package,
    PackageVersion,
)
from .client import (
    delete,
    get,
)


__all__ = (
    "get_package",
    "list_packages",
    "list_package_versions",
    "delete_package_version",
)


async def list_packages(owner: str, **kwargs) -> list[Package]:
    # https://docs.github.com/en/rest/packages/packages#list-packages-for-an-organization
    kwargs.setdefault('model', list[Package])
    res = await get(
        f"orgs/{owner}/packages?package_type=container", **kwargs
    )
    return cast(list[Package], res)


async def get_package(owner: str, package: str, **kwargs) -> Package:
    # https://docs.github.com/en/rest/packages/packages#get-a-package-for-an-organization
    kwargs.setdefault('model', Package)
    res = await get(
        f"orgs/{owner}/packages/container/{quote_plus(package)}",
        **kwargs,
    )
    return cast(Package, res)


async def list_package_versions(
    owner: str,
    package: str,
    **kwargs
) -> list[PackageVersion]:
    # https://docs.github.com/en/rest/packages/packages#list-package-versions-for-a-package-owned-by-an-organization
    model = kwargs.pop('model', None)
    has_model = model is not None
    model = model or list[PackageVersion]
    res = await get(
        f"/orgs/{owner}/packages/container/{quote_plus(package)}/versions",
        model=model,
        **kwargs,
    )
    if has_model:
        # if a custom model is specified, don't set the package attribute
        return res

    package_obj = await get_package(owner, package, **kwargs)
    for package_version in res:
        package_version.package = package_obj

    return cast(list[PackageVersion], res)


async def delete_package_version(
    owner: str, package: str, *, version_id: int, **kwargs
) -> None:
    # https://docs.github.com/en/rest/packages/packages#delete-package-version-for-an-organization
    await delete(
        f"/orgs/{owner}/packages/container/{quote_plus(package)}/versions/{version_id:d}",
        **kwargs,
    )


async def _get_versions(self) -> list[PackageVersion]:
    return await list_package_versions(self.owner.login, self.name)


# Monkey-patch Package to add versions property
setattr(Package, "versions", property(_get_versions))


# Monkey-patch PackageVersion to add delete method
async def _delete(self) -> None:
    await delete_package_version(
        self.package.owner,
        self.package.name,
        version_id=self.id,
    )

PackageVersion.delete = _delete


async def delete_package_versions(
    *package_versions: PackageVersion,
    max_parallel: int = 30,
) -> list[PackageVersion]:
    # FIXME: handle errors with outcome
    limiter = trio.CapacityLimiter(max_parallel)

    async def _delete(
        package_version: PackageVersion,
        *,
        limiter: trio.CapacityLimiter,
    ) -> None:
        async with limiter:
            await package_version.delete()

    async with trio.open_nursery() as nursery:
        for package_version in package_versions:
            nursery.start_soon(partial(_delete, limiter=limiter), package_version)

    return list(package_versions)


async def cleanup_package_versions(
    owner: str,
    package: str,
    *,
    tags_to_keep: list[str] = ['latest', r'\d+\.\d+\.\d+'],
    max_age: int = 7,
    max_parallel: int = 30,
    **kwargs,
) -> list[PackageVersion]:
    tags_to_keep = re.compile(f"^({'|'.join(tags_to_keep)})$")
    today = Date.today()

    def has_expired(pv: PackageVersion) -> bool:
        age: int = (today - pv.updated_at.date()).days
        return age > max_age

    versions_to_delete = [
        package_version for package_version
        in await list_package_versions(owner, package, **kwargs)
        if has_expired(package_version)
        and not any(map(tags_to_keep.match, package_version.metadata.tags))
    ]
    deleted = await delete_package_versions(*versions_to_delete, max_parallel=max_parallel)
    return deleted
