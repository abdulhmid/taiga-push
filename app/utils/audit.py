from datetime import datetime
from typing import List


class AuditLog:
    def __init__(self) -> None:
        self.entries: List[str] = []

    def record(self, message: str) -> None:
        timestamp = datetime.utcnow().isoformat() + "Z"
        self.entries.append(f"{timestamp} - {message}")

    def get_entries(self) -> List[str]:
        return self.entries.copy()
