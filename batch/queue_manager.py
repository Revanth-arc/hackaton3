from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class QueueItem:
    filename: str
    size_bytes: int


def build_queue(uploaded_files) -> List[QueueItem]:
    items: List[QueueItem] = []
    for f in uploaded_files:
        items.append(QueueItem(filename=f.name, size_bytes=getattr(f, "size", 0)))
    return items
