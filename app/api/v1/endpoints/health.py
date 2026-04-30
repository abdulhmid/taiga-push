from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx
from sqlalchemy import text

from app.core.database import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/ready")
async def readiness_check(taiga_url: Optional[str] = Query(None)):
    dependencies = {}
    db_status = "healthy"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = "unhealthy"
        dependencies["database"] = {"status": "unhealthy", "message": str(exc)}

    if taiga_url:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(taiga_url, follow_redirects=True)
                dependencies["taiga"] = {
                    "status": "healthy" if response.status_code < 400 else "unhealthy",
                    "status_code": response.status_code,
                }
            except Exception as exc:
                dependencies["taiga"] = {"status": "unhealthy", "message": str(exc)}

    if db_status == "unhealthy":
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "dependencies": dependencies},
        )

    return {"status": "ready", "dependencies": dependencies}


@router.get("/health/live")
async def liveness_check():
    return {"status": "alive"}
