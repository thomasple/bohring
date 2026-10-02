"""Immutable unit values and the built-in SI registry."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType
from typing import Mapping

from hartreez.dimensions import Dimensions


@dataclass(frozen=True, slots=True)
class Unit:
    """A positive scale relative to SI and its physical dimensions."""

    scale: float
    dimensions: Dimensions

    def __post_init__(self) -> None:
        scale = float(self.scale)
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("unit scale must be a positive finite number")
        if type(self.dimensions) is not Dimensions:
            raise TypeError("dimensions must be a Dimensions value")
        object.__setattr__(self, "scale", scale)

    def __mul__(self, other: Unit) -> Unit:
        if type(other) is not Unit:
            return NotImplemented
        return Unit(self.scale * other.scale, self.dimensions * other.dimensions)

    def __truediv__(self, other: Unit) -> Unit:
        if type(other) is not Unit:
            return NotImplemented
        return Unit(self.scale / other.scale, self.dimensions / other.dimensions)

    def __pow__(self, exponent: int | float | str | Fraction) -> Unit:
        power = Fraction(str(exponent)) if isinstance(exponent, float) else Fraction(exponent)
        return Unit(self.scale**float(power), self.dimensions**power)


DIMENSIONLESS = Dimensions()
MASS = Dimensions(mass=1)
LENGTH = Dimensions(length=1)
TIME = Dimensions(time=1)
CHARGE = Dimensions(charge=1)
TEMPERATURE = Dimensions(temperature=1)

# Scales use exact SI definitions where available. This first registry is
# deliberately small; later releases can add names without changing parsing.
_REGISTRY: dict[str, Unit] = {
    "1": Unit(1.0, DIMENSIONLESS),
    "kg": Unit(1.0, MASS),
    "g": Unit(1e-3, MASS),
    "m": Unit(1.0, LENGTH),
    "cm": Unit(1e-2, LENGTH),
    "mm": Unit(1e-3, LENGTH),
    "km": Unit(1e3, LENGTH),
    "s": Unit(1.0, TIME),
    "ms": Unit(1e-3, TIME),
    "us": Unit(1e-6, TIME),
    "ns": Unit(1e-9, TIME),
    "min": Unit(60.0, TIME),
    "h": Unit(3600.0, TIME),
    "C": Unit(1.0, CHARGE),
    "K": Unit(1.0, TEMPERATURE),
    "J": Unit(1.0, MASS * (LENGTH**2) / (TIME**2)),
    "N": Unit(1.0, MASS * LENGTH / (TIME**2)),
    "Pa": Unit(1.0, MASS / LENGTH / (TIME**2)),
}
UNIT_REGISTRY: Mapping[str, Unit] = MappingProxyType(_REGISTRY)


def unit_names() -> tuple[str, ...]:
    """Return the registered unit names in stable alphabetical order."""

    return tuple(sorted(UNIT_REGISTRY))
