"""Detector interface scaffold.

M1 defines the shape of the future adapter layer but does not integrate any
third-party detector.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class RPeakEvent:
    """One R-peak event in detector output coordinates."""

    r_peak_sample_index: int
    r_peak_time_s: float
    rr_ms: float | None
    detector_name: str
    detector_version: str | None = None
    quality_flag: str | None = None
    error_message: str | None = None


class RPeakDetector(Protocol):
    """Unified detector interface for future adapters."""

    name: str
    version: str | None

    def detect(self, ecg: Sequence[float], sampling_rate_hz: float) -> list[RPeakEvent]:
        """Detect R peaks from one ECG sequence."""
        ...
