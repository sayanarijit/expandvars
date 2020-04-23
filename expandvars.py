# -*- coding: utf-8 -*-

from os import environ

__author__ = "Arijit Basu"
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/expandvars"
__description__ = "Expand system variables Unix style"
__version__ = "v0.5.1"
__license__ = "MIT"
__all__ = ["expandvars"]


ESCAPE_CHAR = "\\"

# Set EXPANDVARS_RECOVER_NULL="foo" if you want variables with
# `${VAR:?}` syntax to fallback to "foo" if it's not defined.
#
# This helps with certain use cases where you need to temporarily
# disable strict parsing of critical env vars. e.g. in testing
# environment.
#
# See tests/test_recover_null.py for examples.
RECOVER_NULL = environ.get("EXPANDVARS_RECOVER_NULL", None)


class MissingClosingBrace(SyntaxError):
    def __init__(self, param):
        super().__init__("{0}: missing '}}'".format(param))


class MissingExcapedChar(SyntaxError):
    def __init__(self, param):
        super().__init__("{0}: missing escaped character".format(param))


class OperandExpected(SyntaxError):
    def __init__(self, param, operand):
        super().__init__(
            "{0}: operand expected (error token is {1})".format(param, repr(operand))
        )


class NegativeSubStringExpression(IndexError):
    def __init__(self, param, expr):
        super().__init__("{0}: {1}: substring expression < 0".format(param, expr))


class BadSubstitution(SyntaxError):
    def __init__(self, param):
        super().__init__("{0}: bad substitution".format(param))


class ParameterNullOrNotSet(KeyError):
    def __init__(self, param, msg=None):
        if msg is None:
            msg = "parameter null or not set"
        super().__init__("{0}: {1}".format(param, msg))


def _valid_char(char):
    return char.isalnum() or char == "_"


def _isint(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def escape(vars_):
    """Escape the first character."""
    if len(vars_) == 0:
        raise MissingExcapedChar(vars_)

    if len(vars_) == 1:
        return vars_[0]

    if vars_[0] == "$":
        return vars_[0] + expandvars(vars_[1:])

    if vars_[0] == ESCAPE_CHAR:
        if vars_[1] == "$":
            return ESCAPE_CHAR + expand_var(vars_[1:])
        if vars_[1] == ESCAPE_CHAR:
            return ESCAPE_CHAR + escape(vars_[2:])

    return ESCAPE_CHAR + vars_[0] + expandvars(vars_[1:])


def expand_var(vars_):
    """Expand a single variable."""

    if len(vars_) == 0:
        return "$"

    if vars_[0] == ESCAPE_CHAR:
        return "$" + escape(vars_[1:])

    if vars_[0] == "{":
        return expand_modifier_var(vars_[1:])

    buff = []
    for c in vars_:
        if _valid_char(c):
            buff.append(c)
        elif c == "$":
            n = len(buff) + 1
            return environ.get("".join(buff), "") + expand_var(vars_[n:])
        else:
            n = len(buff)
            return environ.get("".join(buff), "") + expandvars(vars_[n:])
    return environ.get("".join(buff), "")


def expand_modifier_var(vars_):
    """Expand variables with modifier."""

    if len(vars_) == 1:
        raise BadSubstitution(vars_)

    buff = []
    for c in vars_:
        if _valid_char(c):
            buff.append(c)
        elif c == "}":
            n = len(buff) + 1
            return environ.get("".join(buff), "") + expandvars(vars_[n:])
        elif c == ":":
            n = len(buff) + 1
            return expand_advanced("".join(buff), vars_[n:])
        else:
            n = len(buff)
            return expand_advanced("".join(buff), vars_[n:])
    raise MissingClosingBrace("".join(buff))


def expand_advanced(var, vars_):
    """Expand substitution."""

    if len(vars_) == 0:
        raise MissingClosingBrace(var)

    if vars_[0] == "-":
        return expand_default(var, vars_[1:])

    if vars_[0] == "=":
        return expand_default(var, vars_[1:], set_=True)

    if vars_[0] == "+":
        return expand_substitute(var, vars_[1:])

    if vars_[0] == "?":
        return expand_strict(var, vars_[1:])

    return expand_offset(var, vars_)


def expand_strict(var, vars_):
    """Expand variable that must be defined."""

    buff = []
    for c in vars_:
        if c == "}":
            n = len(buff) + 1
            val = environ.get(var, "")
            if val:
                return val + expandvars(vars_[n:])
            if RECOVER_NULL is not None:
                return RECOVER_NULL + expandvars(vars_[n:])
            raise ParameterNullOrNotSet(var, "".join(buff) if buff else None)

        buff.append(c)

    raise MissingClosingBrace("".join(buff))


def expand_offset(var, vars_):
    """Expand variable with offset."""

    buff = []
    for c in vars_:
        if c == ":":
            n = len(buff) + 1
            offset_str = "".join(buff)
            if not offset_str:
                offset = None
            elif not _isint(offset_str):
                raise OperandExpected(var, offset_str)
            else:
                offset = int(offset_str)
            return expand_length(var, vars_[n:], offset)

        if c == "}":
            n = len(buff) + 1
            offset_str = "".join(buff).strip()
            if not offset_str:
                raise BadSubstitution(var)
            elif not _isint(offset_str):
                raise OperandExpected(var, offset_str)
            else:
                offset = int(offset_str)
            return environ.get(var, "")[offset:] + expandvars(vars_[n:])
        buff.append(c)
    raise MissingClosingBrace("".join(buff))


def expand_length(var, vars_, offset=None):
    """Expand variable with offset and length."""

    buff = []
    for c in vars_:
        if c == "}":
            n = len(buff) + 1
            length_str = "".join(buff).strip()
            if not length_str:
                length = None
            elif not _isint(length_str):
                raise OperandExpected(var, length_str)
            else:
                length = int(length_str)
                if length < 0:
                    raise NegativeSubStringExpression(var, length_str)

            if length is None:
                width = 0
            elif offset is None:
                width = length
            else:
                width = offset + length

            return environ.get(var, "")[offset:width] + expandvars(vars_[n:])

        buff.append(c)
    raise MissingClosingBrace("".join(buff))


def expand_substitute(var, vars_):
    """Expand or return substitute."""

    sub = []
    for c in vars_:
        if c == "}":
            n = len(sub) + 1
            if var in environ:
                return "".join(sub) + expandvars(vars_[n:])
            return expandvars(vars_[n:])
        sub.append(c)
    raise MissingClosingBrace("".join(sub))


def expand_default(var, vars_, set_=False):
    """Expand var or return default."""

    default = []
    for c in vars_:
        if c == "}":
            n = len(default) + 1
            default_ = "".join(default)
            if set_ and var not in environ:
                environ.update({var: default_})
            return environ.get(var, default_) + expandvars(vars_[n:])
        default.append(c)
    raise MissingClosingBrace("".join(default))


def expandvars(vars_):
    """Expand system variables Unix style.

    Params:
        vars_ (str): System variables to expand.

    Returns:
        str: Expanded values.

    Example usage: ::

        from expandvars import expandvars

        print(expandvars("$PATH:$HOME/bin:${SOME_UNDEFINED_PATH:-/default/path}"))
        # /bin:/sbin:/usr/bin:/usr/sbin:/home/you/bin:/default/path
    """
    if len(vars_) == 0:
        return ""

    buff = []

    try:
        for c in vars_:
            if c == "$":
                n = len(buff) + 1
                return "".join(buff) + expand_var(vars_[n:])

            if c == ESCAPE_CHAR:
                n = len(buff) + 1
                return "".join(buff) + escape(vars_[n:])

            buff.append(c)
        return "".join(buff)
    except MissingExcapedChar:
        raise MissingExcapedChar(vars_)
    except MissingClosingBrace:
        raise MissingClosingBrace(vars_)
    except BadSubstitution:
        raise BadSubstitution(vars_)
