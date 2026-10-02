# Mapping conversion

Use `convert_mapping` at a configuration or object construction boundary to
convert annotated values into a selected working `UnitSystem`. It accepts
Python mappings directly, so the caller can use the same API after loading
YAML, TOML, JSON, or any other format. `hartreez` does not load or write those
formats itself.

```python
from hartreez import au, convert_mapping

raw = {
    "timestep[fs]": 0.5,
    "cell[angstrom]": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
    "solver": {"tolerance": 1e-8},
}
config = convert_mapping(raw, au)
```

`config` has keys `timestep`, `cell`, and `solver`. Annotated values are
multiplied by their unit factor in `au`; nested mappings are normalized
recursively. The input mapping is left untouched. Unannotated values are
assumed to already use the selected working units, and non-string keys are
preserved as-is.

Lists and tuples under annotated keys are scaled recursively while retaining
their structure. Other numeric or array-like values can participate by
supporting multiplication by a Python `float`. The core package does not
import NumPy or another numerical framework. Annotated booleans, strings,
`None`, unsupported leaves, and mapping values raise `MappingConversionError`
with the affected path and original key.

Annotations use a terminal unit expression, for example `dt[fs]`,
`cell[angstrom]`, or `force[eV/angstrom]`. The annotation is removed after
conversion. If multiple input keys normalize to the same name, conversion
raises `MappingConversionError` instead of overwriting a value.

```python
from hartreez import MappingConversionError, au, convert_mapping

try:
    config = convert_mapping({"dt[fortnight]": 1.0}, au)
except MappingConversionError as error:
    print(error)
```
