from __future__ import annotations

import csv
from pathlib import Path


FIXTURE = Path("tests/fixtures/bidmc_01_Signals_4000.csv")


def test_fixture_exists() -> None:
    assert FIXTURE.exists(), f"Missing fixture: {FIXTURE}"


def test_fixture_required_columns_after_strip() -> None:
    with FIXTURE.open(newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
    normalized = {col.strip(): col for col in header}
    assert "Time [s]" in normalized
    assert "II" in normalized
    assert "PLETH" in normalized


def test_fixture_sampling_rate_is_125_hz() -> None:
    times: list[float] = []
    with FIXTURE.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["Time [s]"]))
    assert len(times) == 4000
    fs = (len(times) - 1) / (times[-1] - times[0])
    assert abs(fs - 125.0) < 1e-6
