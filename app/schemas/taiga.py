from datetime import date
from typing import List, Optional

from pydantic import BaseModel, AnyHttpUrl, constr


class TaigaImportRequest(BaseModel):
    taiga_url: AnyHttpUrl
    token: constr(min_length=10)
    project_id: int
    sprint_name: Optional[str]
    sprint_start: Optional[date]
    sprint_end: Optional[date]
    estimated_start: Optional[date]
    estimated_finish: Optional[date]
    document: bytes
    document_filename: str


class TaigaTaskResult(BaseModel):
    row_number: int
    subject: str
    talent: str
    estimation: float
    taiga_task_id: Optional[int]
    status: str
    message: Optional[str] = None


class TaigaImportResponse(BaseModel):
    created_tasks: int
    failed_rows: List[TaigaTaskResult]
    audit_log: List[str]
