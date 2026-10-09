import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Tuple

ALLOWED_CONTENT_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "text/plain",
    "application/octet-stream",
}

FILE_EXTENSIONS = {".csv"}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

@dataclass(frozen=True)
class UploadRequest:
    filename: str
    content_type: str
    job_id: str
    s3_key: str
    file_size: int | None = None


def validate_upload_payload(body: Dict[str, Any]) -> Tuple[UploadRequest | None, str | None]:
    if not isinstance(body, dict):
        return None, "Request body must be a JSON object"

    filename = body.get("filename")
    if not filename or not isinstance(filename, str) or not filename.strip():
        return None, "Missing or invalid 'filename' field"

    filename = filename.strip()
    _, ext = os.path.splitext(filename)

    if ext.lower() not in FILE_EXTENSIONS:
        return None, "Invalid file extension"

    content_type = body.get("contentType", "text/csv")
    if content_type not in ALLOWED_CONTENT_TYPES:
        return None, "Invalid content type"

    file_size = body.get("fileSize")
    if file_size is not None:
        if not isinstance(file_size, int) or file_size <= 0:
            return None, "Invalid 'fileSize' field"
        if file_size > MAX_FILE_SIZE_BYTES:
            return None, "File size exceeds the maximum allowed limit"

    job_id = str(uuid.uuid4())
    s3_key = f"uploads/{job_id}/{filename}"

    return UploadRequest(
        filename=filename,
        content_type=content_type,
        job_id=job_id,
        s3_key=s3_key,
        file_size=file_size,
    ), None 
