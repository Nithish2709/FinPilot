import os
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.repositories.account_repository import AccountRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentDetailResponse, DocumentResponse
from app.schemas.retrieval import DocumentSearchRequest, DocumentSearchResponse
from app.services.document_processing_service import DocumentProcessingService
from app.services.ingestion.ingestion_service import IngestionService
from app.services.ingestion.storage import StorageManager
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload financial statement",
    description="Upload a CSV, XLSX, or PDF document for statement ingestion and parsing.",
)
async def upload_document(
    file: UploadFile = File(...),
    account_id: Optional[uuid.UUID] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    # 1. Validate file extension
    filename = file.filename or ""
    _, ext = os.path.splitext(filename)
    clean_ext = ext.lower().strip()

    if clean_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: '{clean_ext}'. Supported extensions: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}",
        )

    # 2. Verify account belongs to user if account_id is supplied
    if account_id:
        account = await AccountRepository.get_by_id(db, account_id, current_user.id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account with id '{account_id}' not found for authenticated user.",
            )

    # 3. Store file safely to prevent path traversal and enforce size limit
    try:
        storage_key, file_size, abs_path = await StorageManager.save_upload_file(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}",
        )

    # 4. Create Document record in DB scoped to current_user.id
    doc_record = Document(
        user_id=current_user.id,
        filename=filename,
        mime_type=file.content_type,
        file_size=file_size,
        storage_key=storage_key,
        status=DocumentStatus.UPLOADED.value,
    )
    doc_record = await DocumentRepository.create(db, doc_record)

    # 5. Process document through ingestion pipeline
    processed_doc = await IngestionService.process_document(
        db=db,
        document_id=doc_record.id,
        user_id=current_user.id,
        file_path=abs_path,
        account_id=account_id,
    )

    # 6. Process document for RAG chunking and vector storage
    try:
        doc_proc_service = DocumentProcessingService()
        await doc_proc_service.process_document(
            db=db,
            document=processed_doc,
            file_path=abs_path,
        )
    except Exception:
        # Non-fatal to ingestion if RAG chunking fails on non-standard formats
        pass

    return DocumentResponse(
        document_id=processed_doc.id,
        filename=processed_doc.filename,
        status=processed_doc.status,
        total_records=processed_doc.total_records,
        successful_records=processed_doc.successful_records,
        failed_records=processed_doc.failed_records,
        duplicate_records=processed_doc.duplicate_records,
        error_message=processed_doc.error_message,
        created_at=processed_doc.created_at,
    )


@router.post(
    "/search",
    response_model=DocumentSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic document search",
    description="Performs semantic vector search across document chunks strictly scoped to the authenticated user.",
)
async def search_documents(
    payload: DocumentSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentSearchResponse:
    retrieval_service = RetrievalService()
    return await retrieval_service.search_documents(
        db=db,
        user_id=current_user.id,
        query=payload.query,
        top_k=payload.top_k,
        similarity_threshold=payload.similarity_threshold,
        document_id=payload.document_id,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document details and processing status",
    description="Fetches document status and ingestion metrics strictly scoped to the authenticated user.",
)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentDetailResponse:
    # Strictly query using document_id AND current_user.id
    document = await DocumentRepository.get_by_id_and_user(db, document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or does not belong to the authenticated user.",
        )

    return DocumentDetailResponse(
        document_id=document.id,
        filename=document.filename,
        status=document.status,
        total_records=document.total_records,
        successful_records=document.successful_records,
        failed_records=document.failed_records,
        duplicate_records=document.duplicate_records,
        error_message=document.error_message,
        mime_type=document.mime_type,
        file_size=document.file_size,
        storage_key=document.storage_key,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )
