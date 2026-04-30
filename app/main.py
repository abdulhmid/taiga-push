from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.taiga_import import router as taiga_import_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.core.database import init_db

app = FastAPI(
    title="Taiga Push API",
    description="Bulk import tasks into Taiga sprints from PDF/TXT documents.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    allow_credentials=True,
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(taiga_import_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()
