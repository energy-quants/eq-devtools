import os
from pathlib import Path
from subprocess import (
    CalledProcessError,
    PIPE,
    Popen,
    STDOUT,
)


def publish_oci_artifact(
    filepath: str | Path,
    *,
    owner: str,
    tag: str | None = None,
    verbose: bool = False,
    token: str | None = None,
    debug: bool = False,
) -> None:
    """Publish a conda package as an OCI artifact to `ghcr.io`.

    Parameters
    ----------
    FIXME!

    """
    token = token or os.environ.get("GHA_PAT", default=os.environ.get("GITHUB_TOKEN"))
    if token is None:
        msg = "The `GITHUB_TOKEN` environment variable needs to be set!"
        raise RuntimeError(msg)
    os.environ["GHA_PAT"] = token
    os.environ["GHA_USER"] = owner
    if debug:
        print(f"GHA_USER = {os.environ['GHA_USER']!r}")
        print(f"GHA_PAT = {os.environ['GHA_PAT']!r}")
    filepath = Path(filepath)
    filename, version, buildstr = filepath.stem.rsplit("-", maxsplit=2)
    cmd = ["powerloader upload"]
    if verbose:
        cmd += ["-v"]
    tag = tag or version.replace('+', '-')
    cmd += [
        f"{filepath}:conda/{filename}:{tag}",
        "-m oci://ghcr.io",
    ]
    cmd = " ".join(cmd)
    print(cmd)
    with Popen(
        cmd,
        stdout=PIPE,
        stderr=STDOUT,
        bufsize=1,
        universal_newlines=True,
        env=os.environ,
        shell=True,
    ) as process:
        for line in process.stdout:
            print(line, end="")

    if process.returncode != 0:
        raise CalledProcessError(process.returncode, process.args)
