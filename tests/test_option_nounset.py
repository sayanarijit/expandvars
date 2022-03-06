# -*- coding: utf-8 -*-

import importlib
from os import environ as env
from unittest.mock import patch

import pytest

import expandvars


@patch.dict(env, {}, clear=True)
def test_expandvars_option_nounset():
    importlib.reload(expandvars)

    assert expandvars.expandvars("$FOO") == ""

    with pytest.raises(
        expandvars.ExpandvarsException, match="FOO: unbound variable"
    ) as e:
        expandvars.expandvars("$FOO", nounset=True)

    assert isinstance(e.value, expandvars.UnboundVariable)

    with pytest.raises(
        expandvars.ExpandvarsException, match="FOO: unbound variable"
    ) as e:
        expandvars.expandvars("${FOO}", nounset=True)

    assert isinstance(e.value, expandvars.UnboundVariable)


@patch.dict(env, {}, clear=True)
def test_expandvars_option_nounset_with_strict():
    importlib.reload(expandvars)

    with pytest.raises(
        expandvars.ExpandvarsException, match="FOO: parameter null or not set"
    ) as e:
        assert expandvars.expandvars("${FOO:?}", nounset=True)

    assert isinstance(e.value, expandvars.ParameterNullOrNotSet)
