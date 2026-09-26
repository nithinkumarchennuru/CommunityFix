from __future__ import annotations

import os
from typing import IO, Any

from flask import current_app

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:  # pragma: no cover - optional dependency
    cloudinary = None

SUPPORTED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_TYPES = {"PROBLEM", "BEFORE_WORK", "AFTER_WORK"}


def _get_max_image_size_mb() -> int:
    value = current_app.config.get("MAX_IMAGE_SIZE_MB", 5)
    try:
        return max(int(value), 1)
    except (TypeError, ValueError):
        return 5


def _get_max_images_per_type() -> int:
    value = current_app.config.get("MAX_IMAGES_PER_TYPE", 5)
    try:
        return max(int(value), 1)
    except (TypeError, ValueError):
        return 5


def _safe_file_name(filename: str) -> str:
    base = os.path.basename(filename or "upload")
    name, ext = os.path.splitext(base)
    cleaned = (name or "upload").replace("..", "").replace("/", "").replace("\\", "")
    cleaned = "".join(ch for ch in cleaned if ch.isalnum() or ch in {"-", "_"})
    if not cleaned:
        cleaned = "upload"
    return f"{cleaned}{ext.lower()}"


def validate_image(file: Any, max_size_mb: int | None = None) -> bool:
    if file is None:
        raise ValueError("No file was provided")

    if getattr(file, "filename", None) is None or str(file.filename).strip() == "":
        raise ValueError("Invalid file name")

    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size <= 0:
        raise ValueError("File is empty")

    max_bytes = (max_size_mb if max_size_mb is not None else _get_max_image_size_mb()) * 1024 * 1024
    if size > max_bytes:
        raise ValueError(f"File exceeds the maximum allowed size of {max_size_mb or _get_max_image_size_mb()} MB")

    mime_type = getattr(file, "content_type", None) or ""
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        raise ValueError("Unsupported file type. Allowed formats: JPEG, PNG, WEBP")

    _safe_file_name(getattr(file, "filename", "upload"))
    return True


def _cloudinary_configured() -> bool:
    return bool(
        current_app.config.get("CLOUDINARY_CLOUD_NAME")
        and current_app.config.get("CLOUDINARY_API_KEY")
        and current_app.config.get("CLOUDINARY_API_SECRET")
    ) and cloudinary is not None


def upload_image(file: Any, folder: str, public_id: str | None = None) -> dict[str, str]:
    if not _cloudinary_configured():
        raise ValueError("Image storage is not configured. Please set Cloudinary environment variables.")

    validate_image(file)
    safe_name = _safe_file_name(getattr(file, "filename", "upload"))
    file.seek(0)
    upload_options: dict[str, Any] = {"folder": folder, "resource_type": "image"}
    if public_id:
        upload_options["public_id"] = public_id
    else:
        upload_options["public_id"] = safe_name.rsplit(".", 1)[0]

    try:
        result = cloudinary.uploader.upload(file, **upload_options)
    except Exception as exc:  # pragma: no cover - cloud dependency path
        raise ValueError("Image upload failed") from exc

    image_url = result.get("secure_url") or result.get("url")
    storage_id = result.get("public_id") or result.get("asset_id") or public_id or safe_name
    if not image_url or not storage_id:
        raise ValueError("Image upload returned incomplete metadata")

    return {"url": image_url, "storage_id": storage_id}


def delete_image(storage_id: str) -> bool:
    if not storage_id:
        return False
    if not _cloudinary_configured():
        return False
    try:
        cloudinary.uploader.destroy(storage_id, resource_type="image")
        return True
    except Exception:
        return False


def get_image_limit_for_type(image_type: str) -> int:
    image_type = str(image_type).upper()
    if image_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Invalid image type")
    return _get_max_images_per_type()
