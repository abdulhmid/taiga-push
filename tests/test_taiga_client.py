import pytest

from app.clients.taiga_client import TaigaClient


class DummyTaigaClient(TaigaClient):
    def __init__(self):
        super().__init__("https://api.taiga.io", "Bearer dummy-token")
        self.captured = None

    async def _request(self, method: str, path: str, **kwargs):
        self.captured = {
            "method": method,
            "path": path,
            "kwargs": kwargs,
        }
        return self.captured


@pytest.mark.asyncio
async def test_create_task_includes_estimated_dates():
    client = DummyTaigaClient()
    result = await client.create_task(
        project_id=123,
        subject="Example task",
        description="Do something",
        milestone_id=10,
        assigned_to=42,
        estimated_start="2026-05-01",
        estimated_finish="2026-05-15",
    )

    assert result["method"] == "POST"
    assert result["path"] == "tasks"
    assert result["kwargs"]["json"]["estimated_start"] == "2026-05-01"
    assert result["kwargs"]["json"]["estimated_finish"] == "2026-05-15"
