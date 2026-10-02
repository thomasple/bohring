"""Public exceptions raised by hartreez."""


class UnitError(ValueError):
    """Base class for invalid unit expressions and conversions."""


class UnitSyntaxError(UnitError):
    """A unit expression is malformed or names an unsupported unit."""


class UnknownUnitError(UnitSyntaxError):
    """A syntactically valid unit name is not in the built-in registry."""


class IncompatibleUnitsError(UnitError):
    """A conversion was requested between different dimensions."""
