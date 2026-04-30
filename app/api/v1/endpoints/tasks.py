from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import async_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead

router = APIRouter(tags=["tasks"])


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


@router.post("/tasks", response_model=TaskRead)
async def create_task(task_in: TaskCreate, session: AsyncSession = Depends(get_db)):
    task = Task(
        subject=task_in.subject,
        description=task_in.description,
        talent=task_in.talent,
        estimation=task_in.estimation,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.get("/tasks", response_model=List[TaskRead])
async def list_tasks(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Task).order_by(Task.id.desc()))
    return result.scalars().all()
