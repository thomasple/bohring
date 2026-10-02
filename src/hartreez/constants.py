"""Source physical constants, independent of the unit registry.

Measured inputs are central values from CODATA 2022. Exact SI defining
constants are kept exact. Derived atomic units share these inputs so that
their identities remain internally consistent.
"""

from dataclasses import dataclass
from math import pi
from types import MappingProxyType
from typing import Mapping

from hartreez.dimensions import Dimensions

# Exact SI defining constants.
C_LIGHT = 299_792_458.0  # m s^-1
PLANCK = 6.626_070_15e-34  # J s
E_CHARGE = 1.602_176_634e-19  # C
K_B = 1.380_649e-23  # J K^-1
N_A = 6.022_140_76e23  # mol^-1; exposed as a dimensionless count

# CODATA 2022 measured central values.
ALPHA = 7.297_352_5643e-3
M_E = 9.109_383_7139e-31  # kg
M_P = 1.672_621_92595e-27  # kg
M_U = 1.660_539_06892e-27  # kg, atomic mass constant (Dalton)

# Derived values use the shared source inputs above.
HBAR = PLANCK / (2.0 * pi)
BOHR_RADIUS = HBAR / (M_E * C_LIGHT * ALPHA)  # m
HARTREE_ENERGY = ALPHA**2 * M_E * C_LIGHT**2  # J
ATOMIC_TIME = HBAR / HARTREE_ENERGY  # s
RYDBERG_ENERGY = HARTREE_ENERGY / 2.0  # J
DEBYE = 1.0e-21 / C_LIGHT  # C m; exact SI conversion under definition
SPECTROSCOPIC_CM1 = C_LIGHT * 100.0  # Hz per cm^-1 of wavenumber

# Dimensions use the package's independent SI bases M, L, T, Q, and Θ.
_MASS = Dimensions(mass=1)
_LENGTH = Dimensions(length=1)
_TIME = Dimensions(time=1)
_CHARGE = Dimensions(charge=1)
_TEMPERATURE = Dimensions(temperature=1)
_ENERGY = _MASS * (_LENGTH**2) / (_TIME**2)
_DIMENSIONLESS = Dimensions()

EPSILON_0 = E_CHARGE**2 / (4.0 * pi * ALPHA * HBAR * C_LIGHT)  # F m^-1
K_E = 1.0 / (4.0 * pi * EPSILON_0)  # N m^2 C^-2


@dataclass(frozen=True, slots=True)
class PhysicalConstant:
    """A central SI value and its physical dimensions."""

    value: float
    dimensions: Dimensions


CONSTANTS: Mapping[str, PhysicalConstant] = MappingProxyType(
    {
        "K_B": PhysicalConstant(K_B, _ENERGY / _TEMPERATURE),
        "HBAR": PhysicalConstant(HBAR, _ENERGY * _TIME),
        "PLANCK": PhysicalConstant(PLANCK, _ENERGY * _TIME),
        "C_LIGHT": PhysicalConstant(C_LIGHT, _LENGTH / _TIME),
        "ALPHA": PhysicalConstant(ALPHA, _DIMENSIONLESS),
        "M_E": PhysicalConstant(M_E, _MASS),
        "M_P": PhysicalConstant(M_P, _MASS),
        "E_CHARGE": PhysicalConstant(E_CHARGE, _CHARGE),
        # This is a particle count and remains dimensionless in every system.
        "N_A": PhysicalConstant(N_A, _DIMENSIONLESS),
        "EPSILON_0": PhysicalConstant(EPSILON_0, (_CHARGE**2) / _ENERGY / _LENGTH),
        "K_E": PhysicalConstant(K_E, _ENERGY * _LENGTH / (_CHARGE**2)),
    }
)


def constant_names() -> tuple[str, ...]:
    """Return the curated physical constant names alphabetically."""

    return tuple(sorted(CONSTANTS))
