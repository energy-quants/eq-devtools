import os
import re
from typing import (
    Literal,
    Type,
    TypeVar,
)

import gidgethub as gh
import gidgethub.httpx
import httpx
import msgspec
from gidgethub.abc import GitHubAPI
from yarl import URL


__all__ = (
    "delete",
    "get",
)


async def _request(
    method: Literal["GET", "DELETE"],
    url: str,
    *,
    api: GitHubAPI,
) -> tuple[int, httpx.Headers, bytes]:
    # print(gh.sansio.format_url(url, {}))
    status, headers, content = await api._request(
        method,
        gh.sansio.format_url(url, {}),
        headers=gh.sansio.create_headers(
            api.requester,
            accept="application/vnd.github.v3+json",
            oauth_token=api.oauth_token,
        ),
    )
    if httpx.codes.is_error(status):
        msg = msgspec.json.decode(content)["message"]
        msg = f"{status}: {msg}\nurl = {url!r}"
        raise httpx.HTTPError(msg)

    return status, headers, content


T = TypeVar("T")


def parse_links(headers: httpx.Headers) -> dict[str, str]:
    links = {}
    key_regex = re.compile(r'\s*rel="(.*?)"\s*')
    if "link" in headers:
        for link in headers["link"].split(","):
            url, key = link.split(";")
            url = url.strip(" <>")
            key = key_regex.match(key).groups()[0]
            links[key] = url
    return links


async def get(
    url: str,
    *,
    model: Type[T],
    github_user: str | None = None,
    github_token: str | None = None,
    timeout: int = 30,
    per_page: int = 100,
) -> T | dict:
    url = URL(url)
    if "per_page" not in url.query:
        url = url.update_query(per_page=per_page)
    async with httpx.AsyncClient(timeout=timeout) as client:
        api = gh.httpx.GitHubAPI(
            client,
            github_user or os.environ["GITHUB_USER"],
            oauth_token=github_token or os.environ["GITHUB_TOKEN"],
        )
        status, headers, content = await _request("GET", str(url), api=api)
        res = msgspec.json.decode(content, type=model)
        links = parse_links(headers)
        while "next" in links:
            status, headers, content = await _request("GET", links["next"], api=api)
            res += msgspec.json.decode(content, type=model)
            links = parse_links(headers)

    return res


async def delete(
    url: str,
    *,
    github_user: str | None = None,
    github_token: str | None = None,
    timeout: int = 30,
) -> T | dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        api = gh.httpx.GitHubAPI(
            client,
            github_user or os.environ["GITHUB_USER"],
            oauth_token=github_token or os.environ["GITHUB_TOKEN"],
        )
        status, headers, content = await _request("DELETE", url, api=api)
    assert not content
