"""Data-ingestion layer for inventory and demand datasets.

The project supports two collection paths: browser-uploaded CSV bytes for the
interactive application and filesystem CSV files for reproducible batch jobs.
Both paths normalize headers, reject empty inputs, and return source provenance
so downstream reports can identify where the operational data originated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path

import pandas as pd


MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class DataSource:
    """Auditable metadata describing an ingested dataset."""

    source_type: str
    source_name: str
    rows_collected: int
    columns_collected: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _normalize(data: pd.DataFrame, *, source_type: str, source_name: str) -> tuple[pd.DataFrame, DataSource]:
    if data.empty:
        raise ValueError("The dataset contains headers but no data rows.")
    normalized = data.copy()
    normalized.columns = normalized.columns.astype(str).str.strip().str.lower()
    if normalized.columns.duplicated().any():
        duplicates = sorted(set(normalized.columns[normalized.columns.duplicated()].tolist()))
        raise ValueError("Duplicate column names after normalization: " + ", ".join(duplicates))
    source = DataSource(source_type, source_name, len(normalized), len(normalized.columns))
    return normalized, source


def collect_csv_bytes(contents: bytes, *, source_name: str = "browser_upload.csv") -> tuple[pd.DataFrame, DataSource]:
    """Collect a CSV received through the application upload interface."""

    if not contents:
        raise ValueError("The uploaded file is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise ValueError("The uploaded CSV is larger than the 10 MB safety limit.")
    try:
        data = pd.read_csv(BytesIO(contents))
    except Exception as exc:
        raise ValueError(f"The file could not be read as CSV: {exc}") from exc
    return _normalize(data, source_type="uploaded_csv", source_name=source_name)


def collect_csv_file(path: str | Path) -> tuple[pd.DataFrame, DataSource]:
    """Collect a local CSV for scheduled or command-line batch processing."""

    source_path = Path(path)
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {source_path}")
    try:
        data = pd.read_csv(source_path)
    except Exception as exc:
        raise ValueError(f"The dataset could not be read as CSV: {exc}") from exc
    return _normalize(data, source_type="batch_csv", source_name=source_path.name)
