# spotify

[![block_fixups](https://github.com/thms317/spotify/actions/workflows/block_fixups.yml/badge.svg)](https://github.com/thms317/spotify/actions/workflows/block_fixups.yml)
[![unit_tests](https://github.com/thms317/spotify/actions/workflows/unit_test.yml/badge.svg)](https://github.com/thms317/spotify/actions/workflows/unit_test.yml)
[![check_formatting](https://github.com/thms317/spotify/actions/workflows/check_formatting.yml/badge.svg)](https://github.com/thms317/spotify/actions/workflows/check_formatting.yml)
[![check_python_packaging](https://github.com/thms317/spotify/actions/workflows/check_python_packaging.yml/badge.svg)](https://github.com/thms317/spotify/actions/workflows/check_python_packaging.yml)

Get the Spotify stats.

## Configuration

### Pre-commit hooks

The pre-commit hooks are defined in the `.pre-commit-config.yaml` file. Before every commit, or when triggered manually, the following checks and tests are run in order:

- several default `pre-commit` checks.
- **ruff** and **mypy** to check - and auto-fix - the formatting of the code.

### Github Actions

The Github Actions are defined in the `.github/workflows` folder. Most are only triggered on certain events such as pull requests. The checks in the Github Actions are the same as the pre-commit hooks. The following actions are run:

- `check_formatting.yml`:
  - **ruff** and **mypy** to check the formatting of the code.
- `unit_tests.yml`:
  - runs the unit tests defined in the `tests` folder.
- `check_python_packaging.yml`:
  - ensures that changes related to packaging correctly build and match the original repository's content.
- `block_fixups.yml`:
  - checks for the presence of `fixup!` commits or `.rej` files between the base and current branches, blocking the merge if any are found.

Note that the formatting checks are descriptive: no changes are made to the code to ensure that the code in the repository is identical to the code on the local machine.


## Common terminal commands

```bash
ruff check (--fix) .
```

```bash
mypy .
```

```bash
pytest -v tests
```

```bash
pre-commit install
```

```bash
pre-commit clean
```

```bash
pre-commit run --all-files
```
