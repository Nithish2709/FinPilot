from typing import List
import pandas as pd

from app.services.ingestion.models import RawRecord
from app.services.ingestion.parsers.base import BaseParser


class ExcelParser(BaseParser):
    """Parses Excel (.xlsx) financial statements using pandas/openpyxl."""

    def parse(self, file_path: str) -> List[RawRecord]:
        try:
            df = pd.read_excel(file_path, dtype=str, engine="openpyxl")
            df = df.dropna(how="all")
            records: List[RawRecord] = []

            for idx, row in df.iterrows():
                clean_row = {}
                for col, val in row.items():
                    col_str = str(col).strip() if pd.notna(col) else ""
                    val_str = str(val).strip() if pd.notna(val) else ""
                    clean_row[col_str] = val_str

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
            raise ValueError(f"Failed to parse Excel file: {str(e)}") from e
