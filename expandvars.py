# -*- coding: utf-8 -*-

import os
from io import TextIOWrapper

__author__ = "Arijit Basu"
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/expandvars"
__description__ = "Expand system variables Unix style"
__version__ = "v1.0.0"
__license__ = "MIT"
__all__ = [
    "BadSubstitution",
    "ExpandvarsException",
    "MissingClosingBrace",
    "MissingEscapedChar",
    "NegativeSubStringExpression",
    "OperandExpected",
    "ParameterNullOrNotSet",
    "UnboundVariable",
    "expand",
    "expandvars",
]


ESCAPE_CHAR = "\\"


class ExpandvarsException(Exception):
    """The base exception for all the handleable exceptions."""

    pass


class MissingClosingBrace(ExpandvarsException, SyntaxError):
    def __init__(self, param):
        super().__init__("{0}: missing '}}'".format(param))


class MissingEscapedChar(ExpandvarsException, SyntaxError):
    def __init__(self, param):
        super().__init__("{0}: missing escaped character".format(param))


class OperandExpected(ExpandvarsException, SyntaxError):
    def __init__(self, param, operand):
        super().__init__(
            "{0}: operand expected (error token is {1})".format(param, repr(operand))
        )


class NegativeSubStringExpression(ExpandvarsException, IndexError):
    def __init__(self, param, expr):
        super().__init__("{0}: {1}: substring expression < 0".format(param, expr))


class BadSubstitution(ExpandvarsException, SyntaxError):
    def __init__(self, param):
        super().__init__("{0}: bad substitution".format(param))


class ParameterNullOrNotSet(ExpandvarsException, KeyError):
    def __init__(self, param, msg=None):
        if msg is None:
            msg = "parameter null or not set"
        super().__init__("{0}: {1}".format(param, msg))


class UnboundVariable(ExpandvarsException, KeyError):
    def __init__(self, param):
        super().__init__("{0}: unbound variable".format(param))


class InvalidIndirectExpansion(ExpandvarsException, KeyError):
    def __init__(self, param):
        super().__init__("{0}: invalid indirect expansion".format(param))


def getenv(var, indirect, environ, var_symbol="$"):
    """Get value from environment variable.

    When indirect is True, it will use the value of the resolved variable as
    the name of the final variable.
    """

    if var == var_symbol:
        return str(os.getpid())

    val = environ.get(var)

    if indirect:
        if val is None:
            raise InvalidIndirectExpansion(var)
        else:
            val = getenv(
                val,
                indirect=False,
                environ=environ,
                var_symbol=var_symbol,
            )

    return val


def expand(vars_, nounset=False, environ=os.environ, var_symbol="$"):
    """Expand variables Unix style.

    Params:
        vars_ (str):  Variables to expand.
        nounset (bool): If True, enables strict parsing (similar to set -u / set -o nounset in bash).
        environ (Mapping): Elements to consider during variable expansion. Defaults to os.environ
        var_symbol (str): Character used to identify a variable. Defaults to $

    Returns:
        str: Expanded values.

    Example usage: ::

        from expandvars import expand

        print(expand("%PATH:$HOME/bin:%{SOME_UNDEFINED_PATH:-/default/path}", environ={"PATH": "/example"}, var_symbol="%"))
        # /example:$HOME/bin:/default/path

        # Or
        with open(somefile) as f:
            print(expand(f))
    """
    if isinstance(vars_, TextIOWrapper):
        # This is a file. Read it.
        vars_ = vars_.read()

    if len(vars_) == 0:
        return ""

    buff = []

    vars_iter = _PeekableIterator(vars_)
    try:
        for c in vars_iter:
            if c == ESCAPE_CHAR:
                next_ = vars_iter.peek()
                if next_ == var_symbol or next_ == ESCAPE_CHAR:
                    buff.append(next(vars_iter))
                elif next_ == _PeekableIterator.NOTHING:
                    raise MissingEscapedChar(c)
                else:
                    buff.append(c)
                    buff.append(next(vars_iter))
            elif c == var_symbol:
                next_ = vars_iter.peek()
                if next_ == _PeekableIterator.NOTHING:
                    buff.append(c)
                elif _valid_char(next_) or next_ == "{" or next_ == var_symbol:
                    val = _expand_var(
                        vars_iter,
                        nounset=nounset,
                        environ=environ,
                        var_symbol=var_symbol,
                    )
                    buff.append(val)
                else:
                    buff.append(c)
            else:
                buff.append(c)
        return "".join(buff)
    except MissingEscapedChar:
        raise MissingEscapedChar(vars_)
    except MissingClosingBrace:
        raise MissingClosingBrace(vars_)
    except BadSubstitution:
        raise BadSubstitution(vars_)


def expandvars(vars_, nounset=False):
    """Expand system variables Unix style.

    Params:
        vars_ (str): System variables to expand.
        nounset (bool): If True, enables strict parsing (similar to set -u / set -o nounset in bash).

    Returns:
        str: Expanded values.

    Example usage: ::

        from expandvars import expandvars

        print(expandvars("$PATH:$HOME/bin:${SOME_UNDEFINED_PATH:-/default/path}"))
        # /bin:/sbin:/usr/bin:/usr/sbin:/home/you/bin:/default/path

        # Or
        with open(somefile) as f:
            print(expandvars(f))
    """
    return expand(vars_, nounset=nounset)


class ModifierType:
    GET_DEFAULT = 1
    GET_OR_SET_DEFAULT = 2
    SUBSTITUTE = 3
    OFFSET = 4
    STRICT = 5
    LENGTH = 6


class State:
    READING_VAR = 1
    READING_MODIFIER_VAR = 2
    READING_MODIFIER = 3
    FINISHED_READING = -1


def _read_var(buff, var_symbol):
    name = []
    state = State.READING_VAR
    next_ = buff.peek()
    modifier, modifier_type = [], None
    bracedepth = 0
    indirect = False

    while state != State.FINISHED_READING:

        next_ = buff.peek()

        if next_ == _PeekableIterator.NOTHING:
            if state == State.READING_MODIFIER_VAR or state == State.READING_MODIFIER:
                raise MissingClosingBrace("".join(name))
            else:
                state = State.FINISHED_READING

        elif next_ == "{" and state == State.READING_VAR:
            next(buff)
            if buff.peek() == "!":
                indirect = True
                next(buff)
            elif buff.peek() == "#":
                modifier_type = ModifierType.LENGTH
                next(buff)
            state = State.READING_MODIFIER_VAR

        elif next_ == "}" and state == State.READING_MODIFIER_VAR:
            next(buff)
            state = State.FINISHED_READING

        elif (_valid_char(next_) or (next_ == var_symbol and not name)) and (
            state == State.READING_VAR or state == State.READING_MODIFIER_VAR
        ):
            name.append(next(buff))

        elif next_ == ":" and state == State.READING_MODIFIER_VAR:
            state = State.READING_MODIFIER
            next(buff)

        elif state == State.READING_MODIFIER_VAR or (
            state == State.READING_MODIFIER and modifier_type is None
        ):
            state = State.READING_MODIFIER
            modifier, modifier_type = [], None
            if next_ == "-":
                modifier_type = ModifierType.GET_DEFAULT
            elif next_ == "=":
                modifier_type = ModifierType.GET_OR_SET_DEFAULT
            elif next_ == "+":
                modifier_type = ModifierType.SUBSTITUTE
            elif next_ == "?":
                modifier_type = ModifierType.STRICT
            elif next_ == "}":
                modifier_type = ModifierType.OFFSET
                state = State.FINISHED_READING
            else:
                modifier_type = ModifierType.OFFSET
                modifier.append(next_)
            next(buff)

        elif state == State.READING_MODIFIER:
            c = next(buff)
            if c == "{":
                bracedepth += 1
                modifier.append(c)
            elif c == "}":
                if bracedepth == 0:
                    state = State.FINISHED_READING
                else:
                    modifier.append(c)
                    bracedepth -= 1
            else:
                modifier.append(c)

        elif state == State.READING_VAR:
            state = State.FINISHED_READING

        else:
            # This should never happen
            raise ExpandvarsException("unexpected state")  # pragma: no cover

    var = "".join(name)
    return var, modifier_type, modifier, indirect


def _expand_var(buff, nounset, environ, var_symbol):
    var, modifier_type, modifier, indirect = _read_var(buff, var_symbol=var_symbol)
    if not var:
        raise BadSubstitution("")

    val = getenv(var, indirect=indirect, environ=environ, var_symbol=var_symbol)
    modifier = expand("".join(modifier), environ=environ, var_symbol=var_symbol)

    if modifier_type == ModifierType.LENGTH:
        if modifier:
            raise BadSubstitution(var)
        modified = str(len(val))
    elif modifier_type == ModifierType.GET_DEFAULT:
        modified = val if val else modifier

    elif modifier_type == ModifierType.GET_OR_SET_DEFAULT:
        modified = _modify_get_or_set_default(var, val, modifier, environ=environ)

    elif modifier_type == ModifierType.SUBSTITUTE:
        modified = modifier if val else ""

    elif modifier_type == ModifierType.OFFSET:
        modified = _modify_offset(var, val, modifier)

    elif modifier_type == ModifierType.STRICT:
        modified = _modify_strict(var, val, modifier, environ=environ)

    else:
        modified = val

    if modified is None:
        if nounset:
            recover_null = environ.get("EXPANDVARS_RECOVER_NULL", None)
            if recover_null is None:
                raise UnboundVariable(var)
            else:
                modified = recover_null
        else:
            modified = ""

    return modified


def _modify_get_or_set_default(var, val, modifier, environ):
    if val:
        return val
    else:
        environ[var] = modifier
        return modifier


def _modify_offset(var, val, modifier):
    if not modifier:
        raise BadSubstitution(var)

    split_ = modifier.split(":")

    if len(split_) == 1:
        offset_str, length_str = split_[0].strip(), None
    elif len(split_) == 2:
        offset_str, length_str = (s.strip() for s in split_)
    else:
        raise BadSubstitution(var)

    if _isint(offset_str):
        offset = int(offset_str)
    else:
        offset = 0

    if length_str is None:
        length = None
    elif not _isint(length_str):
        if not all(_valid_char(c) for c in length_str):
            raise OperandExpected(var, length_str)
        else:
            length = 0
    else:
        length = int(length_str)
        if length < 0:
            raise NegativeSubStringExpression(var, length_str)

    width = offset + length if length is not None else None
    return val[offset:width]


def _modify_strict(var, val, modifier, environ):
    if val:
        return val

    recover_null = environ.get("EXPANDVARS_RECOVER_NULL", None)
    if recover_null is not None:
        return recover_null
    raise ParameterNullOrNotSet(var, modifier if modifier else None)


def _valid_char(char):
    return char.isalnum() or char == "_"


def _isint(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


class _PeekableIterator:
    """Peekable iterator."""

    NOTHING = object()

    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self._next = self.NOTHING

    def __iter__(self):
        return self

    def __next__(self):
        if self._next is self.NOTHING:
            return next(self.iterator)
        else:
            next_ = self._next
            self._next = self.NOTHING
            return next_

    def peek(self):
        """Peek at the next item."""
        if self._next is self.NOTHING:
            self._next = next(self.iterator, self.NOTHING)
        return self._next
