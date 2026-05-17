from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


FIXTURE = Path("tests/fixtures/bidmc_01_Signals_4000.csv")
SCRIPT = Path("tools/evaluate_detectors.py")


def _load_eval_module():
    pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    pytest.importorskip("sleepecg")
    spec = importlib.util.spec_from_file_location("evaluate_detectors", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_m2a_eval_script_smoke_candidates_are_mappable() -> None:
    module = _load_eval_module()
    results = module.evaluate_detectors(FIXTURE, ["sleepecg", "scipy_find_peaks"])

    assert len(results) == 2
    assert all(result.status == "success" for result in results)
    assert all(result.io_contract_mappable for result in results)
    assert all(result.r_peak_count > 0 for result in results)
    assert all(result.rr_all_in_300_2000_ms for result in results)
