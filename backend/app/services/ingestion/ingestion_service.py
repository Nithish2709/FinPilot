from datetime import datetime
from decimal import Decimal
import os
from typing import Optional, Set
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus
from app.models.transaction import Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.ingestion.duplicate_detector import DuplicateDetector
from app.services.ingestion.models import NormalizedTransaction
from app.services.ingestion.normalizer import Normalizer
from app.services.ingestion.parsers.base import BaseParser
from app.services.ingestion.parsers.csv_parser import CSVParser
from app.services.ingestion.parsers.excel_parser import ExcelParser
from app.services.ingestion.parsers.pdf_parser import PDFParser
from app.services.ingestion.validators import TransactionValidator


class IngestionService:
    """Orchestrates parsing, normalization, validation, deduplication, and persistence."""

    @classmethod
    def get_parser(cls, filename: str) -> BaseParser:
        _, ext = os.path.splitext(filename)
        ext = ext.lower().strip()
        if ext == ".csv":
            return CSVParser()
        elif ext in {".xlsx", ".xls"}:
            return ExcelParser()
        elif ext == ".pdf":
            return PDFParser()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @classmethod
    async def process_document(
        cls,
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        file_path: str,
        account_id: Optional[uuid.UUID] = None,
    ) -> Document:
        """Executes the full ingestion pipeline for an uploaded document."""
        document = await DocumentRepository.get_by_id_and_user(db, document_id, user_id)
        if not document:
            raise ValueError(f"Document {document_id} not found for user {user_id}")

        # Update status to PROCESSING
        document.status = DocumentStatus.PROCESSING.value
        await DocumentRepository.update(db, document)

        try:
            # 1. Select parser
            parser = cls.get_parser(document.filename)

            # 2. Extract raw records
            raw_records = parser.parse(file_path)
            total_records = len(raw_records)

            if total_records == 0:
                document.status = DocumentStatus.COMPLETED.value
                document.total_records = 0
                document.successful_records = 0
                document.failed_records = 0
                document.duplicate_records = 0
                return await DocumentRepository.update(db, document)

            # 3. Normalize records
            normalized_txns: list[NormalizedTransaction] = []
            for raw_rec in raw_records:
                norm_txn = Normalizer.normalize_record(raw_rec)
                # 4. Validate record
                norm_txn = TransactionValidator.validate(norm_txn)
                normalized_txns.append(norm_txn)

            # 5. Fetch existing fingerprints for deduplication
            valid_dates = [t.transaction_date for t in normalized_txns if t.transaction_date is not None]
            existing_fps: Set[str] = set()
            if valid_dates:
                min_date = min(valid_dates)
                max_date = max(valid_dates)
                existing_txns = await TransactionRepository.get_existing_transactions_for_fingerprinting(
                    db, user_id=user_id, min_date=min_date, max_date=max_date
                )
                for et in existing_txns:
                    dummy_norm = NormalizedTransaction(
                        row_number=0,
                        transaction_date=et.transaction_date,
                        description=et.description,
                        amount=et.amount,
                        currency=et.currency,
                        transaction_type=et.transaction_type,
                        merchant=et.merchant,
                        external_reference=et.external_reference,
                    )
                    existing_fps.add(
                        DuplicateDetector.compute_fingerprint(user_id, dummy_norm, et.account_id)
                    )

            # 6. Apply deterministic deduplication
            processed_txns = DuplicateDetector.filter_batch_duplicates(
                user_id=user_id,
                transactions=normalized_txns,
                existing_fingerprints=existing_fps,
                account_id=account_id,
            )

            # 7. Convert to SQLAlchemy models and calculate statistics
            successful_count = 0
            failed_count = 0
            duplicate_count = 0
            db_transactions: list[Transaction] = []

            # Ensure an account exists if none provided
            target_account_id = account_id
            if not target_account_id:
                default_acc = await AccountRepository.get_or_create_default(db, user_id)
                target_account_id = default_acc.id

            for txn in processed_txns:
                if not txn.is_valid:
                    failed_count += 1
                elif txn.is_duplicate:
                    duplicate_count += 1
                else:
                    successful_count += 1

                # Save all transactions (including invalid/duplicates with flags preserved)
                db_transactions.append(
                    Transaction(
                        user_id=user_id,
                        account_id=target_account_id,
                        source_document_id=document.id,
                        transaction_date=txn.transaction_date or datetime.now().date(),
                        merchant=txn.merchant,
                        description=txn.description or "Unspecified Description",
                        amount=txn.amount or Decimal("0.00"),
                        currency=txn.currency,
                        transaction_type=txn.transaction_type,
                        category=txn.category,
                        subcategory=txn.subcategory,
                        is_recurring=False,
                        external_reference=txn.external_reference,
                        is_duplicate=txn.is_duplicate,
                        is_valid=txn.is_valid,
                        validation_error=txn.validation_error,
                    )
                )

            # 8. Batch insert
            if db_transactions:
                await TransactionRepository.create_batch(db, db_transactions)

            # 9. Update Document status and record counters
            document.status = DocumentStatus.COMPLETED.value
            document.total_records = total_records
            document.successful_records = successful_count
            document.failed_records = failed_count
            document.duplicate_records = duplicate_count
            return await DocumentRepository.update(db, document)

        except Exception as e:
            document.status = DocumentStatus.FAILED.value
            document.error_message = str(e)
            return await DocumentRepository.update(db, document)
