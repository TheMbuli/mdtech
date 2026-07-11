from __future__ import annotations

from pathlib import PurePosixPath
from tempfile import SpooledTemporaryFile

import requests
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


def clean_media_name(name: str) -> str:
    """Normalize a Django media name and reject unsafe paths."""
    normalized = PurePosixPath(str(name).replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise SuspiciousFileOperation(f"Chemin média invalide: {name!r}")
    value = normalized.as_posix().lstrip("/")
    if not value or value == ".":
        raise SuspiciousFileOperation("Chemin média vide.")
    return value


def public_id_for_name(name: str, prefix: str | None = None) -> str:
    """Map a relative media path to a stable Cloudinary public_id."""
    safe_name = clean_media_name(name)
    path = PurePosixPath(safe_name)
    without_suffix = path.with_suffix("").as_posix()
    folder = (prefix if prefix is not None else settings.CLOUDINARY_FOLDER).strip("/")
    return f"{folder}/{without_suffix}" if folder else without_suffix


def configure_cloudinary():
    import cloudinary

    cloudinary.config(**settings.CLOUDINARY_CONFIG)


def cloudinary_error_is_not_found(exc: Exception) -> bool:
    message = str(exc).lower()
    return "not found" in message or "404" in message


@deconstructible
class CloudinaryMediaStorage(Storage):
    """Django storage backend for user-uploaded media only."""

    resource_types = ("image", "raw", "video")

    def __init__(self, prefix: str | None = None):
        self.prefix = (prefix if prefix is not None else settings.CLOUDINARY_FOLDER).strip("/")

    def _public_id(self, name: str) -> str:
        return public_id_for_name(name, self.prefix)

    def _save(self, name, content):
        configure_cloudinary()
        import cloudinary.uploader

        safe_name = clean_media_name(name)
        result = cloudinary.uploader.upload(
            content,
            public_id=self._public_id(safe_name),
            resource_type="auto",
            overwrite=False,
            unique_filename=False,
            use_filename=False,
        )
        if not result.get("public_id"):
            raise OSError("Cloudinary n'a pas confirmé l'upload du média.")
        return safe_name

    def url(self, name):
        configure_cloudinary()
        from cloudinary.utils import cloudinary_url

        url, _options = cloudinary_url(
            self._public_id(name),
            secure=True,
            resource_type="image",
            fetch_format="auto",
            quality="auto",
        )
        return url

    def exists(self, name):
        configure_cloudinary()
        import cloudinary.api

        public_id = self._public_id(name)
        for resource_type in self.resource_types:
            try:
                cloudinary.api.resource(public_id, resource_type=resource_type)
                return True
            except Exception as exc:
                if cloudinary_error_is_not_found(exc):
                    continue
                raise OSError("Impossible de vérifier l'existence du média Cloudinary.") from exc
        return False

    def delete(self, name):
        configure_cloudinary()
        import cloudinary.uploader

        public_id = self._public_id(name)
        for resource_type in self.resource_types:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            if result.get("result") in {"ok", "not found"}:
                return

    def size(self, name):
        configure_cloudinary()
        import cloudinary.api

        public_id = self._public_id(name)
        for resource_type in self.resource_types:
            try:
                result = cloudinary.api.resource(public_id, resource_type=resource_type)
                return int(result.get("bytes", 0))
            except Exception as exc:
                if cloudinary_error_is_not_found(exc):
                    continue
                raise OSError("Impossible de lire les métadonnées Cloudinary.") from exc
        raise FileNotFoundError(clean_media_name(name))

    def _open(self, name, mode="rb"):
        response = requests.get(self.url(name), timeout=30)
        response.raise_for_status()
        tmp = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
        tmp.write(response.content)
        tmp.seek(0)
        return File(tmp, name=clean_media_name(name))
