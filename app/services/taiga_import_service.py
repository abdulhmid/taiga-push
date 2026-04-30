from datetime import date
from typing import Any, Dict, List, Optional

from app.clients.taiga_client import TaigaClient, TaigaClientError
from app.schemas.taiga import (
    TaigaImportRequest,
    TaigaImportResponse,
    TaigaTaskResult,
)
from app.utils.audit import AuditLog
from app.utils.doc_parser import DocumentParseError, parse_document


class TaigaImportService:
    def __init__(self, client: TaigaClient) -> None:
        self.client = client

    async def import_tasks(self, request: TaigaImportRequest) -> TaigaImportResponse:
        audit = AuditLog()
        audit.record("Starting Taiga import request")

        try:
            rows = parse_document(request.doc_input.path, request.doc_input.format.value)
            audit.record(f"Parsed {len(rows)} row(s) from document")
        except DocumentParseError as exc:
            audit.record(f"Document parse failed: {exc}")
            raise ValueError(str(exc)) from exc

        sprint = await self._get_or_create_sprint(
            request.project_id,
            request.sprint_name,
            request.sprint_start,
            request.sprint_end,
            audit,
        )

        created_count = 0
        failed_rows: List[TaigaTaskResult] = []

        for row in rows:
            row_number = row.get("row_number", 0)
            talent = row["talent"]
            note = row["note"]
            estimation_raw = row["estimation"]
            subject = note if len(note) <= 120 else note[:117] + "..."

            try:
                estimation = float(estimation_raw)
            except ValueError:
                failed_rows.append(
                    TaigaTaskResult(
                        row_number=row_number,
                        subject=subject,
                        talent=talent,
                        estimation=0.0,
                        taiga_task_id=None,
                        status="failed",
                        message="Estimation must be numeric",
                    )
                )
                audit.record(f"Row {row_number} failed: invalid estimation '{estimation_raw}'")
                continue

            try:
                member_id = await self._resolve_talent(request.project_id, talent)
                if member_id is None:
                    raise TaigaClientError(f"No Taiga member found for talent '{talent}'")

                task = await self.client.create_task(
                    project_id=request.project_id,
                    subject=subject,
                    description=note,
                    milestone_id=sprint["id"],
                    assigned_to=member_id,
                )
                created_count += 1
                audit.record(
                    f"Created task for row {row_number} assigned to user {member_id}"
                )
            except TaigaClientError as exc:
                failed_rows.append(
                    TaigaTaskResult(
                        row_number=row_number,
                        subject=subject,
                        talent=talent,
                        estimation=estimation,
                        taiga_task_id=None,
                        status="failed",
                        message=str(exc),
                    )
                )
                audit.record(f"Row {row_number} failed: {exc}")

        audit.record("Taiga import request completed")

        return TaigaImportResponse(
            created_tasks=created_count,
            failed_rows=failed_rows,
            audit_log=audit.get_entries(),
        )

    async def _get_or_create_sprint(
        self,
        project_id: int,
        name: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
        audit: AuditLog,
    ) -> Dict[str, Any]:
        sprints = await self.client.get_sprints(project_id)
        if name:
            for sprint in sprints:
                if sprint.get("name") == name:
                    audit.record(f"Found existing sprint '{name}'")
                    return sprint

        if not name:
            raise ValueError("Sprint name is required when creating or selecting a sprint.")

        created = await self.client.create_sprint(
            project_id=project_id,
            name=name,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
        )
        audit.record(f"Created new sprint '{name}'")
        return created

    async def _resolve_talent(self, project_id: int, talent: str) -> Optional[int]:
        members = await self.client.get_project_members(project_id)
        search_value = talent.strip().lower()
        for member in members:
            username = str(member.get("username", "")).lower()
            full_name = str(member.get("full_name", "")).lower()
            if search_value in username or search_value in full_name:
                return member["id"]
        return None
