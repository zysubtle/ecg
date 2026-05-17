"""Detector factory scaffold."""

from __future__ import annotations

from ecg_rr_tool.detectors.base import RPeakDetector


def create_detector(name: str) -> RPeakDetector:
    """Create a detector adapter by name.

    Concrete detector adapters are selected after M2a and implemented in M3.
    """
    raise NotImplementedError(
        f"Detector '{name}' is not implemented in M1. "
        "Run M2a evaluation first, then implement the selected adapter in M3."
    )
