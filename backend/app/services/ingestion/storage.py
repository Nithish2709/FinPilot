import os
import uuid
from pathlib import Path
import shutil
from fastapi import UploadFile

from app.core.config import settings


class StorageManager:
    """Safely saves and retrieves uploaded financial documents."""

    @staticmethod
    def get_upload_dir() -> Path:
        upload_path = Path(settings.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path

    @classmethod
    def generate_storage_key(cls, original_filename: str) -> str:
        """Generates a secure, collision-free storage key to prevent path traversal."""
        # Sanitize extension
        _, ext = os.path.splitext(original_filename)
        clean_ext = ext.lower().strip()
        if clean_ext not in settings.ALLOWED_EXTENSIONS:
            clean_ext = ".bin"
        return f"{uuid.uuid4()}{clean_ext}"

    @classmethod
    async def save_upload_file(cls, file: UploadFile) -> tuple[str, int, str]:
        """
        Saves an uploaded file to the secure local storage directory.
        Returns: (storage_key, file_size_in_bytes, absolute_path_str)
        """
        upload_dir = cls.get_upload_dir()
        storage_key = cls.generate_storage_key(file.filename or "upload")
        destination_path = upload_dir / storage_key

        size = 0
        try:
            with open(destination_path, "wb") as out_file:
                while chunk := await file.read(1024 * 1024):  # 1MB chunk
                    size += len(chunk)
                    if size > settings.MAX_UPLOAD_SIZE_BYTES:
                        raise ValueError(
                            f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES} bytes"
                        )
                    out_file.write(chunk)
        except Exception:
            if destination_path.exists():
                destination_path.unlink()
            raise
        finally:
            await file.seek(0)

        return storage_key, size, str(destination_path.resolve())

    @classmethod
    def get_file_path(cls, storage_key: str) -> Path:
        """Resolves storage key ensuring no directory traversal."""
        upload_dir = cls.get_upload_dir().resolve()
        file_path = (upload_dir / storage_key).resolve()
        if not str(file_path).startswith(str(upload_dir)):
            raise ValueError("Directory traversal attempt detected")
        return file_path
