import os
from decimal import Decimal
import pytest

from app.services.ingestion.parsers.csv_parser import CSVParser
from app.services.ingestion.parsers.excel_parser import ExcelParser
from app.services.ingestion.parsers.pdf_parser import PDFParser
from app.services.ingestion.normalizer import Normalizer


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def test_csv_parser_fixture():
    csv_path = os.path.join(FIXTURES_DIR, "sample_transactions.csv")
    assert os.path.exists(csv_path)

    parser = CSVParser()
    records = parser.parse(csv_path)
    assert len(records) == 7

    # Check first record
    rec1 = records[0]
    assert rec1.row_number == 2
    assert "Swiggy" in rec1.raw_data.get("Description", "")


def test_excel_parser_fixture():
    xlsx_path = os.path.join(FIXTURES_DIR, "sample_transactions.xlsx")
    assert os.path.exists(xlsx_path)

    parser = ExcelParser()
    records = parser.parse(xlsx_path)
    assert len(records) == 3

    # Verify normalization from Excel record
    norm0 = Normalizer.normalize_record(records[0])
    assert norm0.description == "Uber Ride"
    assert norm0.amount == Decimal("250.00")
    assert norm0.transaction_type == "DEBIT"

    norm2 = Normalizer.normalize_record(records[2])
    assert norm2.description == "Cashback Refund"
    assert norm2.amount == Decimal("50.00")
    assert norm2.transaction_type == "REFUND"


def test_pdf_parser_fixture():
    pdf_path = os.path.join(FIXTURES_DIR, "sample_statement.pdf")
    assert os.path.exists(pdf_path)

    parser = PDFParser()
    records = parser.parse(pdf_path)
    assert len(records) >= 3

    # Check that rows were identified with dates and amounts
    first_record = records[0]
    assert "2026-09-01" in first_record.raw_data.get("date", "")
    assert "1299.00" in first_record.raw_data.get("amount", "")
