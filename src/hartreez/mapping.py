"""Normalization of unit-annotated Python mappings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast, overload

from hartreez.errors import MappingConversionError, UnitError
from hartreez.parser import parse_unit
from hartreez.systems import UnitSystem


def _path_child(path: str, key: object) -> str:
    """Return a readable normalized path for a mapping key."""

    if isinstance(key, str) and key.isidentifier():
        return f"{path}.{key}"
    return f"{path}[{key!r}]"


def _annotation(key: str, path: str) -> tuple[str, str] | None:
    """Split one strict terminal ``[unit expression]`` annotation."""

    has_bracket = "[" in key or "]" in key
    if not has_bracket:
        return None
    if not key.endswith("]"):
        raise MappingConversionError(
            f"malformed unit annotation in key {key!r} at {path}; "
            "expected a terminal '[unit expression]' suffix"
        )
    open_bracket = key.rfind("[")
    if open_bracket <= 0 or "[" in key[:open_bracket] or "]" in key[:open_bracket]:
        raise MappingConversionError(
            f"malformed unit annotation in key {key!r} at {path}; "
            "expected a non-empty key followed by one terminal '[unit expression]' suffix"
        )
    expression = key[open_bracket + 1 : -1]
    if not expression.strip():
        raise MappingConversionError(
            f"malformed unit annotation in key {key!r} at {path}; unit expression is empty"
        )
    canonical = key[:open_bracket]
    if canonical != canonical.strip():
        raise MappingConversionError(
            f"malformed unit annotation in key {key!r} at {path}; "
            "the canonical key cannot have surrounding whitespace"
        )
    return canonical, expression


def _scale_value(value: Any, factor: float, path: str, original_key: str) -> Any:
    """Scale supported annotated values, retaining list and tuple structure."""

    if isinstance(value, Mapping):
        raise MappingConversionError(
            f"annotated key {original_key!r} at {path} has a mapping value; "
            "unit annotations cannot be applied to mappings"
        )
    if isinstance(value, list):
        items = cast(list[Any], value)
        return [
            _scale_value(item, factor, f"{path}[{index}]", original_key)
            for index, item in enumerate(items)
        ]
    if isinstance(value, tuple):
        items = cast(tuple[Any, ...], value)
        return tuple(
            _scale_value(item, factor, f"{path}[{index}]", original_key)
            for index, item in enumerate(items)
        )
    if isinstance(value, bool) or value is None or isinstance(value, str):
        raise MappingConversionError(
            f"cannot scale value at {path} from annotated key {original_key!r}: "
            f"unsupported value of type {type(value).__name__}"
        )
    try:
        return value * factor
    except Exception as exc:
        raise MappingConversionError(
            f"cannot scale value at {path} from annotated key {original_key!r}: "
            f"unsupported value of type {type(value).__name__} "
            "(it must support multiplication by a Python float)"
        ) from exc


def _normalize_mapping_level(
    mapping: Mapping[Any, Any],
    system: UnitSystem,
    path: str,
    *,
    recurse: bool,
) -> dict[Any, Any]:
    """Normalize one mapping level; ``recurse`` is a seam for shallow clients."""

    entries: list[tuple[Any, Any, str, str | None, str | None]] = []
    seen: dict[Any, Any] = {}
    for key, value in mapping.items():
        child_path = _path_child(path, key)
        if isinstance(key, str):
            annotation = _annotation(key, child_path)
        else:
            annotation = None
        canonical, expression = annotation if annotation is not None else (key, None)
        if canonical in seen:
            first = seen[canonical]
            raise MappingConversionError(
                f"normalized key collision at {_path_child(path, canonical)}: "
                f"keys {first!r} and {key!r} both normalize to {canonical!r}"
            )
        seen[canonical] = key
        entries.append((canonical, value, child_path, expression, key if expression is not None else None))

    normalized: dict[Any, Any] = {}
    for canonical, value, original_path, expression, original_key in entries:
        target_path = _path_child(path, canonical)
        if expression is not None:
            if original_key is None:
                raise RuntimeError("annotated mapping entry has no original key")
            try:
                unit = parse_unit(expression)
            except UnitError as exc:
                raise MappingConversionError(
                    f"invalid unit expression {expression!r} in key {original_key!r} "
                    f"at {original_path}: {exc}"
                ) from exc
            try:
                factor = system.factor_from(unit)
            except Exception as exc:
                raise MappingConversionError(
                    f"could not convert key {original_key!r} with unit expression "
                    f"{expression!r} at {original_path}: {exc}"
                ) from exc
            normalized[canonical] = _scale_value(value, factor, target_path, original_key)
        elif recurse:
            normalized[canonical] = _normalize_unannotated(value, system, target_path)
        else:
            normalized[canonical] = value
    return normalized


def _normalize_unannotated(value: Any, system: UnitSystem, path: str) -> Any:
    if isinstance(value, Mapping):
        return _normalize_mapping_level(cast(Mapping[Any, Any], value), system, path, recurse=True)
    if isinstance(value, list):
        items = cast(list[Any], value)
        return [
            _normalize_unannotated(item, system, f"{path}[{index}]")
            for index, item in enumerate(items)
        ]
    if isinstance(value, tuple):
        items = cast(tuple[Any, ...], value)
        return tuple(
            _normalize_unannotated(item, system, f"{path}[{index}]")
            for index, item in enumerate(items)
        )
    return value


@overload
def convert_mapping(mapping: Mapping[Any, Any], system: UnitSystem) -> dict[Any, Any]: ...


@overload
def convert_mapping(mapping: Any, system: Any) -> dict[Any, Any]: ...


def convert_mapping(mapping: Any, system: Any) -> dict[Any, Any]:
    """Return a new mapping with annotated values converted into ``system``.

    String keys ending in ``[unit expression]`` are converted and returned
    without that suffix. Other keys and values are treated as already in the
    supplied system. Nested mappings are normalized recursively. The input is
    never mutated and no serialization framework is required.

    Annotated lists and tuples are scaled recursively. Other scalar or
    array-like values are passed through ``value * float_factor`` so numerical
    frameworks can participate without becoming dependencies of this package.
    """

    if not isinstance(mapping, Mapping):
        raise TypeError("mapping must implement collections.abc.Mapping")
    if not isinstance(system, UnitSystem):
        raise TypeError("system must be a UnitSystem")
    return _normalize_mapping_level(cast(Mapping[Any, Any], mapping), system, "$", recurse=True)
