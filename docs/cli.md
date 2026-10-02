# Command line interface

The `hartreez` command uses only the Python standard library and is installed
with the base package. Unit expressions use the same curated, case-sensitive
grammar as the Python API. Quote expressions containing spaces so the shell
passes each expression as one argument. The CLI parses unit expressions; it
does not evaluate Python code.

## Convert values

`convert VALUE FROM_UNIT TO_UNIT` converts a number and prints only the numeric
result, in the destination unit. For example:

```sh
hartreez convert 1 eV Ha
hartreez convert 1 'kcal/mol' eV
hartreez convert 1 cm1 THz
```

Use `--verbose` (or `-v`) for a readable equality:

```sh
hartreez convert 1 eV Ha --verbose
# 1 eV is approximately 0.03675 Ha
```

Products, quotients, and powers work in either unit argument. For example,
`hartreez convert 1 'eV/angstrom' 'Hartree/bohr'`. Spectroscopic `cm1` means
cyclic frequency (`f = c*wavenumber`); `1/cm` and `cm^-1` are geometric
reciprocal length.

## Query atomic-unit values

`factor UNIT` prints one unit expressed in the built-in atomic unit system. Its
number follows the library convention, so multiply an input value by the
factor to express it in atomic units:

```sh
hartreez factor eV
hartreez factor angstrom
```

`constant NAME` prints a physical constant in atomic units. Names are
case-sensitive:

```sh
hartreez constant HBAR
hartreez constant K_B
```

## Discover the curated vocabulary

The discovery commands print one item per line, sorted alphabetically.
`units` lists canonical unit spellings, `aliases` lists each accepted alias
and its canonical spelling, and `constants` lists queryable physical constant
names. These are curated names, not prefix-generated possibilities.

```sh
hartreez units
hartreez aliases
hartreez constants
```

Invalid expressions, incompatible dimensions, unknown constant names, and
invalid arguments exit unsuccessfully and report diagnostics to standard
error. Successful non-verbose conversions, factor queries, and constant
queries keep standard output numeric for use in scripts.
