from pathlib import Path

import pandas as pd
import pytest

from src.data_collection import collect_csv_bytes, collect_csv_file


def test_collect_uploaded_csv_normalizes_headers_and_records_provenance() -> None:
    data, source = collect_csv_bytes(b" Product_ID , Daily_Sales\nP1,12\n", source_name="store.csv")
    assert data.columns.tolist() == ["product_id", "daily_sales"]
    assert source.source_type == "uploaded_csv"
    assert source.source_name == "store.csv"
    assert source.rows_collected == 1


def test_collect_batch_csv(tmp_path: Path) -> None:
    path = tmp_path / "inventory.csv"
    pd.DataFrame({"product_id": ["P1"], "current_inventory": [20]}).to_csv(path, index=False)
    data, source = collect_csv_file(path)
    assert len(data) == 1
    assert source.source_type == "batch_csv"


def test_collection_rejects_empty_file() -> None:
    with pytest.raises(ValueError, match="empty"):
        collect_csv_bytes(b"")


def test_collection_rejects_oversized_upload() -> None:
    with pytest.raises(ValueError, match="10 MB"):
        collect_csv_bytes(b"x" * (10 * 1024 * 1024 + 1))
