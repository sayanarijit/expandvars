# -*- coding: utf-8 -*-

from os import environ as env

import importlib
import pytest
from unittest.mock import patch

import expandvars


@patch.dict(env, {})
def test_expandvars_constant():
    importlib.reload(expandvars)

    assert expandvars.expandvars("FOO") == "FOO"
    assert expandvars.expandvars("$") == "$"
    assert expandvars.expandvars("BAR$") == "BAR$"


@patch.dict(env, {})
def test_expandvars_empty():
    importlib.reload(expandvars)

    assert expandvars.expandvars("") == ""
    assert expandvars.expandvars("$FOO") == ""


@patch.dict(env, {"FOO": "bar"})
def test_expandvars_simple():
    importlib.reload(expandvars)

    assert expandvars.expandvars("$FOO") == "bar"
    assert expandvars.expandvars("${FOO}") == "bar"


@patch.dict(env, {"FOO": "bar", "BIZ": "buz"})
def test_expandvars_combo():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO}:$BIZ") == "bar:buz"
    assert expandvars.expandvars("$FOO$BIZ") == "barbuz"
    assert expandvars.expandvars("${FOO}$BIZ") == "barbuz"
    assert expandvars.expandvars("$FOO${BIZ}") == "barbuz"
    assert expandvars.expandvars("$FOO-$BIZ") == "bar-buz"
    assert expandvars.expandvars("boo$BIZ") == "boobuz"
    assert expandvars.expandvars("boo${BIZ}") == "boobuz"


@patch.dict(env, {})
def test_expandvars_get_default():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:-default}") == "default"
    assert expandvars.expandvars("${FOO:-}") == ""


@patch.dict(env, {})
def test_expandvars_update_default():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:=}") == ""

    del env["FOO"]

    assert expandvars.expandvars("${FOO:=default}") == "default"
    assert env.get("FOO") == "default"
    assert expandvars.expandvars("${FOO:=ignoreme}") == "default"


@patch.dict(env, {"FOO": "bar"})
def test_expandvars_substitute():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:+foo}") == "foo"
    assert expandvars.expandvars("${BAR:+foo}") == ""
    assert expandvars.expandvars("${BAR:+}") == ""


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_offset():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:3}") == "nbigfoobar"
    assert expandvars.expandvars("${FOO: 4}") == "bigfoobar"
    assert expandvars.expandvars("${FOO:30}") == ""
    assert expandvars.expandvars("${FOO:0}") == "damnbigfoobar"
    assert expandvars.expandvars("${FOO:foo}") == "damnbigfoobar"


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_offset_length():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:4:3}") == "big"
    assert expandvars.expandvars("${FOO: 7:6}") == "foobar"
    assert expandvars.expandvars("${FOO:7: 100}") == "foobar"
    assert expandvars.expandvars("${FOO:0:100}") == "damnbigfoobar"
    assert expandvars.expandvars("${FOO:70:10}") == ""
    assert expandvars.expandvars("${FOO:1:0}") == ""
    assert expandvars.expandvars("${FOO:0:}") == ""
    assert expandvars.expandvars("${FOO:0:foo}") == ""
    assert expandvars.expandvars("${FOO::}") == ""
    assert expandvars.expandvars("${FOO::5}") == "damnb"


@patch.dict(env, {"FOO": "foo", "BAR": "bar"})
def test_escape():
    importlib.reload(expandvars)

    assert expandvars.expandvars("\\$FOO\\$BAR") == "$FOO$BAR"
    assert expandvars.expandvars("$FOO\\$BAR") == "foo$BAR"
    assert expandvars.expandvars("\\$FOO$BAR") == "$FOObar"
    assert expandvars.expandvars("$FOO" "\\" "\\" "\\" "$BAR") == (
        "foo" "\\" "\\" "$BAR"
    )
    assert expandvars.expandvars("$FOO\\$") == "foo$"
    assert expandvars.expandvars("$\\FOO") == "$\\FOO"
    assert expandvars.expandvars("\\$FOO") == "$FOO"
    assert expandvars.expandvars("D:\\some\\windows\\path") == "D:\\some\\windows\\path"


@patch.dict(env, {})
def test_corner_cases():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:-{}}{}{}{}{{}}") == "{}{}{}{}{{}}"


@patch.dict(env, {})
def test_strict_parsing():
    importlib.reload(expandvars)

    with pytest.raises(ValueError, match="FOO: parameter null or not set"):
        expandvars.expandvars("${FOO:?}")

    with pytest.raises(ValueError, match="FOO: custom error"):
        expandvars.expandvars("${FOO:?custom error}")

    env.update({"FOO": "foo"})

    assert expandvars.expandvars("${FOO:?custom err}") == "foo"


@patch.dict(env, {"FOO": "foo"})
def test_escape_not_followed_err():
    importlib.reload(expandvars)

    with pytest.raises(ValueError, match="escape character is not escaping anything"):
        expandvars.expandvars("$FOO\\")


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_invalid_length_err():
    importlib.reload(expandvars)

    with pytest.raises(ValueError, match="-3: substring expression < 0") as e:
        expandvars.expandvars("${FOO:1:-3}")


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_bad_syntax_err():
    importlib.reload(expandvars)

    with pytest.raises(ValueError, match="bad substitution") as e:
        expandvars.expandvars("${FOO:}") == ""


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_brace_never_closed_err():
    importlib.reload(expandvars)

    with pytest.raises(ValueError) as e:
        expandvars.expandvars("${FOO:")
    assert str(e.value) == "${FOO:: '{' was never closed."

    with pytest.raises(ValueError) as e:
        expandvars.expandvars("${FOO}${BAR")
    assert str(e.value) == "${BAR: '{' was never closed."


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_invalid_operand_err():
    importlib.reload(expandvars)

    oprnds = "@#$%^&*()_'\"\\"

    for o in oprnds:
        with pytest.raises(ValueError) as e:
            expandvars.expandvars("${{FOO:{}}}".format(o))
        assert str(e.value) == (
            "{0}: syntax error: operand expected (error token is {1})"
        ).format(o, repr(o))

        with pytest.raises(ValueError) as e:
            expandvars.expandvars("${{FOO:0:{}}}".format(o))
        assert str(e.value) == (
            "{0}: syntax error: operand expected (error token is {1})"
        ).format(o, repr(o))
