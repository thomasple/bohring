from __future__ import annotations

import os
import subprocess
import zipfile
from pathlib import Path


def test_built_wheel_contains_pep561_marker(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(tmp_path / "uv-cache")
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    wheels = list(tmp_path.glob("*.whl"))
    assert len(wheels) == 1
    with zipfile.ZipFile(wheels[0]) as wheel:
        assert "hartreez/py.typed" in wheel.namelist()
