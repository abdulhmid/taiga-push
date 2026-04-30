# Taiga Push API Documentation

## Overview
API for bulk importing tasks into a Taiga sprint from document input (PDF/TXT) and for basic task management.

Base URL: `http://localhost:8000/api/v1`

## Authentication
- Taiga integration uses the `token` field in the import request body.
- The service itself does not implement app-level authentication yet.
- The `token` value should be a valid Taiga API token, preferably prefixed with `Bearer `.

## Endpoints

### 1. `POST /taiga/import`
Bulk import tasks into Taiga using a document file path and sprint metadata.

Request body:
```json
{
  "taiga_url": "https://api.taiga.io",
  "token": "Bearer <TOKEN_TAIGA_API>",
  "project_id": 12345,
  "sprint_name": "Sprint 1",
  "sprint_start": "2026-05-01",
  "sprint_end": "2026-05-15",
  "doc_input": {
    "path": "/path/to/tasks.txt",
    "format": "txt"
  }
}
```

Notes:
- `project_id` is required.
- `sprint_name`, `sprint_start`, and `sprint_end` are optional, but if you want the API to create a sprint you must supply `sprint_name`.
- `doc_input.format` must be either `pdf` or `txt`.
- The document must contain columns for `Talent`, `Note`, and `Estimation`.

Success response example:
```json
{
  "created_tasks": 5,
  "failed_rows": [
    {
      "row_number": 4,
      "subject": "Review user guide",
      "talent": "Jane Doe",
      "estimation": 0.0,
      "taiga_task_id": null,
      "status": "failed",
      "message": "Estimation must be numeric"
    }
  ],
  "audit_log": [
    "2026-04-30T12:00:00Z - Starting Taiga import request",
    "2026-04-30T12:00:01Z - Parsed 6 row(s) from document",
    "2026-04-30T12:00:05Z - Created task for row 1 assigned to user 42",
    "2026-04-30T12:00:06Z - Taiga import request completed"
  ]
}
```

Failure responses:
- `400 Bad Request` for document parsing errors or invalid request fields.
- `502 Bad Gateway` for Taiga API failures.

### 2. `POST /tasks`
Create a local task record in the service database.

Request body:
```json
{
  "subject": "Implement login flow",
  "description": "Create login endpoint and UI interactions.",
  "talent": "John Doe",
  "estimation": 4.0
}
```

Success response:
```json
{
  "id": 1,
  "subject": "Implement login flow",
  "description": "Create login endpoint and UI interactions.",
  "talent": "John Doe",
  "estimation": 4.0,
  "created_at": "2026-04-30T12:15:00"
}
```

### 3. `GET /tasks`
Retrieve all local task records.

Success response example:
```json
[
  {
    "id": 1,
    "subject": "Implement login flow",
    "description": "Create login endpoint and UI interactions.",
    "talent": "John Doe",
    "estimation": 4.0,
    "created_at": "2026-04-30T12:15:00"
  }
]
```

### 4. `GET /health`
Basic liveness health check.

Success response:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-30T12:20:00Z"
}
```

### 5. `GET /health/ready`
Readiness probe that validates database connectivity and optionally Taiga connectivity.

Query parameters:
- `taiga_url` (optional)

Success response when ready:
```json
{
  "status": "ready",
  "dependencies": {
    "database": {"status": "healthy"},
    "taiga": {"status": "healthy", "status_code": 200}
  }
}
```

Failure response when a dependency is unhealthy:
```json
{
  "status": "not_ready",
  "dependencies": {
    "database": {"status": "unhealthy", "message": "..."}
  }
}
```

### 6. `GET /health/live`
Liveness probe for the running process.

Success response:
```json
{
  "status": "alive"
}
```

## Environment Configuration
Create a `.env` file at project root with your local settings.

Example:
```env
TAIGA_URL=https://api.taiga.io
TAIGA_TOKEN=Bearer <TOKEN_TAIGA_API>
DATABASE_URL=postgresql+asyncpg://taiga_push:secret@db:5432/taiga_push
```

## Docker / Local Startup
Use Docker Compose to start the service and the PostgreSQL database:
```bash
docker compose up --build
```

Then access the API on:
- `http://localhost:8000/api/v1/taiga/import`
- `http://localhost:8000/api/v1/tasks`
- `http://localhost:8000/api/v1/health`

## Input Document Requirements
The import endpoint expects document input with these columns:
- `Talent` → Taiga assignee lookup
- `Note` → task subject/description
- `Estimation` → numeric effort value

If the document is `pdf`, the API reads extracted text. For best results, convert PDF to plain text first.

## Notes
- The Taiga import request uses runtime request parameters for project and sprint metadata.
- The local `/tasks` endpoint is a simple database-backed task API for verification and Postman testing.
- The service currently uses token-based Taiga integration from the request body, not app-level authentication.
