"""Immutable unit values and the curated atomistic/MD registry."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType
from typing import Mapping

from hartreez import constants
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
ENERGY = MASS * (LENGTH**2) / (TIME**2)
FORCE = MASS * LENGTH / (TIME**2)
PRESSURE = MASS / LENGTH / (TIME**2)
DIPOLE = CHARGE * LENGTH
FREQUENCY = Dimensions(time=-1)


def _unit(scale: float, dimensions: Dimensions) -> Unit:
    return Unit(scale, dimensions)


_CANONICAL: dict[str, Unit] = {
    "1": _unit(1.0, DIMENSIONLESS),
    "kg": _unit(1.0, MASS),
    "g": _unit(1e-3, MASS),
    "Da": _unit(constants.M_U, MASS),
    "m": _unit(1.0, LENGTH),
    "cm": _unit(1e-2, LENGTH),
    "mm": _unit(1e-3, LENGTH),
    "km": _unit(1e3, LENGTH),
    "nm": _unit(1e-9, LENGTH),
    "angstrom": _unit(1e-10, LENGTH),
    "bohr": _unit(constants.BOHR_RADIUS, LENGTH),
    "s": _unit(1.0, TIME),
    "ms": _unit(1e-3, TIME),
    "us": _unit(1e-6, TIME),
    "ns": _unit(1e-9, TIME),
    "ps": _unit(1e-12, TIME),
    "fs": _unit(1e-15, TIME),
    "atomic_time": _unit(constants.ATOMIC_TIME, TIME),
    "C": _unit(1.0, CHARGE),
    "e": _unit(constants.E_CHARGE, CHARGE),
    "K": _unit(1.0, TEMPERATURE),
    "J": _unit(1.0, ENERGY),
    "eV": _unit(constants.E_CHARGE, ENERGY),
    "meV": _unit(constants.E_CHARGE * 1e-3, ENERGY),
    "Hartree": _unit(constants.HARTREE_ENERGY, ENERGY),
    "Rydberg": _unit(constants.RYDBERG_ENERGY, ENERGY),
    "cal": _unit(4.184, ENERGY),
    "kcal": _unit(4184.0, ENERGY),
    "kJ": _unit(1000.0, ENERGY),
    "Hz": _unit(1.0, FREQUENCY),
    "THz": _unit(1e12, FREQUENCY),
    "cm1": _unit(constants.SPECTROSCOPIC_CM1, FREQUENCY),
    "Pa": _unit(1.0, PRESSURE),
    "bar": _unit(1e5, PRESSURE),
    "kbar": _unit(1e8, PRESSURE),
    "atm": _unit(101325.0, PRESSURE),
    "GPa": _unit(1e9, PRESSURE),
    "N": _unit(1.0, FORCE),
    "nN": _unit(1e-9, FORCE),
    "D": _unit(constants.DEBYE, DIPOLE),
    # In this package mol means Avogadro's multiplicity, so mol is
    # dimensionless and its scale is a particle count.
    "mol": _unit(constants.N_A, DIMENSIONLESS),
    "min": _unit(60.0, TIME),
    "h": _unit(3600.0, TIME),
}

# Each alias maps to a canonical entry above. Keep this list explicit; units
# are case-sensitive and no prefix inference takes place.
_ALIASES: dict[str, str] = {
    "meter": "m",
    "centimeter": "cm",
    "kilometer": "km",
    "nanometer": "nm",
    "Å": "angstrom",
    "Angstrom": "angstrom",
    "a0": "bohr",
    "a_0": "bohr",
    "second": "s",
    "femtosecond": "fs",
    "picosecond": "ps",
    "nanosecond": "ns",
    "atomic_unit_of_time": "atomic_time",
    "aut": "atomic_time",
    "coulomb": "C",
    "elementary_charge": "e",
    "kelvin": "K",
    "joule": "J",
    "electronvolt": "eV",
    "Hartree_energy": "Hartree",
    "Ha": "Hartree",
    "Ry": "Rydberg",
    "cal_th": "cal",
    "kcal_th": "kcal",
    "kilocalorie": "kcal",
    "kilojoule": "kJ",
    "atomic_mass_unit": "Da",
    "amu": "Da",
    "u": "Da",
    "hertz": "Hz",
    "terahertz": "THz",
    "pascal": "Pa",
    "atmosphere": "atm",
    "newton": "N",
    "debye": "D",
}

def _build_registry() -> Mapping[str, Unit]:
    registry = dict(_CANONICAL)
    for alias, canonical_name in _ALIASES.items():
        registry[alias] = _CANONICAL[canonical_name]
    return MappingProxyType(registry)


UNIT_REGISTRY: Mapping[str, Unit] = _build_registry()


def unit_names() -> tuple[str, ...]:
    """Return all registered canonical spellings and aliases alphabetically."""

    return tuple(sorted(UNIT_REGISTRY))


def canonical_unit_names() -> tuple[str, ...]:
    """Return the curated canonical unit spellings alphabetically."""

    return tuple(sorted(_CANONICAL))


def unit_aliases() -> Mapping[str, str]:
    """Return the read-only mapping from aliases to canonical unit spellings."""

    return MappingProxyType(_ALIASES)
