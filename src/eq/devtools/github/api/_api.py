from collections.abc import Generator
from datetime import datetime as DateTime
from typing import (
    Any,
    cast,
    Protocol,
)

import tzlocal
from msgspec import (
    field,
    Struct,
)
from rich.repr import Result as RichRepr


TZ_LOCAL = tzlocal.get_localzone()


class HasRichRepr(Protocol):
    def __rich_repr__(self) -> RichRepr: ...


def parse_repr(obj: HasRichRepr) -> Generator[str, None, None]:
    for attr in obj.__rich_repr__():
        if isinstance(attr, str):
            yield f"{attr!r}"
        else:
            attr = cast(tuple[str, Any], attr)
            try:
                key, value = attr
                yield f"{key}={value!r}"
            except (TypeError, ValueError):
                yield f"{attr!r}"


class APIObject(Struct):
    def __repr__(self) -> str:
        if hasattr(self, "__rich_repr__"):
            return f"{self.__class__.__name__}({', '.join(parse_repr(self))})"
        else:
            return object.__repr__(self)


class _Account(APIObject):
    id: int
    node_id: str
    login: str

    def __str__(self) -> str:
        return self.login

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.login!r})"

    def __rich_repr__(self) -> RichRepr:  # type: ignore
        yield self.login


class User(_Account, tag=True):
    name: str


class Organization(_Account, tag=True):
    pass


Account = Organization | User


class Repository(APIObject):
    id: int
    node_id: str
    name: str
    full_name: str
    url: str
    html_url: str
    description: str

    def __rich_repr__(self) -> RichRepr:  # type: ignore
        yield self.full_name


class Package(APIObject):
    id: int
    name: str
    owner: Account
    url: str
    html_url: str
    created_at: DateTime
    updated_at: DateTime
    repository: Repository

    def __str__(self) -> str:
        return self.name

    def __rich_repr__(self) -> RichRepr:  # type: ignore
        yield self.name
        yield "id", self.id
        yield "owner", self.owner.login
        yield "repository", self.repository.full_name


def normalise_tag(arg: str) -> str:
    return arg.lower().removesuffix("metadata")


class _PackageMetadata(APIObject, tag_field="package_type", tag=normalise_tag):
    pass


class ContainerMetadata(_PackageMetadata):
    container: dict

    def __getattr__(self, name) -> Any:
        try:
            return self.container[name]
        except KeyError:
            msg = f"{self.__class__.__name__!r} has no attribute {name!r}"
            raise AttributeError(msg) from None

    def __dir__(self) -> list[str]:
        return sorted((*object.__dir__(self), *self.container.keys()))

    def __rich_repr__(self) -> RichRepr:  # type: ignore
        for key, value in self.container.items():
            yield key, value


class DockerMetadata(_PackageMetadata):
    docker: dict


PackageMetadata = (
    ContainerMetadata | DockerMetadata
)  # reduce(op.or_, _PackageMetadata.__subclasses__())


class PackageVersion(APIObject):
    id: int
    digest: str = field(name="name")
    url: str
    created_at: DateTime
    updated_at: DateTime
    metadata: PackageMetadata
    package: Package | None = None

    def __rich_repr__(self) -> RichRepr:  # type: ignore
        yield str(self.package)
        yield "id", self.id
        yield "updated_at", self.updated_at.astimezone(TZ_LOCAL).isoformat()
        yield "metadata", self.metadata
