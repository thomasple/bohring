"""Parser for the small, explicit hartreez unit-expression grammar."""

from __future__ import annotations

import re
from functools import lru_cache
from fractions import Fraction

from hartreez.errors import UnitSyntaxError, UnknownUnitError
from hartreez.units import UNIT_REGISTRY, Unit

_TOKEN = re.compile(r"\s*(\*\*|[*/^()]|[A-Za-z_][A-Za-z_0-9]*|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:/[+-]?\d+)?)")


def _tokens(expression: str) -> list[str]:
    result: list[str] = []
    position = 0
    while position < len(expression):
        match = _TOKEN.match(expression, position)
        if match is None:
            raise UnitSyntaxError(f"invalid unit expression at character {position}: {expression!r}")
        result.append(match.group(1))
        position = match.end()
    if not result:
        raise UnitSyntaxError("unit expression must not be empty")
    return result


class _Parser:
    def __init__(self, expression: str) -> None:
        self.expression = expression
        self.tokens = _tokens(expression)
        self.index = 0

    def peek(self) -> str | None:
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise UnitSyntaxError(f"unexpected end of unit expression: {self.expression!r}")
        self.index += 1
        return token

    def parse(self) -> Unit:
        value = self.product()
        if self.peek() is not None:
            raise UnitSyntaxError(f"unexpected token {self.peek()!r} in unit expression {self.expression!r}")
        return value

    def product(self) -> Unit:
        value = self.power()
        while self.peek() in ("*", "/"):
            operator = self.take()
            following = self.peek()
            if following is None or following in ("*", "/", "^", ")"):
                raise UnitSyntaxError(f"missing unit after {operator!r} in {self.expression!r}")
            right = self.power()
            value = value * right if operator == "*" else value / right
        return value

    def power(self) -> Unit:
        value = self.atom()
        if self.peek() in ("^", "**"):
            self.take()
            token = self.peek()
            if token is None:
                raise UnitSyntaxError(f"missing exponent in unit expression {self.expression!r}")
            try:
                exponent = Fraction(self.take())
            except (ValueError, ZeroDivisionError) as error:
                raise UnitSyntaxError(f"invalid exponent {token!r} in unit expression {self.expression!r}") from error
            value = value**exponent
        return value

    def atom(self) -> Unit:
        token = self.take()
        if token == "(":
            value = self.product()
            if self.peek() != ")":
                raise UnitSyntaxError(f"unmatched '(' in unit expression {self.expression!r}")
            self.take()
            return value
        if token == ")":
            raise UnitSyntaxError(f"unexpected ')' in unit expression {self.expression!r}")
        if token in ("*", "/", "^", "**"):
            raise UnitSyntaxError(f"unexpected operator {token!r} in unit expression {self.expression!r}")
        if token == "1":
            return UNIT_REGISTRY["1"]
        if token[0].isdigit() or token[0] in "+-.":
            raise UnitSyntaxError(f"numeric coefficients are not allowed in unit expression {self.expression!r}")
        try:
            return UNIT_REGISTRY[token]
        except KeyError as error:
            raise UnknownUnitError(f"unknown unit {token!r} in expression {self.expression!r}") from error


@lru_cache(maxsize=512)
def parse_unit(expression: str) -> Unit:
    """Parse a registered unit name or unit expression.

    The expression grammar accepts ``*``, ``/``, parentheses, and one ``^``
    (or ``**``) exponent per factor. Exponents are signed integers, finite
    decimals, or signed rational literals such as ``-1/2``. Multiplication
    must be explicit; only ``1`` is accepted as a numeric literal.
    """

    if type(expression) is not str:
        raise TypeError("unit expression must be a string")
    return _Parser(expression).parse()
