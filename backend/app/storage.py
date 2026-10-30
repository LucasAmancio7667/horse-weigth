"""Acesso ao Azure Blob Storage (Azurite no desenvolvimento local)."""

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

from .config import settings


def _client(*, fast: bool = False) -> BlobServiceClient:
    # fast=True: sem retentativas e com timeout curto, para o health check não travar
    kwargs = {"retry_total": 0, "connection_timeout": 2, "read_timeout": 3} if fast else {}
    return BlobServiceClient.from_connection_string(settings.azure_storage_connection_string, **kwargs)


def ensure_container() -> None:
    """Cria o container das fotos se ainda não existir."""
    container = _client().get_container_client(settings.azure_storage_container)
    try:
        container.create_container()
    except ResourceExistsError:
        pass


def upload_bytes(blob_name: str, data: bytes, content_type: str = "image/jpeg") -> None:
    from azure.storage.blob import ContentSettings

    blob = _client().get_blob_client(settings.azure_storage_container, blob_name)
    blob.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))


def download_bytes(blob_name: str) -> bytes:
    blob = _client().get_blob_client(settings.azure_storage_container, blob_name)
    return blob.download_blob().readall()


def is_available() -> bool:
    """True se o Blob Storage responde (usado em /api/health)."""
    try:
        _client(fast=True).get_service_properties()
        return True
    except Exception:
        return False
