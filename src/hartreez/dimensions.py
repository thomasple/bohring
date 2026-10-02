"""Exact physical dimensions for the five independent hartreez dimensions."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
def _fraction(value: int | float | str | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    return Fraction(value)


@dataclass(frozen=True, slots=True, init=False)
class Dimensions:
    """Exponents of mass, length, time, charge, and temperature.

    Exponents are normalized to :class:`fractions.Fraction`, so dimensional
    equality is exact even when units are raised to fractional powers.
    """

    mass: Fraction = Fraction(0)
    length: Fraction = Fraction(0)
    time: Fraction = Fraction(0)
    charge: Fraction = Fraction(0)
    temperature: Fraction = Fraction(0)

    def __init__(
        self,
        mass: int | float | str | Fraction = 0,
        length: int | float | str | Fraction = 0,
        time: int | float | str | Fraction = 0,
        charge: int | float | str | Fraction = 0,
        temperature: int | float | str | Fraction = 0,
    ) -> None:
        object.__setattr__(self, "mass", _fraction(mass))
        object.__setattr__(self, "length", _fraction(length))
        object.__setattr__(self, "time", _fraction(time))
        object.__setattr__(self, "charge", _fraction(charge))
        object.__setattr__(self, "temperature", _fraction(temperature))

    def __mul__(self, other: Dimensions) -> Dimensions:
        if type(other) is not Dimensions:
            return NotImplemented
        return Dimensions(*(a + b for a, b in zip(self._exponents(), other._exponents())))

    def __truediv__(self, other: Dimensions) -> Dimensions:
        if type(other) is not Dimensions:
            return NotImplemented
        return Dimensions(*(a - b for a, b in zip(self._exponents(), other._exponents())))

    def __pow__(self, exponent: int | float | str | Fraction) -> Dimensions:
        power = _fraction(exponent)
        return Dimensions(*(value * power for value in self._exponents()))

    def _exponents(self) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction]:
        return self.mass, self.length, self.time, self.charge, self.temperature

    def __str__(self) -> str:
        labels = ("M", "L", "T", "Q", "Θ")
        terms = [f"{label}^{value}" for label, value in zip(labels, self._exponents()) if value]
        return "1" if not terms else " ".join(terms)
