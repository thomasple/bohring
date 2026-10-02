from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EXPECTED_EV_IN_HARTREE = 0.0367493221760613


@pytest.fixture(scope="session")
def console_script() -> Path:
    candidate = shutil.which("hartreez")
    if candidate is None:
        candidate_path = Path(sys.executable).with_name("hartreez")
        if candidate_path.is_file():
            candidate = str(candidate_path)
    if candidate is None:
        pytest.fail("hartreez console script is not installed; run the suite with `uv run`")
    return Path(candidate)


def run_cli(console_script: Path, *arguments: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(console_script), *arguments],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_console_script_converts_numerically_and_verbosely(console_script: Path) -> None:
    result = run_cli(console_script, "convert", "1", "eV", "Ha")
    assert result.returncode == 0
    assert result.stderr == ""
    assert float(result.stdout) == pytest.approx(EXPECTED_EV_IN_HARTREE, rel=1e-14)

    verbose = run_cli(console_script, "convert", "1", "eV", "Ha", "--verbose")
    assert verbose.returncode == 0
    assert verbose.stderr == ""
    assert verbose.stdout == f"1 eV = {EXPECTED_EV_IN_HARTREE:.15g} Ha\n"


def test_console_script_queries_factors_and_constants(console_script: Path) -> None:
    factor = run_cli(console_script, "factor", "eV")
    assert factor.returncode == 0
    assert float(factor.stdout) == pytest.approx(EXPECTED_EV_IN_HARTREE, rel=1e-14)

    constant = run_cli(console_script, "constant", "HBAR")
    assert constant.returncode == 0
    assert float(constant.stdout) == pytest.approx(1.0)


def test_console_script_lists_curated_discovery_data(console_script: Path) -> None:
    units = run_cli(console_script, "units")
    assert units.returncode == 0
    assert "angstrom\n" in units.stdout
    assert "eV\n" in units.stdout
    assert "Å\n" not in units.stdout

    aliases = run_cli(console_script, "aliases")
    assert aliases.returncode == 0
    assert "Å -> angstrom" in aliases.stdout
    assert "Ha -> Hartree" in aliases.stdout
    assert "kcalpermol -> kcal/mol" in aliases.stdout
    assert "kJpermol -> kJ/mol" in aliases.stdout

    constants = run_cli(console_script, "constants")
    assert constants.returncode == 0
    assert "HBAR\n" in constants.stdout
    assert "K_B\n" in constants.stdout


@pytest.mark.parametrize(
    ("arguments", "diagnostic"),
    [
        (("convert", "1", "m", "s"), "cannot convert"),
        (("convert", "1", "missing_unit", "m"), "unknown unit"),
        (("factor", "m**"), "unit expression"),
        (("constant", "missing"), "unknown physical constant"),
        (("convert", "not-a-number", "m", "m"), "invalid float value"),
    ],
)
def test_console_script_reports_errors_on_stderr(
    console_script: Path, arguments: tuple[str, ...], diagnostic: str
) -> None:
    result = run_cli(console_script, *arguments)
    assert result.returncode != 0
    assert result.stdout == ""
    assert diagnostic in result.stderr


def test_console_script_does_not_import_optional_frameworks(
    console_script: Path, tmp_path: Path
) -> None:
    guard = tmp_path / "sitecustomize.py"
    guard.write_text(
        "import builtins\n"
        "original_import = builtins.__import__\n"
        "blocked = {'pydantic', 'numpy', 'scipy', 'torch', 'jax'}\n"
        "def guarded_import(name, *args, **kwargs):\n"
        "    if name.split('.')[0] in blocked:\n"
        "        raise AssertionError('optional dependency imported: ' + name)\n"
        "    return original_import(name, *args, **kwargs)\n"
        "builtins.__import__ = guarded_import\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp_path)

    result = run_cli(console_script, "convert", "1", "eV", "Ha", env=env)
    assert result.returncode == 0
    assert result.stderr == ""
    assert float(result.stdout) == pytest.approx(EXPECTED_EV_IN_HARTREE, rel=1e-14)
