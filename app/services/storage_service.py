import os
from abc import ABC, abstractmethod
from app.core.config import settings


class BaseStorageService(ABC):
    """
    Abstract Storage Interface. Allows swapping local file storage 
    with AWS S3 or Google Cloud Storage in production.
    """

    @abstractmethod
    def save_file(self, filename: str, content: bytes) -> str:
        """Saves file content and returns the absolute or relative file path / URL."""
        pass

    @abstractmethod
    def get_file_path(self, filename: str) -> str:
        """Returns storage location path for a given filename."""
        pass

    @abstractmethod
    def file_exists(self, filename: str) -> bool:
        """Checks if file exists in storage."""
        pass


class LocalStorageService(BaseStorageService):
    """
    Local filesystem implementation of storage service.
    """

    def __init__(self, base_dir: str = settings.STORAGE_DIR):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def save_file(self, filename: str, content: bytes) -> str:
        file_path = os.path.join(self.base_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path

    def get_file_path(self, filename: str) -> str:
        return os.path.join(self.base_dir, filename)

    def file_exists(self, filename: str) -> bool:
        file_path = os.path.join(self.base_dir, filename)
        return os.path.exists(file_path)
