from pathlib import Path

import pytest

from StecaChargerPy.spec import ApiSpecification, load_default_specification


def test_specification_loads_from_file(tmp_path: Path) -> None:
    original = Path(__file__).resolve().parent.parent / "eSystemsWlwbRestApi.yaml"
    if not original.exists():
        pytest.skip("OpenAPI specification not available in repository root")

    copied = tmp_path / "spec.yaml"
    copied.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")

    spec = ApiSpecification.from_file(copied)

    assert len(spec) > 0
    assert spec.get_operation("get-charging-state").path == "/charging/state"


def test_load_default_specification_falls_back_to_repository_copy() -> None:
    spec = load_default_specification()
    assert spec.get_operation("get-charging-state")

