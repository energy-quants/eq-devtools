import io
import os.path
from collections import defaultdict
from itertools import chain
from pathlib import Path
from textwrap import dedent

import ruamel.yaml
import tomllib as toml
from hatch_requirements_txt import load_requirements_files
from ruamel.yaml.scalarstring import PreservedScalarString


__all__ = (
    "render_recipe",
)


def render_recipe(
    *,
    version: str,
    build_number: int,
    pyproject_file: Path | str = Path("./pyproject.toml"),
    output_path: Path | str = Path("./.build/conda/recipe/recipe.yaml"),
    debug: bool = True
) -> Path:
    """Render a conda recipe from a `pyproject.toml` file.

    Parameters
    ----------
    name : str
        The name of the package.
    version : str
        The version of the package.
    build_number : int
        The build number of the package.
    url : str
        The URL of the package.
    license : str
        The license of the package.
    summary : str
        The summary of the package.

    Returns
    -------
    recipe : str
        The rendered conda recipe.

    """
    pyproject_file = Path(pyproject_file)
    output_path= Path(output_path)
    metadata = _parse_pyproject(pyproject_file)
    metadata['version'] = version
    metadata['build_number'] = build_number
    metadata['source_path']  = os.path.relpath(
        pyproject_file.parent,
        output_path.parent,
    )
    recipe = _render_recipe(**metadata)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w') as f:
        f.write(recipe)
    if debug:
        os.system(f"bat {output_path.as_posix()}")

    return output_path



def _parse_pyproject(
    pyproject_file: Path | str,
    /,
) -> dict[str, str]:
    pyproject = toml.load(pyproject_file)
    metadata = dict(
        name = pyproject['project']['name'],
        url = pyproject['project']['urls']['repository'],
        license = pyproject['project']['license']['file'],
        summary = pyproject['project']['description'],
    )
    return metadata


def _parse_requirements() -> dict[str, list[str]]:
    requirements = defaultdict(list[str])
    for filepath in Path('requirements/').glob('**/*.txt'):
        deps, _ = load_requirements_files([filepath.as_posix()])
        requirements[filepath.stem].extend([
            f"{dep.name} {dep.specifier}".strip()
            for dep in deps
        ])

    return requirements


def _render_recipe(
    *,
    name: str,
    version: str,
    build_number: int,
    source_path: str,
    url: str,
    license: str,
    summary: str,
) -> str:
    """Render a conda recipe from the specified arguments.

    Parameters
    ----------
    name : str
        The name of the package.
    version : str
        The version of the package.
    build_number : int
        The build number of the package.
    url : str
        The URL of the package.
    license : str
        The license of the package.
    summary : str
        The summary of the package.
    source_path : Path | str
        The path to the source code of the package.

    Returns
    -------
    recipe : str
        The rendered conda recipe.

    """
    recipe = defaultdict(dict)
    recipe['context']['name'] = name
    recipe['context']['version'] = version
    recipe['package']['name'] = "{{ name }}"
    recipe['package']['version'] = "{{ version }}"
    recipe['source']['path'] = Path(source_path).as_posix()
    recipe['build']['noarch'] = 'python'
    recipe['build']['number'] = build_number
    script = dedent("""
    set -euxo pipefail
    python -m pip install -vv --no-deps --no-build-isolation .
    """).lstrip()
    recipe['build']['script'] = PreservedScalarString(script)
    requirements = _parse_requirements()
    recipe['requirements'] = {
        key: deps
        for key, deps in requirements.items()
        if key in ('build', 'host', 'run')
    }
    # recipe['test']['files'] = ['./tests/']
    # recipe['test']['commands'] = ['tree ./']
    # recipe['test']['requires'] = requirements['test']
    recipe['about']['home'] = url
    recipe['about']['license'] = license
    recipe['about']['summary'] = summary

    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    stream = io.StringIO()
    yaml.dump(dict(recipe), stream=stream)
    return stream.getvalue()
