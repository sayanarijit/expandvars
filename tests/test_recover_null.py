# -*- coding: utf-8 -*-

import importlib
from os import environ as env
from unittest.mock import patch

import expandvars


@patch.dict(env, {"EXPANDVARS_RECOVER_NULL": "foo"})
def test_strict_parsing_recover_null():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:?}") == "foo"
    assert expandvars.expandvars("${FOO:?custom err}") == "foo"
