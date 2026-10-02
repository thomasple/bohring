"""Source physical constants, independent of the unit registry.

Measured inputs are central values from CODATA 2022. Exact SI defining
constants are kept exact. Derived atomic units share these inputs so that
their identities remain internally consistent.
"""

from math import pi

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
SPECTROSCOPIC_CM1 = 2.0 * pi * C_LIGHT * 100.0  # s^-1

