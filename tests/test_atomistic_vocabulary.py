from fractions import Fraction

import pytest

from hartreez import Dimensions, IncompatibleUnitsError, UnknownUnitError, convert, parse_unit, unit_names


@pytest.mark.parametrize(
    ("name", "canonical"),
    [
        ("1", "1"), ("kg", "kg"), ("g", "g"), ("Da", "Da"),
        ("m", "m"), ("cm", "cm"), ("mm", "mm"), ("km", "km"), ("nm", "nm"),
        ("angstrom", "angstrom"), ("bohr", "bohr"),
        ("s", "s"), ("ms", "ms"), ("us", "us"), ("ns", "ns"),
        ("ps", "ps"), ("fs", "fs"), ("atomic_time", "atomic_time"),
        ("C", "C"), ("e", "e"), ("K", "K"), ("J", "J"),
        ("eV", "eV"), ("meV", "meV"), ("Hartree", "Hartree"),
        ("Rydberg", "Rydberg"), ("cal", "cal"), ("kcal", "kcal"),
        ("kJ", "kJ"), ("Hz", "Hz"), ("THz", "THz"),
        ("cm1", "cm1"), ("Pa", "Pa"), ("bar", "bar"),
        ("kbar", "kbar"), ("atm", "atm"), ("GPa", "GPa"),
        ("N", "N"), ("nN", "nN"), ("D", "D"), ("mol", "mol"),
        ("min", "min"), ("h", "h"),
        ("meter", "m"), ("centimeter", "cm"), ("kilometer", "km"), ("nanometer", "nm"),
        ("Å", "angstrom"), ("Angstrom", "angstrom"), ("a0", "bohr"),
        ("a_0", "bohr"), ("second", "s"), ("femtosecond", "fs"),
        ("picosecond", "ps"), ("nanosecond", "ns"),
        ("atomic_unit_of_time", "atomic_time"), ("aut", "atomic_time"),
        ("coulomb", "C"), ("elementary_charge", "e"), ("kelvin", "K"),
        ("joule", "J"), ("electronvolt", "eV"),
        ("Hartree_energy", "Hartree"), ("Ha", "Hartree"), ("Ry", "Rydberg"),
        ("cal_th", "cal"), ("kcal_th", "kcal"), ("kilocalorie", "kcal"),
        ("kilojoule", "kJ"), ("atomic_mass_unit", "Da"), ("amu", "Da"),
        ("u", "Da"), ("hertz", "Hz"), ("terahertz", "THz"),
        ("pascal", "Pa"), ("atmosphere", "atm"),
        ("newton", "N"), ("debye", "D"),
    ],
)
def test_every_registered_name_resolves_to_documented_unit(name: str, canonical: str) -> None:
    assert parse_unit(name) == parse_unit(canonical)
    assert name in unit_names()


def test_registry_names_are_exact_and_case_sensitive() -> None:
    assert len(unit_names()) == len(set(unit_names()))
    for unsupported in ("angstroms", "kPa", "EV", "dalton", "CM1"):
        with pytest.raises(UnknownUnitError):
            parse_unit(unsupported)


def test_mole_scaling_gives_molar_energy_particle_energy_dimensions() -> None:
    assert parse_unit("mol").dimensions == Dimensions()
    assert parse_unit("kcal/mol").dimensions == parse_unit("J").dimensions
    assert parse_unit("kJ/mol").dimensions == parse_unit("J").dimensions
    assert convert(1.0, "eV", "kcal/mol") == pytest.approx(23.06054783061903, rel=1e-14)
    # Independent CODATA 2022 Hartree value and exact Avogadro count.
    expected_hartree_kj_per_mol = 4.3597447222060e-18 * 6.02214076e23 / 1000
    assert convert(1.0, "Hartree", "kJ/mol") == pytest.approx(
        expected_hartree_kj_per_mol, rel=2e-11
    )


def test_cm1_is_spectroscopic_and_geometric_powers_remain_geometric() -> None:
    spectroscopy = parse_unit("cm1")
    assert spectroscopy.dimensions == Dimensions(time=-1)
    assert convert(1.0, "cm1", "THz") == pytest.approx(0.0299792458, rel=1e-14)
    assert parse_unit("cm1/s").dimensions == Dimensions(time=-2)
    assert parse_unit("(cm1)*s").dimensions == Dimensions()
    assert parse_unit("1/cm").dimensions == Dimensions(length=-1)
    assert parse_unit("cm^-1").dimensions == Dimensions(length=-1)
    assert parse_unit("cm^-1") == parse_unit("1/cm")
    assert parse_unit("cm**-1").dimensions == Dimensions(length=-1)
    assert parse_unit("(cm)^-1").dimensions == Dimensions(length=-1)
    assert parse_unit("cm^-10").dimensions == Dimensions(length=-10)
    assert parse_unit("cm^-1/2").dimensions == Dimensions(length=Fraction(-1, 2))
    assert parse_unit("cm^-1.5").dimensions == Dimensions(length=Fraction(-3, 2))
    assert parse_unit("(cm)^-1/2").dimensions == Dimensions(length=Fraction(-1, 2))
    with pytest.raises(IncompatibleUnitsError):
        convert(1.0, "cm1", "1/cm")


def test_cm_inverse_combines_as_geometric_length() -> None:
    assert parse_unit("cm^-1/s").dimensions == Dimensions(length=-1, time=-1)


def test_dalton_debye_and_derived_atomic_units_use_reference_scales() -> None:
    from hartreez import constants

    assert constants.M_U == pytest.approx(1.66053906892e-27, rel=1e-14)
    assert parse_unit("Da").scale == constants.M_U
    # CODATA gives these derived values at higher precision than the rounded
    # ALPHA and M_E inputs used here; this tolerance covers their input rounding.
    assert parse_unit("bohr").scale == pytest.approx(5.29177210544e-11, rel=2e-11)
    assert parse_unit("Hartree").scale == pytest.approx(4.3597447222060e-18, rel=2e-11)
    assert parse_unit("atomic_time").scale == pytest.approx(2.4188843265864e-17, rel=2e-11)
    assert parse_unit("D").scale == pytest.approx(3.33564095198152e-30, rel=1e-14)
    assert convert(1.0, "D", "e*bohr") == pytest.approx(0.3934302697868, rel=2e-11)


def test_trailing_whitespace_is_accepted() -> None:
    assert parse_unit("m   ") == parse_unit("m")
    assert parse_unit("  kcal / mol  ") == parse_unit("kcal/mol")
