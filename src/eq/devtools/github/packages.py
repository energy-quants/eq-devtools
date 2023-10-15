from typing import cast
from urllib.parse import quote_plus

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
    res = await get(
        f"orgs/{owner}/packages?package_type=container", model=list[Package], **kwargs
    )
    return cast(list[Package], res)


async def get_package(owner: str, package: str, **kwargs) -> Package:
    res = await get(
        f"orgs/{owner}/packages/container/{quote_plus(package)}",
        model=Package,
        **kwargs,
    )
    return cast(Package, res)


async def list_package_versions(
    owner: str, package: str, **kwargs
) -> list[PackageVersion]:
    res = await get(
        f"/orgs/{owner}/packages/container/{quote_plus(package)}/versions",
        model=list[PackageVersion],
        **kwargs,
    )
    for package_version in res:
        package_version.package = package

    return cast(list[PackageVersion], res)


def _get_versions(self) -> list[PackageVersion]:
    return list_package_versions(self.owner.login, self.name)


# Monkey-patch Package to add versions property
setattr(Package, "versions", property(_get_versions))


async def delete_package_version(
    owner: str, package: str, *, version_id: int, **kwargs
) -> None:
    await delete(
        f"/orgs/{owner}/packages/container/{quote_plus(package)}/versions/{version_id:d}",
        **kwargs,
    )
