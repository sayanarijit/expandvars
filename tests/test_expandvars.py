# -*- coding: utf-8 -*-

import importlib
from os import environ as env, getpid
from unittest.mock import patch

import expandvars
import pytest


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


@patch.dict(env, {"FOO": "bar"})
def test_expandvars_from_file():
    importlib.reload(expandvars)

    with open("tests/data/foo.txt") as f:
        assert expandvars.expandvars(f) == "bar:bar"


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
def test_expandvars_pid():
    importlib.reload(expandvars)

    assert expandvars.expandvars("$$") == str(getpid())
    assert expandvars.expandvars("PID( $$ )") == "PID( {0} )".format(getpid())


@patch.dict(env, {})
def test_expandvars_get_default():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO-default}") == "default"
    assert expandvars.expandvars("${FOO:-default}") == "default"
    assert expandvars.expandvars("${FOO:-}") == ""
    assert expandvars.expandvars("${FOO:-foo}:${FOO-bar}") == "foo:bar"


@patch.dict(env, {})
def test_expandvars_update_default():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:=}") == ""
    assert expandvars.expandvars("${FOO=}") == ""

    del env["FOO"]

    assert expandvars.expandvars("${FOO:=default}") == "default"
    assert expandvars.expandvars("${FOO=default}") == "default"
    assert env.get("FOO") == "default"
    assert expandvars.expandvars("${FOO:=ignoreme}") == "default"
    assert expandvars.expandvars("${FOO=ignoreme}:bar") == "default:bar"


@patch.dict(env, {"FOO": "bar", "BUZ": "bar"})
def test_expandvars_substitute():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:+foo}") == "foo"
    assert expandvars.expandvars("${FOO+foo}") == "foo"
    assert expandvars.expandvars("${BAR:+foo}") == ""
    assert expandvars.expandvars("${BAR+foo}") == ""
    assert expandvars.expandvars("${BAR:+}") == ""
    assert expandvars.expandvars("${BAR+}") == ""
    assert expandvars.expandvars("${BUZ:+foo}") == "foo"
    assert expandvars.expandvars("${BUZ+foo}:bar") == "foo:bar"


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_offset():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:3}") == "nbigfoobar"
    assert expandvars.expandvars("${FOO: 4 }") == "bigfoobar"
    assert expandvars.expandvars("${FOO:30}") == ""
    assert expandvars.expandvars("${FOO:0}") == "damnbigfoobar"
    assert expandvars.expandvars("${FOO:-3}:bar") == "damnbigfoobar:bar"


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_offset_length():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:4:3}") == "big"
    assert expandvars.expandvars("${FOO: 7:6 }") == "foobar"
    assert expandvars.expandvars("${FOO:7: 100 }") == "foobar"
    assert expandvars.expandvars("${FOO:0:100}") == "damnbigfoobar"
    assert expandvars.expandvars("${FOO:70:10}") == ""
    assert expandvars.expandvars("${FOO:1:0}") == ""
    assert expandvars.expandvars("${FOO:0:}") == ""
    assert expandvars.expandvars("${FOO::}") == ""
    assert expandvars.expandvars("${FOO::5}") == "damnb"
    assert expandvars.expandvars("${FOO:-3:1}:bar") == "damnbigfoobar:bar"


@patch.dict(env, {"FOO": "X", "X": "foo"})
def test_expandvars_indirection():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${!FOO}:${FOO}") == "foo:X"
    assert expandvars.expandvars("${!FOO-default}") == "foo"
    assert expandvars.expandvars("${!BAR-default}") == "default"
    assert expandvars.expandvars("${!X-default}") == "default"


@patch.dict(env, {"FOO": "foo", "BAR": "bar"})
def test_escape():
    importlib.reload(expandvars)

    assert expandvars.expandvars("\\$FOO\\$BAR") == "$FOO$BAR"
    assert expandvars.expandvars("\\\\$FOO") == "\\foo"
    assert expandvars.expandvars("$FOO\\$BAR") == "foo$BAR"
    assert expandvars.expandvars("\\$FOO$BAR") == "$FOObar"
    assert expandvars.expandvars("$FOO" "\\" "\\" "\\" "$BAR") == ("foo" "\\" "$BAR")
    assert expandvars.expandvars("$FOO\\$") == "foo$"
    assert expandvars.expandvars("$\\FOO") == "$\\FOO"
    assert expandvars.expandvars("$\\$FOO") == "$$FOO"
    assert expandvars.expandvars("\\$FOO") == "$FOO"
    assert (
        expandvars.expandvars("D:\\\\some\\windows\\path")
        == "D:\\\\some\\windows\\path"
    )


@patch.dict(env, {})
def test_corner_cases():
    importlib.reload(expandvars)

    assert expandvars.expandvars("${FOO:-{}}{}{}{}{{}}") == "{}{}{}{}{{}}"
    assert expandvars.expandvars("${FOO-{}}{}{}{}{{}}") == "{}{}{}{}{{}}"


@patch.dict(env, {})
def test_strict_parsing():
    importlib.reload(expandvars)

    with pytest.raises(
        expandvars.ExpandvarsException, match="FOO: parameter null or not set"
    ) as e:
        expandvars.expandvars("${FOO:?}")
    assert isinstance(e.value, expandvars.ParameterNullOrNotSet)

    with pytest.raises(
        expandvars.ExpandvarsException, match="FOO: parameter null or not set"
    ) as e:
        expandvars.expandvars("${FOO?}")
    assert isinstance(e.value, expandvars.ParameterNullOrNotSet)

    with pytest.raises(expandvars.ExpandvarsException, match="FOO: custom error") as e:
        expandvars.expandvars("${FOO:?custom error}")
    assert isinstance(e.value, expandvars.ParameterNullOrNotSet)

    with pytest.raises(expandvars.ExpandvarsException, match="FOO: custom error") as e:
        expandvars.expandvars("${FOO?custom error}")
    assert isinstance(e.value, expandvars.ParameterNullOrNotSet)

    env.update({"FOO": "foo"})

    assert expandvars.expandvars("${FOO:?custom err}") == "foo"
    assert expandvars.expandvars("${FOO?custom err}:bar") == "foo:bar"


@patch.dict(env, {"FOO": "foo"})
def test_missing_escapped_character():
    importlib.reload(expandvars)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("$FOO\\")

    assert str(e.value) == "$FOO\\: missing escaped character"
    assert isinstance(e.value, expandvars.MissingExcapedChar)


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_invalid_length_err():
    importlib.reload(expandvars)

    with pytest.raises(
        expandvars.ExpandvarsException, match="FOO: -3: substring expression < 0"
    ) as e:
        expandvars.expandvars("${FOO:1:-3}")
    assert isinstance(e.value, expandvars.NegativeSubStringExpression)


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_bad_substitution_err():
    importlib.reload(expandvars)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO:}") == ""
    assert str(e.value) == "${FOO:}: bad substitution"
    assert isinstance(e.value, expandvars.BadSubstitution)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${}") == ""
    assert str(e.value) == "${}: bad substitution"
    assert isinstance(e.value, expandvars.BadSubstitution)


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_brace_never_closed_err():
    importlib.reload(expandvars)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO:")
    assert str(e.value) == "${FOO:: missing '}'"
    assert isinstance(e.value, expandvars.MissingClosingBrace)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO}${BAR")
    assert str(e.value) == "${FOO}${BAR: missing '}'"
    assert isinstance(e.value, expandvars.MissingClosingBrace)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO?")
    assert str(e.value) == "${FOO?: missing '}'"
    assert isinstance(e.value, expandvars.ExpandvarsException)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO:1")
    assert str(e.value) == "${FOO:1: missing '}'"
    assert isinstance(e.value, expandvars.MissingClosingBrace)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO:1:2")
    assert str(e.value) == "${FOO:1:2: missing '}'"
    assert isinstance(e.value, expandvars.MissingClosingBrace)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO+")
    assert str(e.value) == "${FOO+: missing '}'"
    assert isinstance(e.value, expandvars.MissingClosingBrace)

    with pytest.raises(expandvars.ExpandvarsException) as e:
        expandvars.expandvars("${FOO-")
    assert str(e.value) == "${FOO-: missing '}'"
    assert isinstance(e.value, expandvars.MissingClosingBrace)


@patch.dict(env, {"FOO": "damnbigfoobar"})
def test_invalid_operand_err():
    importlib.reload(expandvars)

    oprnds = "@#$%^&*()_'\"\\"

    for o in oprnds:
        with pytest.raises(expandvars.ExpandvarsException) as e:
            expandvars.expandvars("${{FOO:{0}}}".format(o))
        assert str(e.value) == ("FOO: operand expected (error token is {0})").format(
            repr(o)
        )
        assert isinstance(e.value, expandvars.OperandExpected)

        with pytest.raises(expandvars.ExpandvarsException) as e:
            expandvars.expandvars("${{FOO:0:{0}}}".format(o))
        assert str(e.value) == ("FOO: operand expected (error token is {0})").format(
            repr(o)
        )
        assert isinstance(e.value, expandvars.OperandExpected)

        with pytest.raises(expandvars.ExpandvarsException) as e:
            expandvars.expandvars("${{FOO:{0}:{0}}}".format(o))
        assert str(e.value) == ("FOO: operand expected (error token is {0})").format(
            repr(o)
        )
        assert isinstance(e.value, expandvars.OperandExpected)


@pytest.mark.parametrize("var_symbol", ["%", "&", "£", "="])
def test_expand_var_symbol(var_symbol):
    assert (
        expandvars.expand(
            var_symbol + "{FOO}", environ={"FOO": "test"}, var_symbol=var_symbol
        )
        == "test"
    )
    assert (
        expandvars.expand(var_symbol + "FOO", environ={}, var_symbol=var_symbol) == ""
    )
    assert (
        expandvars.expand(
            var_symbol + "{FOO:-default_value}", environ={}, var_symbol=var_symbol
        )
        == "default_value"
    )
    with pytest.raises(expandvars.ParameterNullOrNotSet):
        expandvars.expand(var_symbol + "{FOO:?}", environ={}, var_symbol=var_symbol)

    assert (
        expandvars.expand(
            var_symbol + "{FOO},$HOME", environ={"FOO": "test"}, var_symbol=var_symbol
        )
        == "test,$HOME"
    )
