# expandvars

Expand system variables Unix style

[![PyPI version](https://img.shields.io/pypi/v/expandvars.svg)](https://pypi.org/project/expandvars)
[![codecov](https://codecov.io/gh/sayanarijit/expandvars/branch/master/graph/badge.svg)](https://codecov.io/gh/sayanarijit/expandvars)

## Inspiration

This module is inspired by [GNU bash's variable expansion features](https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html). It can be used as an alternative to Python's [os.path.expandvars](https://docs.python.org/3/library/os.path.html#os.path.expandvars) function.

A good use case is reading config files with the flexibility of reading values from environment variables using advanced features like returning a default value if some variable is not defined.
For example:

```toml
[default]
my_secret_access_code = "${ACCESS_CODE:-default_access_code}"
my_important_variable = "${IMPORTANT_VARIABLE:?}"
my_updated_path = "$PATH:$HOME/.bin"
my_process_id = "$$"
my_nested_variable = "${!NESTED}"
```

> NOTE: Although this module copies most of the common behaviours of bash,
> it doesn't follow bash strictly. For example, it doesn't work with arrays.

## Installation

### Pip

```
pip install expandvars
```

### Conda

```
conda install -c conda-forge expandvars
```

## Usage

```python
from expandvars import expandvars

print(expandvars("$PATH:${HOME:?}/bin:${SOME_UNDEFINED_PATH:-/default/path}"))
# /bin:/sbin:/usr/bin:/usr/sbin:/home/you/bin:/default/path
```

## Examples

For now, [refer to the test cases](https://github.com/sayanarijit/expandvars/blob/master/tests) to see how it behaves.

## TIPs

### nounset=True

If you want to enable strict parsing by default, (similar to `set -u` / `set -o nounset` in bash), pass `nounset=True`.

```python
# All the variables must be defined.
expandvars("$VAR1:${VAR2}:$VAR3", nounset=True)

# Raises UnboundVariable error.
```

> NOTE: Another way is to use the `${VAR?}` or `${VAR:?}` syntax. See the examples in tests.

### EXPANDVARS_RECOVER_NULL="foo"

If you want to temporarily disable strict parsing both for `nounset=True` and the `${VAR:?}` syntax, set environment variable `EXPANDVARS_RECOVER_NULL=somevalue`.
This helps with certain use cases where you need to temporarily disable strict parsing of critical env vars, e.g. in testing environment, without modifying the code.

e.g.

```bash
EXPANDVARS_RECOVER_NULL=foo myapp --config production.ini && echo "All fine."
```

> WARNING: Try to avoid `export EXPANDVARS_RECOVER_NULL` because that will disable strict parsing permanently until you log out.

### Customization

You can customize the variable symbol and data used for the expansion by using the more general `expand` function.

```python
from expandvars import expand

print(expand("%PATH:$HOME/bin:%{SOME_UNDEFINED_PATH:-/default/path}", environ={"PATH": "/example"}, var_symbol="%"))
# /example:$HOME/bin:/default/path
```

## Contributing

To contribute, setup environment following way:

Then

```bash
# Clone repo
git clone https://github.com/sayanarijit/expandvars && cd expandvars

# Setup virtualenv
python -m venv .venv
source ./.venv/bin/activate

# Install as editable including test dependencies
pip install -e ".[tests]"
```

- Follow [general git guidelines](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project).
- Keep it simple. Run `black .` to auto format the code.
- Test your changes locally by running `pytest` (pass `--cov --cov-report html` for browsable coverage report).
- If you are familiar with [tox](https://tox.readthedocs.io), you may want to use it for testing in different python versions.

## Alternatives

- [environs](https://github.com/sloria/environs) - simplified environment variable parsing.
