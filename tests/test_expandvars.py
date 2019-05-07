import os

import pytest

from expandvars import expandvars


def test_expandvars_constant():
    assert expandvars("FOO") == "FOO"
    assert expandvars("$") == "$"
    assert expandvars("BAR$") == "BAR$"


def test_expandvars_empty():
    if "FOO" in os.environ:
        del os.environ["FOO"]
    assert expandvars("") == ""
    assert expandvars("$FOO") == ""


def test_expandvars_simple():
    os.environ.update({"FOO": "bar"})
    assert expandvars("$FOO") == "bar"
    assert expandvars("${FOO}") == "bar"


def test_expandvars_combo():
    os.environ.update({"FOO": "bar", "BIZ": "buz"})
    assert expandvars("${FOO}:$BIZ") == "bar:buz"
    assert expandvars("$FOO$BIZ") == "barbuz"
    assert expandvars("${FOO}$BIZ") == "barbuz"
    assert expandvars("$FOO${BIZ}") == "barbuz"
    assert expandvars("$FOO-$BIZ") == "bar-buz"
    assert expandvars("boo$BIZ") == "boobuz"
    assert expandvars("boo${BIZ}") == "boobuz"


def test_expandvars_get_default():
    if "FOO" in os.environ:
        del os.environ["FOO"]
    assert expandvars("${FOO:-default}") == "default"
    assert expandvars("${FOO:-}") == ""


def test_expandvars_update_default():
    if "FOO" in os.environ:
        del os.environ["FOO"]
    assert expandvars("${FOO:=}") == ""
    del os.environ["FOO"]
    assert expandvars("${FOO:=default}") == "default"
    assert os.environ.get("FOO") == "default"
    assert expandvars("${FOO:=ignoreme}") == "default"


def test_expandvars_substitute():
    if "BAR" in os.environ:
        del os.environ["BAR"]
    os.environ.update({"FOO": "bar"})
    assert expandvars("${FOO:+foo}") == "foo"
    assert expandvars("${BAR:+foo}") == ""
    assert expandvars("${BAR:+}") == ""


def test_offset():
    os.environ.update({"FOO": "damnbigfoobar"})
    assert expandvars("${FOO:3}") == "nbigfoobar"
    assert expandvars("${FOO: 4}") == "bigfoobar"
    assert expandvars("${FOO:30}") == ""
    assert expandvars("${FOO:0}") == "damnbigfoobar"
    assert expandvars("${FOO:foo}") == "damnbigfoobar"


def test_offset_length():
    os.environ.update({"FOO": "damnbigfoobar"})
    assert expandvars("${FOO:4:3}") == "big"
    assert expandvars("${FOO: 7:6}") == "foobar"
    assert expandvars("${FOO:7: 100}") == "foobar"
    assert expandvars("${FOO:0:100}") == "damnbigfoobar"
    assert expandvars("${FOO:70:10}") == ""
    assert expandvars("${FOO:1:0}") == ""
    assert expandvars("${FOO:0:}") == ""
    assert expandvars("${FOO:0:foo}") == ""
    assert expandvars("${FOO::}") == ""
    assert expandvars("${FOO::5}") == "damnb"


def test_escape():
    os.environ.update({"FOO": "foo"})
    assert expandvars("$FOO\\" + "$bar") == "foo$bar"
    assert expandvars("$FOO\\" + "\\" + "\\" + "$bar") == "foo" + "\\" + "$bar"
    assert expandvars("$FOO\\" + "$") == "foo$"
    assert expandvars("$\\" + "FOO") == "$\\" + "FOO"
    assert expandvars("\\" + "$FOO") == "$FOO"


def test_escape_not_followed_err():
    os.environ.update({"FOO": "foo"})
    with pytest.raises(ValueError) as e:
        expandvars("$FOO\\")
    assert str(e.value) == "escape chracter is not escaping anything"


def test_invalid_length_err():
    os.environ.update({"FOO": "damnbigfoobar"})
    with pytest.raises(ValueError) as e:
        expandvars("${FOO:1:-3}")
    assert str(e.value) == "-3: substring expression < 0"


def test_bad_syntax_err():
    os.environ.update({"FOO": "damnbigfoobar"})
    with pytest.raises(ValueError) as e:
        expandvars("${FOO:}") == ""
    assert str(e.value) == "bad substitution"


def test_brace_never_closed_err():
    os.environ.update({"FOO": "damnbigfoobar"})
    with pytest.raises(ValueError) as e:
        expandvars("${FOO:")
    assert str(e.value) == "${FOO:: '{' was never closed."
    with pytest.raises(ValueError) as e:
        expandvars("${FOO}${BAR")
    assert str(e.value) == "${BAR: '{' was never closed."


def test_invalid_operand_err():
    os.environ = {"FOO": "damnbigfoobar"}
    oprnds = "@#$%^&*()_'\"\\"
    for o in oprnds:
        with pytest.raises(ValueError) as e:
            expandvars("${{FOO:{}}}".format(o))
        assert str(e.value) == (
            "{}: syntax error: operand expected (error token is {})"
        ).format(o, repr(o))

        with pytest.raises(ValueError) as e:
            expandvars("${{FOO:0:{}}}".format(o))
        assert str(e.value) == (
            "{}: syntax error: operand expected (error token is {})"
        ).format(o, repr(o))
