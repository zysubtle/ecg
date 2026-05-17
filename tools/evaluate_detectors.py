"""Temporary M2a detector evaluation script.

This script is intentionally kept under tools/ and may call third-party
detector APIs directly. Formal detector integration must happen later through
the adapter layer under ecg_rr_tool/detectors/.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import tempfile
import warnings
from dataclasses import asdict, dataclass
from importlib import metadata
from pathlib import Path
from typing import Callable, Iterable

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "ecg_m2a_mpl"))

import numpy as np


RR_MIN_MS = 300.0
RR_MAX_MS = 2000.0


@dataclass(frozen=True)
class InputSignal:
    path: str
    sample_count: int
    estimated_fs_hz: float
    time_s: np.ndarray
    ecg: np.ndarray


@dataclass(frozen=True)
class DetectorResult:
    name: str
    package: str
    version: str | None
    status: str
    r_peak_count: int
    first_r_peak_times_s: list[float]
    rr_count: int
    rr_min_ms: float | None
    rr_median_ms: float | None
    rr_max_ms: float | None
    rr_out_of_range_count: int | None
    rr_all_in_300_2000_ms: bool | None
    io_contract_mappable: bool
    quality_flag: str
    error_message: str | None = None


def _package_version(package: str) -> str | None:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None


def _read_bidmc_csv(path: Path) -> InputSignal:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        normalized = {name.strip(): name for name in reader.fieldnames}
        missing = {"Time [s]", "II", "PLETH"} - set(normalized)
        if missing:
            raise ValueError(f"Missing required columns after strip(): {sorted(missing)}")

        time_s: list[float] = []
        ecg: list[float] = []
        for row in reader:
            time_s.append(float(row[normalized["Time [s]"]]))
            ecg.append(float(row[normalized["II"]]))

    if len(time_s) < 2:
        raise ValueError("Need at least two samples to estimate sampling rate")

    time_array = np.asarray(time_s, dtype=float)
    ecg_array = np.asarray(ecg, dtype=float)
    fs = float((len(time_array) - 1) / (time_array[-1] - time_array[0]))
    if abs(fs - 125.0) > 1e-6:
        raise ValueError(f"Expected about 125 Hz input, got {fs:.6f} Hz")

    return InputSignal(
        path=str(path),
        sample_count=len(time_array),
        estimated_fs_hz=fs,
        time_s=time_array,
        ecg=ecg_array,
    )


def _normalize_peaks(peaks: Iterable[int], sample_count: int) -> np.ndarray:
    array = np.asarray(list(peaks), dtype=int)
    if array.size == 0:
        return array
    array = np.unique(array)
    return array[(array >= 0) & (array < sample_count)]


def _summarize_result(
    name: str,
    package: str,
    signal: InputSignal,
    peaks: Iterable[int],
) -> DetectorResult:
    r_peaks = _normalize_peaks(peaks, signal.sample_count)
    peak_times = signal.time_s[r_peaks] if r_peaks.size else np.asarray([], dtype=float)
    rr_ms = np.diff(peak_times) * 1000.0
    out_of_range = int(np.sum((rr_ms < RR_MIN_MS) | (rr_ms > RR_MAX_MS)))
    rr_all_reasonable = bool(rr_ms.size > 0 and out_of_range == 0)

    return DetectorResult(
        name=name,
        package=package,
        version=_package_version(package),
        status="success",
        r_peak_count=int(r_peaks.size),
        first_r_peak_times_s=[round(float(value), 3) for value in peak_times[:8]],
        rr_count=int(rr_ms.size),
        rr_min_ms=round(float(np.min(rr_ms)), 3) if rr_ms.size else None,
        rr_median_ms=round(float(statistics.median(rr_ms)), 3) if rr_ms.size else None,
        rr_max_ms=round(float(np.max(rr_ms)), 3) if rr_ms.size else None,
        rr_out_of_range_count=out_of_range if rr_ms.size else None,
        rr_all_in_300_2000_ms=rr_all_reasonable if rr_ms.size else None,
        io_contract_mappable=True,
        quality_flag="ok" if rr_all_reasonable else "unknown",
    )


def _failure_result(name: str, package: str, error: BaseException) -> DetectorResult:
    return DetectorResult(
        name=name,
        package=package,
        version=_package_version(package),
        status="failed",
        r_peak_count=0,
        first_r_peak_times_s=[],
        rr_count=0,
        rr_min_ms=None,
        rr_median_ms=None,
        rr_max_ms=None,
        rr_out_of_range_count=None,
        rr_all_in_300_2000_ms=None,
        io_contract_mappable=False,
        quality_flag="error",
        error_message=f"{type(error).__name__}: {error}",
    )


def _run_neurokit2(signal: InputSignal) -> Iterable[int]:
    import neurokit2 as nk

    _, info = nk.ecg_peaks(signal.ecg, sampling_rate=signal.estimated_fs_hz, method="neurokit")
    return info["ECG_R_Peaks"]


def _run_wfdb_xqrs(signal: InputSignal) -> Iterable[int]:
    from wfdb import processing

    return processing.xqrs_detect(sig=signal.ecg, fs=signal.estimated_fs_hz, verbose=False)


def _run_biosppy(signal: InputSignal) -> Iterable[int]:
    from biosppy.signals import ecg as biosppy_ecg

    output = biosppy_ecg.ecg(signal=signal.ecg, sampling_rate=signal.estimated_fs_hz, show=False)
    return output["rpeaks"]


def _run_heartpy(signal: InputSignal) -> Iterable[int]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import heartpy as hp

    working_data, _ = hp.process(signal.ecg, sample_rate=signal.estimated_fs_hz)
    removed = {int(value) for value in working_data.get("removed_beats", [])}
    return [int(value) for value in working_data.get("peaklist", []) if int(value) not in removed]


def _run_sleepecg(signal: InputSignal) -> Iterable[int]:
    import sleepecg

    return sleepecg.detect_heartbeats(signal.ecg, fs=signal.estimated_fs_hz)


def _run_scipy_find_peaks(signal: InputSignal) -> Iterable[int]:
    from scipy.signal import butter, filtfilt, find_peaks

    nyquist = signal.estimated_fs_hz / 2.0
    b, a = butter(2, [5.0 / nyquist, 20.0 / nyquist], btype="bandpass")
    filtered = filtfilt(b, a, signal.ecg)
    score = filtered**2
    peaks, _ = find_peaks(
        score,
        distance=int(0.3 * signal.estimated_fs_hz),
        prominence=float(np.percentile(score, 90) * 0.5),
    )
    return peaks


CandidateRunner = Callable[[InputSignal], Iterable[int]]


CANDIDATES: dict[str, tuple[str, str, CandidateRunner]] = {
    "neurokit2": ("NeuroKit2 ecg_peaks(method='neurokit')", "neurokit2", _run_neurokit2),
    "wfdb_xqrs": ("WFDB processing.xqrs_detect", "wfdb", _run_wfdb_xqrs),
    "biosppy": ("BioSPPy ecg.ecg", "biosppy", _run_biosppy),
    "heartpy": ("HeartPy process", "heartpy", _run_heartpy),
    "sleepecg": ("SleepECG detect_heartbeats", "sleepecg", _run_sleepecg),
    "scipy_find_peaks": ("SciPy bandpass + find_peaks smoke heuristic", "scipy", _run_scipy_find_peaks),
}


def evaluate_detectors(path: Path, candidate_names: Iterable[str] | None = None) -> list[DetectorResult]:
    signal = _read_bidmc_csv(path)
    selected = list(candidate_names) if candidate_names is not None else list(CANDIDATES)
    results: list[DetectorResult] = []
    for key in selected:
        display_name, package, runner = CANDIDATES[key]
        try:
            peaks = runner(signal)
            results.append(_summarize_result(display_name, package, signal, peaks))
        except Exception as error:  # noqa: BLE001 - per-candidate failures are evaluation data.
            results.append(_failure_result(display_name, package, error))
    return results


def _format_rr(result: DetectorResult) -> str:
    if result.rr_count == 0:
        return "-"
    return f"{result.rr_min_ms:.1f}/{result.rr_median_ms:.1f}/{result.rr_max_ms:.1f}"


def _print_text_report(path: Path, results: list[DetectorResult]) -> None:
    signal = _read_bidmc_csv(path)
    print(f"input_csv: {signal.path}")
    print(f"samples: {signal.sample_count}")
    print(f"estimated_fs_hz: {signal.estimated_fs_hz:.6f}")
    print()
    print(
        "candidate | status | version | r_peak_count | rr_ms_min/median/max | "
        "rr_out_of_range | first_r_peak_times_s"
    )
    print("-" * 118)
    for result in results:
        first_times = ", ".join(f"{value:.3f}" for value in result.first_r_peak_times_s)
        print(
            f"{result.name} | {result.status} | {result.version or '-'} | "
            f"{result.r_peak_count} | {_format_rr(result)} | "
            f"{result.rr_out_of_range_count if result.rr_out_of_range_count is not None else '-'} | "
            f"{first_times or '-'}"
        )
        if result.error_message:
            print(f"  error: {result.error_message}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run M2a temporary R-peak detector smoke tests.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument(
        "--candidate",
        action="append",
        choices=sorted(CANDIDATES),
        help="Run only this candidate. Can be passed multiple times.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    results = evaluate_detectors(args.input_csv, args.candidate)
    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True))
    else:
        _print_text_report(args.input_csv, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
