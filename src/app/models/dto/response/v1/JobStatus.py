from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class JobStatus:
    job_id: str
    status: str
    created_at: datetime
    file_count: int
    processed_count: int = 0
    error_count: int = 0
    errors: List[str] = None
    results: List[dict] = None
