expandvars
==========
Expand system variables Unix style

[![PyPI version](https://img.shields.io/pypi/v/expandvars.svg)](https://pypi.org/project/expandvars)
[![CircleCI](https://circleci.com/gh/sayanarijit/expandvars/tree/master.svg?style=svg)](https://circleci.com/gh/sayanarijit/expandvars/tree/master)
[![codecov](https://codecov.io/gh/sayanarijit/expandvars/branch/master/graph/badge.svg)](https://codecov.io/gh/sayanarijit/expandvars)


Inspiration
-----------
This module is inspired by [GNU bash's variable expansion features](https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html). It can be used as an alternative to Python's [os.path.expandvars](https://docs.python.org/3/library/os.path.html#os.path.expandvars) function.

A good use case is reading config files with the flexibility of reading values from environment variables using advanced features like returning a default value if some variable is not defined.
For example:

```toml
[default]
my_secret_access_code = "${ACCESS_CODE:-default_access_code}"
```

> NOTE: Although this module copies most of the common behaviours of bash,
> it doesn't follow bash strictly. For example, it doesn't work with arrays.


Usage
-----

```python
from expandvars import expandvars

print(expandvars("$PATH:$HOME/bin:${SOME_UNDEFINED_PATH:-/default/path}"))
# /bin:/sbin:/usr/bin:/usr/sbin:/home/you/bin:/default/path
```


Examples
--------
For now, [refer to the test cases](https://github.com/sayanarijit/expandvars/blob/master/tests) to see how it behaves.


Contributing
------------
To contribute, setup environment following way:

```bash
# Clone repo
git clone https://github.com/sayanarijit/expandvars && cd expandvars

# Create virtualenv
virtualenv .venv && source .venv/bin/activate

# Install library in edit mode along with other handy dev tools
pip install -r dev-requirements.txt
```

- Follow [general git guidelines](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project).
- Keep it simple. Use [black](https://github.com/python/black) to format code.
- Test your changes locally by running `pytest`.
- If you are familiar with [tox](https://tox.readthedocs.io), you may want to use it for testing in different python versions.
