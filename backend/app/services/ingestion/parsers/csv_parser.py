from typing import List
import pandas as pd

from app.services.ingestion.models import RawRecord
from app.services.ingestion.parsers.base import BaseParser


class CSVParser(BaseParser):
    """Parses CSV financial statements using pandas."""

    def parse(self, file_path: str) -> List[RawRecord]:
        try:
            # Try reading with utf-8, fallback to latin-1
            try:
                df = pd.read_csv(file_path, dtype=str)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, dtype=str, encoding="latin-1")

            # Clean empty rows
            df = df.dropna(how="all")
            records: List[RawRecord] = []

            for idx, row in df.iterrows():
                # Convert row to dict, stripping column names and values
                clean_row = {}
                for col, val in row.items():
                    col_str = str(col).strip() if pd.notna(col) else ""
                    val_str = str(val).strip() if pd.notna(val) else ""
                    clean_row[col_str] = val_str

                # Skip completely blank rows
                if not any(clean_row.values()):
                    continue

                records.append(
                    RawRecord(
                        row_number=int(idx) + 2,  # 1-indexed, header is row 1
                        raw_data=clean_row,
                    )
                )

            return records
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}") from e
