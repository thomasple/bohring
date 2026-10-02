"""Optional-free metadata for declaring a field's physical dimensionality."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hartreez.dimensions import Dimensions
from hartreez.parser import parse_unit


@dataclass(frozen=True, slots=True, init=False)
class UnitDimension:
    """Declare the expected dimensionality of a field using a unit expression.

    The expression supplies dimensional semantics only. Its scale does not
    select the field's output units; values are normalized into the active
    :class:`~hartreez.systems.UnitSystem` at an input boundary.

    ``UnitDimension`` is core metadata and does not import Pydantic.
    """

    expression: str
    dimensions: Dimensions = field(init=False)

    def __init__(self, expression: str) -> None:
        raw_expression: Any = expression
        if not isinstance(raw_expression, str):
            raise TypeError("UnitDimension expression must be a unit expression string")
        unit = parse_unit(raw_expression)
        object.__setattr__(self, "expression", raw_expression)
        object.__setattr__(self, "dimensions", unit.dimensions)
