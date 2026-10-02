from __future__ import annotations

import subprocess
import sys
from typing import Annotated

import pytest
from pydantic import Field, ValidationError, field_validator

from hartreez import UnitDimension, UnitSystem, au, parse_unit
from hartreez.pydantic import UnitAwareModel


class InputModel(UnitAwareModel):
    timestep: Annotated[float, UnitDimension("ps")] = Field(gt=0.0)
    energy: Annotated[float, UnitDimension("eV")] = 0.0
    force: Annotated[float, UnitDimension("eV/angstrom")] = 0.0
    count: int = 1

    @field_validator("timestep")
    @classmethod
    def positive_internal_time(cls, value: float) -> float:
        assert value > 0
        return value


def test_unit_dimension_is_immutable_and_represents_only_dimensions() -> None:
    femtoseconds = UnitDimension("fs")
    picoseconds = UnitDimension("ps")
    momentum = UnitDimension("Da*angstrom/ps")

    assert femtoseconds.dimensions == picoseconds.dimensions
    assert momentum.dimensions == parse_unit("Da*angstrom/ps").dimensions
    with pytest.raises(AttributeError):
        femtoseconds.expression = "ps"  # type: ignore[misc]
    with pytest.raises(ValueError):
        UnitDimension("fortnight")


def test_pydantic_converts_scalars_in_the_selected_system_before_constraints() -> None:
    model = InputModel.model_validate(
        {"timestep[fs]": 100.0, "energy[eV]": 2.0, "force[eV/angstrom]": 1.0},
        context={"unit_system": UnitSystem(length="angstrom", time="ps", energy="eV")},
    )

    assert model.timestep == pytest.approx(0.1)
    assert model.energy == pytest.approx(2.0)
    assert model.force == pytest.approx(1.0)


def test_annotations_are_dimensional_and_do_not_choose_output_units() -> None:
    md = UnitSystem(length="angstrom", time="ps", energy="kcal/mol")

    model = InputModel.model_validate(
        {"timestep[fs]": 1.0, "energy[eV]": 1.0}, context={"unit_system": md}
    )

    assert model.energy == pytest.approx(md.factor_from("eV"))


def test_constraints_and_application_validators_receive_converted_values() -> None:
    with pytest.raises(ValidationError, match="greater than 0"):
        InputModel.model_validate(
            {"timestep[fs]": -1.0}, context={"unit_system": au}
        )

    model = InputModel.model_validate(
        {"timestep[fs]": 1.0}, context={"unit_system": au}
    )
    assert model.timestep == pytest.approx(1.0 * au.factor_from("fs"))


def test_canonical_input_needs_no_context() -> None:
    model = InputModel.model_validate({"timestep": 0.25, "energy": 3.0})

    assert model.timestep == 0.25
    assert model.energy == 3.0


def test_annotated_input_requires_a_usable_system_context() -> None:
    with pytest.raises(ValidationError, match="requires a UnitSystem"):
        InputModel.model_validate({"timestep[fs]": 1.0})
    with pytest.raises(ValidationError, match="requires a UnitSystem"):
        InputModel.model_validate({"timestep[fs]": 1.0}, context={"unit_system": object()})


def test_dimensional_mismatch_and_normalization_collision_are_validation_errors() -> None:
    with pytest.raises(ValidationError, match="dimensional mismatch"):
        InputModel.model_validate(
            {"timestep[eV]": 1.0}, context={"unit_system": au}
        )
    with pytest.raises(ValidationError, match="normalized key collision"):
        InputModel.model_validate(
            {"timestep": 1.0, "timestep[fs]": 1.0}, context={"unit_system": au}
        )


def test_unannotated_fields_keep_normal_pydantic_conversion_semantics() -> None:
    model = InputModel.model_validate(
        {"timestep[fs]": 1.0, "count": "4"}, context={"unit_system": au}
    )

    assert model.count == 4


def test_core_namespace_does_not_import_or_require_pydantic() -> None:
    script = """
import importlib.abc
import sys

class BlockPydantic(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'pydantic' or fullname.startswith('pydantic.'):
            raise AssertionError('core import attempted to load Pydantic')
        return None

sys.meta_path.insert(0, BlockPydantic())
import hartreez
from hartreez import UnitDimension
assert UnitDimension('fs').dimensions == hartreez.parse_unit('ps').dimensions
assert 'pydantic' not in sys.modules
"""
    subprocess.run([sys.executable, "-c", script], check=True)
