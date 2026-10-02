from types import MappingProxyType

import pytest

from hartreez import UnitSystem, au
from hartreez import constants
from hartreez.dimensions import Dimensions


def test_registry_is_immutable_and_separate_from_unit_registry() -> None:
    assert isinstance(constants.CONSTANTS, MappingProxyType)
    with pytest.raises(TypeError):
        constants.CONSTANTS["NEW"] = constants.CONSTANTS["K_B"]  # type: ignore[index]
    with pytest.raises((AttributeError, TypeError)):
        constants.CONSTANTS["K_B"].value = 0  # type: ignore[misc]
    assert "K_B" not in __import__("hartreez.units", fromlist=["UNIT_REGISTRY"]).UNIT_REGISTRY


@pytest.mark.parametrize(
    "name",
    ["K_B", "HBAR", "PLANCK", "C_LIGHT", "ALPHA", "M_E", "M_P", "E_CHARGE", "N_A", "EPSILON_0", "K_E"],
)
def test_constants_are_explicit_float_properties(name: str) -> None:
    value = getattr(au, name)
    assert type(value) is float
    assert value > 0


def test_constant_source_values_and_dimensions() -> None:
    assert constants.K_B == 1.380649e-23
    assert constants.PLANCK == 6.62607015e-34
    assert constants.C_LIGHT == 299792458.0
    assert constants.E_CHARGE == 1.602176634e-19
    assert constants.N_A == 6.02214076e23
    assert constants.M_E == pytest.approx(9.1093837139e-31, rel=1e-14)
    assert constants.M_P == pytest.approx(1.67262192595e-27, rel=1e-14)
    assert constants.CONSTANTS["ALPHA"].dimensions == Dimensions()
    assert constants.CONSTANTS["N_A"].dimensions == Dimensions()
    assert constants.HBAR == pytest.approx(constants.PLANCK / (2 * 3.141592653589793))
    assert constants.EPSILON_0 == pytest.approx(8.8541878188e-12, rel=2e-10)
    assert constants.K_E == pytest.approx(1 / (4 * 3.141592653589793 * constants.EPSILON_0))


def test_atomic_unit_constant_identities_and_electromagnetic_constants() -> None:
    assert au.HBAR == pytest.approx(1.0)
    assert au.M_E == pytest.approx(1.0)
    assert au.E_CHARGE == pytest.approx(1.0)
    assert au.BOHR == pytest.approx(1.0)
    assert au.HARTREE == pytest.approx(1.0)
    assert au.N_A == 6.02214076e23
    assert au.ALPHA == pytest.approx(constants.ALPHA)
    assert au.K_E == pytest.approx(1.0)
    assert au.EPSILON_0 == pytest.approx(1.0 / (4.0 * 3.141592653589793))


def test_md_boltzmann_constant_and_nontrivial_dimensional_conversion() -> None:
    md = UnitSystem(length="angstrom", time="ps", energy="kcal/mol")
    assert md.K_B == pytest.approx(0.00198720425864083, rel=2e-12)
    assert md.C_LIGHT == pytest.approx(2_997_924.58)
    assert md.M_E == pytest.approx(constants.M_E / md.mass.scale)
    assert md.E_CHARGE == pytest.approx(1.0)
    assert md.N_A == constants.N_A
