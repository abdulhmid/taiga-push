from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx


class TaigaClientError(Exception):
    pass


class TaigaClient:
    def __init__(self, base_url: str, token: str) -> None:
        base_url = base_url.rstrip("/")
        self.base_url = base_url
        self.api_root = base_url if base_url.endswith("/api/v1") else f"{base_url}/api/v1"
        self.headers = {
            "Authorization": token if token.startswith("Bearer ") else f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.timeout = httpx.Timeout(20.0, connect=10.0)

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = urljoin(self.api_root + "/", path.lstrip("/"))
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            response = await client.request(method, url, **kwargs)
        if response.status_code >= 400:
            raise TaigaClientError(
                f"Taiga API error {response.status_code}: {response.text}"
            )
        return response.json()

    async def get_project_members(self, project_id: int) -> List[Dict[str, Any]]:
        return await self._request("GET", f"projects/{project_id}/users")

    async def get_sprints(self, project_id: int) -> List[Dict[str, Any]]:
        return await self._request("GET", f"milestones?project={project_id}")

    async def create_sprint(
        self,
        project_id: int,
        name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "project": project_id,
            "name": name,
            "status": "open",
        }
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["due_date"] = end_date
        return await self._request("POST", "milestones", json=payload)

    async def create_task(
        self,
        project_id: int,
        subject: str,
        description: str,
        milestone_id: int,
        assigned_to: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "project": project_id,
            "subject": subject,
            "description": description,
            "milestone": milestone_id,
        }
        if assigned_to:
            payload["assigned_to"] = assigned_to
            payload["owner"] = assigned_to
        return await self._request("POST", "tasks", json=payload)

    async def ping(self) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.api_root)
        return response.status_code < 400
