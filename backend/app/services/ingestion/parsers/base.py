from abc import ABC, abstractmethod
from typing import List
from app.services.ingestion.models import RawRecord


class BaseParser(ABC):
    """Abstract base class for statement parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> List[RawRecord]:
        """
        Parses the document at file_path and extracts raw transaction records.
        """
        pass
