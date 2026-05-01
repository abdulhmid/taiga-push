from datetime import date
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import AnyHttpUrl, constr

from app.schemas.taiga import TaigaImportRequest, TaigaImportResponse
from app.clients.taiga_client import TaigaClient, TaigaClientError
from app.services.taiga_import_service import TaigaImportService

router = APIRouter(tags=["taiga"])


@router.post("/taiga/import", response_model=TaigaImportResponse)
async def import_taiga_tasks(
    taiga_url: AnyHttpUrl = Form(...),
    token: constr(min_length=10) = Form(...),
    project_id: int = Form(...),
    sprint_name: Optional[str] = Form(None),
    sprint_start: Optional[date] = Form(None),
    sprint_end: Optional[date] = Form(None),
    estimated_start: Optional[date] = Form(None),
    estimated_finish: Optional[date] = Form(None),
    document: UploadFile = File(...),
):
    request = TaigaImportRequest(
        taiga_url=taiga_url,
        token=token,
        project_id=project_id,
        sprint_name=sprint_name,
        sprint_start=sprint_start,
        sprint_end=sprint_end,
        estimated_start=estimated_start,
        estimated_finish=estimated_finish,
        document=await document.read(),
        document_filename=document.filename,
    )

    client = TaigaClient(base_url=str(request.taiga_url), token=request.token)
    service = TaigaImportService(client)

    try:
        response = await service.import_tasks(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TaigaClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return response
