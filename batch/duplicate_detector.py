from __future__ import annotations

import hashlib
from dataclasses import dataclass

from database.repository import get_complaint_by_hash


@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    existing_data: dict | None = None
    file_hash: str | None = None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_duplicate(file_bytes: bytes) -> DuplicateCheckResult:
    file_hash = sha256_bytes(file_bytes)
    existing = get_complaint_by_hash(file_hash)
    return DuplicateCheckResult(
        is_duplicate=existing is not None,
        existing_data=existing,
        file_hash=file_hash,
    )
