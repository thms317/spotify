"""Setup file."""

from pathlib import Path

import toml
from setuptools import find_packages, setup


def read_toml(section: str, parameter: str) -> str:
    """Read data from the pyproject.toml file.

    Parameters
    ----------
    section : str
        Section of the pyproject.toml file.
    parameter : str
        Parameter of the pyproject.toml file.

    Returns
    -------
    str
        Parameter value.
    """
    pyproject_config = toml.load("pyproject.toml")
    return str(pyproject_config[section][parameter])


def read_dependencies() -> list[str]:
    """Read the dependencies from the requirements file.

    Returns
    -------
    list[str]
        List of dependencies.
    """
    requirements_path = Path("requirements") / "spotify.txt"

    with Path.open(requirements_path, encoding="utf-8") as f:
        return f.readlines()


def read_readme() -> str:
    """Read the README file to use as long description.

    Returns
    -------
    str
        README file content as string.
    """
    readme_path = Path("README.md")

    if not Path.is_file(readme_path):
        return ""

    with Path.open(readme_path, encoding="utf-8") as f:
        return f.read()


def read_optional_dependencies() -> dict[str, list[str]]:
    """Read the optional dependencies from the requirements directory.

    Returns
    -------
    dict[str, list[str]]
        Dictionary containing lists of optional dependencies, grouped by type.
    """
    optional_deps: dict[str, list[str]] = {}

    requirements_path = Path("requirements")
    for file in requirements_path.iterdir():
        if file.stem != "spotify":
            with file.open() as f:
                optional_deps[file.stem] = f.readlines()

    return optional_deps


setup(
    name=read_toml(section="project", parameter="name"),
    version=read_toml(section="project", parameter="version"),
    packages=find_packages(),
    install_requires=read_dependencies(),
    extras_require=read_optional_dependencies(),
    long_description=read_readme(),
    python_requires=read_toml(section="project", parameter="requires-python"),
    description=read_toml(section="project", parameter="description"),
    classifiers=read_toml(section="project", parameter="classifiers"),
    include_package_data=True,
)
