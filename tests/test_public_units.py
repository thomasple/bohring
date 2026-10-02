from fractions import Fraction

import pytest

from hartreez import (
    Dimensions,
    IncompatibleUnitsError,
    Unit,
    UnitSyntaxError,
    UnknownUnitError,
    convert,
    parse_unit,
    unit_names,
)


def test_dimension_and_unit_algebra_is_exact() -> None:
    momentum = parse_unit("kg*m/s")
    force = parse_unit("kg*m/s^2")
    energy = parse_unit("kg*m^2/s^2")
    pressure = parse_unit("kg/(m*s^2)")

    assert momentum.dimensions == Dimensions(mass=1, length=1, time=-1)
    assert force.dimensions == energy.dimensions / parse_unit("m").dimensions
    assert pressure.dimensions == parse_unit("Pa").dimensions
    assert parse_unit("m^2/s").dimensions == Dimensions(length=2, time=-1)
    assert parse_unit("C*m").dimensions == Dimensions(charge=1, length=1)
    assert parse_unit("J").dimensions == Dimensions(mass=1, length=2, time=-2)


def test_fractional_power_keeps_exact_dimensions_and_positive_scale() -> None:
    root = parse_unit("m^1/2")
    assert root.dimensions == Dimensions(length=Fraction(1, 2))
    assert root.scale == 1.0
    assert parse_unit("cm^0.5").dimensions == root.dimensions
    assert parse_unit("(m^2)^-1/2").dimensions == Dimensions(length=-1)


def test_registered_names_are_case_sensitive_and_available() -> None:
    assert {"kg", "g", "m", "cm", "s", "C", "K", "J", "N", "Pa"} <= set(unit_names())
    assert parse_unit("C").dimensions == Dimensions(charge=1)
    with pytest.raises(UnknownUnitError):
        parse_unit("c")


def test_direct_conversion_and_round_trip() -> None:
    value = 12.5
    centimeters = convert(value, "m", "cm")
    assert centimeters == pytest.approx(1250)
    assert convert(centimeters, "cm", "m") == pytest.approx(value)
    assert convert(2.0, "J", "kg*m^2/s^2") == pytest.approx(2.0)


def test_conversion_preserves_numeric_duck_type() -> None:
    class Scaled:
        def __init__(self, value: float) -> None:
            self.value = value

        def __mul__(self, factor: float) -> "Scaled":
            assert type(factor) is float
            return Scaled(self.value * factor)

    result = convert(Scaled(2.0), "m", "cm")
    assert isinstance(result, Scaled)
    assert result.value == pytest.approx(200)


@pytest.mark.parametrize(
    "expression",
    ["", "m**", "m//s", "m*/s", "m^", "m^1/0", "(m", "m)", "m s", "2*m", "m^2^3", "m/s/"],
)
def test_malformed_expressions_raise_syntax_errors(expression: str) -> None:
    with pytest.raises(UnitSyntaxError):
        parse_unit(expression)


def test_unknown_units_have_a_distinct_actionable_error() -> None:
    with pytest.raises(UnknownUnitError, match="unknown unit 'fortnight'"):
        parse_unit("fortnight")


def test_incompatible_dimensions_have_a_distinct_error() -> None:
    with pytest.raises(IncompatibleUnitsError, match="cannot convert"):
        convert(1, "m", "s")


def test_dimensions_and_units_are_immutable_and_validate_scale() -> None:
    dimensions = Dimensions(length=1)
    with pytest.raises((AttributeError, TypeError)):
        dimensions.length = Fraction(2)  # type: ignore[misc]
    with pytest.raises(ValueError, match="positive finite"):
        Unit(0, dimensions)


def test_registry_is_not_exposed_as_a_mutable_mapping() -> None:
    # A new name cannot be introduced implicitly by the parser.
    with pytest.raises(UnknownUnitError):
        parse_unit("made_up")
