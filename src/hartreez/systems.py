"""Coherent, immutable working unit systems."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from hartreez import constants
from hartreez.dimensions import Dimensions
from hartreez.errors import UnitSystemError
from hartreez.parser import parse_unit
from hartreez.units import CHARGE, ENERGY, LENGTH, MASS, TEMPERATURE, TIME, Unit


def _resolve_unit(value: str | Unit, name: str, expected: Dimensions) -> Unit:
    unit = parse_unit(value) if isinstance(value, str) else value
    if type(unit) is not Unit:
        raise UnitSystemError(f"{name} must be a unit expression or Unit")
    if unit.dimensions != expected:
        raise UnitSystemError(
            f"{name} must have dimensions {expected}; got {unit.dimensions}"
        )
    return unit


@dataclass(frozen=True, slots=True, init=False)
class UnitSystem:
    """An immutable coherent working system defined by three mechanical units.

    Supply exactly three of ``length``, ``time``, ``energy``, and ``mass``.
    The missing unit is derived from ``E = M L^2 / T^2``. ``charge`` and
    ``temperature`` default to elementary charge and kelvin respectively.

    Conversion factors follow one convention: a named unit factor is one
    external unit expressed in this system, so values convert by multiplication.
    """

    length: Unit
    time: Unit
    energy: Unit
    mass: Unit
    charge: Unit
    temperature: Unit
    _scales: tuple[float, float, float, float, float] = field(repr=False)

    def __init__(
        self,
        *,
        length: str | Unit | None = None,
        time: str | Unit | None = None,
        energy: str | Unit | None = None,
        mass: str | Unit | None = None,
        charge: str | Unit = "e",
        temperature: str | Unit = "K",
    ) -> None:
        supplied = {"length": length, "time": time, "energy": energy, "mass": mass}
        count = sum(value is not None for value in supplied.values())
        if count != 3:
            raise UnitSystemError(
                "exactly three of length, time, energy, and mass must be supplied; "
                f"got {count}"
            )

        scales: dict[str, float] = {}
        mechanical_dims = {"length": LENGTH, "time": TIME, "energy": ENERGY, "mass": MASS}
        resolved: dict[str, Unit] = {}
        for name, value in supplied.items():
            if value is not None:
                unit = _resolve_unit(value, name, mechanical_dims[name])
                resolved[name] = unit
                scales[name] = unit.scale

        if "mass" not in scales:
            scales["mass"] = scales["energy"] * scales["time"] ** 2 / scales["length"] ** 2
        elif "energy" not in scales:
            scales["energy"] = scales["mass"] * scales["length"] ** 2 / scales["time"] ** 2
        elif "length" not in scales:
            scales["length"] = math.sqrt(scales["energy"] * scales["time"] ** 2 / scales["mass"])
        else:
            scales["time"] = math.sqrt(scales["mass"] * scales["length"] ** 2 / scales["energy"])

        # Derived mechanical units are represented in SI and remain available
        # through the same explicit public attributes as supplied units.
        resolved.setdefault("length", Unit(scales["length"], LENGTH))
        resolved.setdefault("time", Unit(scales["time"], TIME))
        resolved.setdefault("energy", Unit(scales["energy"], ENERGY))
        resolved.setdefault("mass", Unit(scales["mass"], MASS))
        resolved["charge"] = _resolve_unit(charge, "charge", CHARGE)
        resolved["temperature"] = _resolve_unit(temperature, "temperature", TEMPERATURE)
        scales["charge"] = resolved["charge"].scale
        scales["temperature"] = resolved["temperature"].scale

        for name, unit in resolved.items():
            object.__setattr__(self, name, unit)
        object.__setattr__(
            self,
            "_scales",
            (scales["mass"], scales["length"], scales["time"], scales["charge"], scales["temperature"]),
        )

    @staticmethod
    def _dims_scale(dimensions: Dimensions, scales: tuple[float, float, float, float, float]) -> float:
        exponents = (dimensions.mass, dimensions.length, dimensions.time, dimensions.charge, dimensions.temperature)
        return math.prod(scale ** float(exponent) for scale, exponent in zip(scales, exponents))

    def factor_from(self, unit: str | Unit) -> float:
        """Return one external unit expressed in this system as a float."""

        if isinstance(unit, str):
            resolved = parse_unit(unit)
        elif type(unit) is Unit:
            resolved = unit
        else:
            raise TypeError("unit must be a unit expression or Unit")
        return float(resolved.scale / self._dims_scale(resolved.dimensions, self._scales))

    def factor_to(self, unit: str | Unit) -> float:
        """Return the inverse of :meth:`factor_from`."""

        return float(1.0 / self.factor_from(unit))

    def to_internal(self, value: Any, unit: str | Unit) -> Any:
        """Convert an external value into this system by scalar multiplication."""

        return value * self.factor_from(unit)

    def from_internal(self, value: Any, unit: str | Unit) -> Any:
        """Convert a value from this system to the requested external unit."""

        return value * self.factor_to(unit)

    def _convenience(self, expression: str) -> float:
        return self.factor_from(expression)

    def _physical_constant(self, name: str) -> float:
        """Express an SI constant in this system, preserving dimensionless values."""

        constant = constants.CONSTANTS[name]
        return float(constant.value / self._dims_scale(constant.dimensions, self._scales))

    @property
    def K_B(self) -> float:
        return self._physical_constant("K_B")

    @property
    def HBAR(self) -> float:
        return self._physical_constant("HBAR")

    @property
    def PLANCK(self) -> float:
        return self._physical_constant("PLANCK")

    @property
    def C_LIGHT(self) -> float:
        return self._physical_constant("C_LIGHT")

    @property
    def ALPHA(self) -> float:
        return self._physical_constant("ALPHA")

    @property
    def M_E(self) -> float:
        return self._physical_constant("M_E")

    @property
    def M_P(self) -> float:
        return self._physical_constant("M_P")

    @property
    def E_CHARGE(self) -> float:
        return self._physical_constant("E_CHARGE")

    @property
    def N_A(self) -> float:
        return self._physical_constant("N_A")

    @property
    def EPSILON_0(self) -> float:
        return self._physical_constant("EPSILON_0")

    @property
    def K_E(self) -> float:
        return self._physical_constant("K_E")

    @property
    def EV(self) -> float:
        return self._convenience("eV")

    @property
    def HARTREE(self) -> float:
        return self._convenience("Hartree")

    @property
    def HA(self) -> float:
        return self._convenience("Ha")

    @property
    def ANGSTROM(self) -> float:
        return self._convenience("angstrom")

    @property
    def BOHR(self) -> float:
        return self._convenience("bohr")

    @property
    def FS(self) -> float:
        return self._convenience("fs")

    @property
    def PS(self) -> float:
        return self._convenience("ps")

    @property
    def DA(self) -> float:
        return self._convenience("Da")

    @property
    def KCALPERMOL(self) -> float:
        return self._convenience("kcal/mol")

    @property
    def KJPERMOL(self) -> float:
        return self._convenience("kJ/mol")

    @property
    def DEBYE(self) -> float:
        return self._convenience("D")

    @property
    def THZ(self) -> float:
        return self._convenience("THz")

    @property
    def CM1(self) -> float:
        return self._convenience("cm^-1")

    @property
    def ATM(self) -> float:
        return self._convenience("atm")

    @property
    def BAR(self) -> float:
        return self._convenience("bar")

    @property
    def GPA(self) -> float:
        return self._convenience("GPa")

    @property
    def PA(self) -> float:
        return self._convenience("Pa")

    @property
    def NEWTON(self) -> float:
        return self._convenience("N")

    @property
    def NN(self) -> float:
        return self._convenience("nN")


au = UnitSystem(length="bohr", time="atomic_time", energy="Hartree", charge="e", temperature="K")
