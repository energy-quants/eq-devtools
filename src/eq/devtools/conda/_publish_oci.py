import os
from pathlib import Path
from subprocess import (
    CalledProcessError,
    PIPE,
    Popen,
    STDOUT,
)


def publish_oci_artifact(
    filepath: str | Path, *, owner: str, verbose: bool = False, token: str | None = None
) -> None:
    """Publish a conda package as an OCI artifact to `ghcr.io`.

    Parameters
    ----------
    FIXME!

    """
    token = token or os.environ["GITHUB_TOKEN"]
    os.environ["GHA_PAT"] = token
    os.environ["GHA_USER"] = owner
    filepath = Path(filepath)
    filename, version, buildstr = filepath.stem.rsplit("-", maxsplit=2)
    cmd = ["powerloader upload"]
    if verbose:
        cmd += ["-v"]
    cmd += [
        f"{filepath}:conda/{filename}:{version.replace('+', '-')}",
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
