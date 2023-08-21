import os
from pathlib import Path
from subprocess import (
    CalledProcessError,
    check_output,
    PIPE,
    Popen,
    STDOUT,
)

from ._render import render_recipe


__all__ = (
    "build_package",
    "get_version",
)


def get_version():
    cmd = "git describe --long"
    try:
        output = check_output(cmd, stderr=STDOUT, encoding="utf-8", shell=True)
    except Exception as exc:
        raise RuntimeError(exc.stdout) from exc

    version, distance, sha = output.strip().split("-")
    distance = int(distance)
    if distance == 0:
        return version
    else:
        return f"{version}.post{distance:03d}+{sha[1:]}"


def build_package(
    *,
    build_number: int = 0,
    recipe_file: Path | str | None = None,
    output_path: Path | str = Path("./.build/conda/dist"),
    debug: bool = True,
) -> None:
    """Build a conda package for the current project."""
    version = get_version()
    os.environ["SETUPTOOLS_SCM_PRETEND_VERSION"] = version
    if recipe_file is None:
        recipe_file = render_recipe(
            version=version,
            build_number=0,
            debug=debug,
        )
    else:
        recipe_file = Path(recipe_file)

    if recipe_file.name != "recipe.yaml":
        msg = (
            "Recipe must be named `recipe.yaml`.\n"
            f"recipe_file = {recipe_file.as_posix()!r}"
        )
        raise RuntimeError(msg)

    recipe_path = recipe_file.parent
    output_path = Path(output_path)
    cmd = (
        "boa build --pkg-format 2 "
        f"--output-folder={output_path.expanduser().resolve().as_posix()!r} "
        f"{recipe_path.as_posix()!r} "
        #  "rattler-build build "
        #  f"--output-dir={output_path.as_posix()!r} "
        #  f"--recipe={recipe_path.as_posix()!r} "
    ).strip()
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
