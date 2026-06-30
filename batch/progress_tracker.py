from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class BatchItemStatus:
    filename: str
    size_bytes: int
    upload_status: str = "queued"  # queued|uploaded
    processing_status: str = "pending"  # pending|processing|success|cached|failed
    message: str | None = None
    metrics: dict = field(default_factory=dict)


@dataclass
class BatchProgress:
    batch_id: str
    total: int
    items: Dict[str, BatchItemStatus] = field(default_factory=dict)
    completed: int = 0
    failed: int = 0

    def remaining(self) -> int:
        return max(0, self.total - (self.completed + self.failed))

    def success_count(self) -> int:
        return self.completed

    def update_processing(self, filename: str, status: str, message: str | None = None, metrics: dict | None = None):
        item = self.items[filename]
        item.processing_status = status
        item.message = message
        if metrics:
            item.metrics = metrics

        if status in {"success", "cached"}:
            # increment completed once
            if item.message != "__counted__":
                self.completed += 1
                item.message = "__counted__"
                item.message = message
        elif status == "failed":
            if item.message != "__counted_failed__":
                self.failed += 1
                item.message = "__counted_failed__"
                item.message = message


class ProgressTracker:
    def create(self, batch_id: str, files: List[dict]) -> BatchProgress:
        progress = BatchProgress(batch_id=batch_id, total=len(files))
        for f in files:
            progress.items[f["filename"]] = BatchItemStatus(
                filename=f["filename"],
                size_bytes=f.get("size_bytes", 0),
            )
        return progress

