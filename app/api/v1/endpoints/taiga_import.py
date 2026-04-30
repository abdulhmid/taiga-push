from fastapi import APIRouter, HTTPException
from app.schemas.taiga import TaigaImportRequest, TaigaImportResponse
from app.clients.taiga_client import TaigaClient, TaigaClientError
from app.services.taiga_import_service import TaigaImportService

router = APIRouter(tags=["taiga"])


@router.post("/taiga/import", response_model=TaigaImportResponse)
async def import_taiga_tasks(request: TaigaImportRequest):
    client = TaigaClient(base_url=str(request.taiga_url), token=request.token)
    service = TaigaImportService(client)

    try:
        response = await service.import_tasks(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TaigaClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return response
