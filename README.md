# hartreez

Small, dependency-free unit parsing and conversion for ordinary numerical code.
The first release provides immutable dimensions and units, a curated atomistic
and MD registry, and direct conversion without quantity wrappers.

## Parse and inspect units

```python
from hartreez import parse_unit

force = parse_unit("kg*m/s^2")
assert force.dimensions == parse_unit("N").dimensions
```

`Dimensions` tracks exact rational exponents for mass (`M`), length (`L`),
time (`T`), charge (`Q`), and temperature (`Θ`). Energy is derived as
`kg*m^2/s^2`; other dimensions such as momentum, force, pressure, diffusion,
and dipole moment follow from the same algebra.

Expressions use registered names, the dimensionless literal `1`, explicit
products (`*`) and quotients (`/`), parentheses, and powers. A power uses `^`
or `**`, followed by a signed integer (`m^-2`), a finite decimal
(`m^0.5`), or a rational literal (`m^1/2`, `m^-3/2`). Multiplication is always
explicit: `kg m` is invalid. Numeric coefficients other than the unit literal
`1` are invalid. Names are case-sensitive. Parsed expressions are cached.

The curated registry includes SI and atomistic units such as `angstrom`,
`bohr`, `fs`, `ps`, `eV`, `Hartree`, `Rydberg`, `Da`, `D`, and `kcal/mol`.
Its full list of canonical spellings, aliases, conventions, and constant
provenance is in [the unit vocabulary reference](docs/units.md). Spectroscopic
`cm^-1` is inverse time; `1/cm` and `cm**-1` are geometric inverse length.
Unregistered names and malformed expressions raise `UnitSyntaxError`, with
`UnknownUnitError` identifying unknown names specifically.

## Convert values

```python
from hartreez import convert

distance_in_cm = convert(1.25, "m", "cm")
energy = convert(1.0, "J", "kg*m^2/s^2")
```

`convert(value, from_unit, to_unit)` requires equal dimensions and multiplies
the supplied value by a Python float. This keeps ordinary scalar types and
array-like objects in control of their own arithmetic. Incompatible dimensions
raise `IncompatibleUnitsError`, distinct from parsing errors. `Unit` values
returned by `parse_unit` can also be passed in place of either expression.

The public value types are `Dimensions` and `Unit`. They are immutable; a
`Unit` stores its positive finite SI scale as `scale` and its dimensions as
`dimensions`. The parser registry is read-only at runtime. `unit_names()` lists
the registered names.

## Coherent working systems

Create a system by supplying exactly three mechanical units. The fourth is
derived from `E = M L^2 / T^2`; charge defaults to elementary charge and
temperature to kelvin.

```python
from hartreez import UnitSystem, au

md = UnitSystem(length="angstrom", time="ps", energy="kcal/mol")
energy_in_md_units = md.to_internal(2.0, "eV")
distance_in_md_units = md.to_internal(1.0, "nm")

# Convenience attributes are floats: one eV expressed in Hartree, and one Å
# expressed in bohr. Multiply external values by these factors.
energy_in_hartree = 2.0 * au.EV
distance_in_bohr = 1.0 * au.ANGSTROM
```

`factor_from(unit)` returns one external unit in the active system and
`factor_to(unit)` returns its reciprocal. `to_internal` and `from_internal`
apply those factors by scalar multiplication. Compound expressions are
supported without predefined quantity categories, for example
`md.factor_from("Da*angstrom/ps")`. Systems and their mechanical unit values
are immutable. Importing `au` requires only the standard-library-backed core.
