import re
from typing import List, Optional
import fitz  # PyMuPDF

from app.services.ingestion.models import RawRecord
from app.services.ingestion.parsers.base import BaseParser


class PDFParser(BaseParser):
    """
    Parses statement text from PDF documents using PyMuPDF (fitz).
    Extracts tabular rows using common date-driven statement regex patterns.
    """

    # Matches common statement dates at line starts, e.g., 2026-09-15, 15/09/2026, 15-09-2026, 15 Sep 2026
    DATE_PREFIX_REGEX = re.compile(
        r"^(\d{1,4}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})\s+(.+)$"
    )

    def parse(self, file_path: str) -> List[RawRecord]:
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF document: {str(e)}") from e

        all_text = ""
        records: List[RawRecord] = []
        row_counter = 1

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                all_text += page_text

                lines = page_text.splitlines()
                for line in lines:
                    line_str = line.strip()
                    if not line_str:
                        continue

                    match = self.DATE_PREFIX_REGEX.match(line_str)
                    if match:
                        date_str = match.group(1).strip()
                        remainder = match.group(2).strip()

                        # Extract numbers at the end of the line which usually represent Debit/Credit/Balance
                        # E.g. "Starbucks Coffee 450.00 12050.00" or "Salary 50000.00 CR"
                        tokens = remainder.split()
                        amount_token: Optional[str] = None
                        txn_type_hint: Optional[str] = None
                        desc_tokens = []

                        # Scan tokens backwards for amounts and markers
                        i = len(tokens) - 1
                        while i >= 0:
                            token = tokens[i].replace(",", "")
                            # Check for CR / DR marker
                            if token.upper() in {"CR", "CREDIT"}:
                                txn_type_hint = "CREDIT"
                                i -= 1
                                continue
                            elif token.upper() in {"DR", "DEBIT"}:
                                txn_type_hint = "DEBIT"
                                i -= 1
                                continue

                            # Check for decimal amount
                            try:
                                float(token)
                                if amount_token is None:
                                    amount_token = token
                                i -= 1
                                continue
                            except ValueError:
                                # Not an amount, remainder is part of description
                                desc_tokens = tokens[: i + 1]
                                break

                        desc_str = " ".join(desc_tokens) if desc_tokens else remainder

                        raw_dict = {
                            "date": date_str,
                            "description": desc_str,
                            "amount": amount_token or "",
                        }
                        if txn_type_hint:
                            raw_dict["type"] = txn_type_hint

                        records.append(
                            RawRecord(
                                row_number=row_counter,
                                raw_data=raw_dict,
                            )
                        )
                        row_counter += 1

            if not all_text.strip():
                raise ValueError("PDF has no extractable text. Scanned document requires OCR.")

            return records
        finally:
            doc.close()
