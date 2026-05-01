# Taiga Push API

A FastAPI-based service for bulk importing tasks into Taiga sprints from PDF/TXT documents with Docker containerization, PostgreSQL database, and ISO 27001 compliance features.

## Features

- **Bulk Task Import**: Import multiple tasks from PDF or TXT documents directly into Taiga sprints
- **Document Parsing**: Automatic extraction of Talent, Note, and Estimation columns
- **Task Mapping**: Intelligent talent-to-assignee mapping against Taiga project members
- **Sprint Management**: Find existing sprints or create new ones with custom metadata
- **Audit Logging**: Complete audit trail with timestamps for compliance
- **Health Checks**: Liveness and readiness probes for container orchestration
- **Database**: Local PostgreSQL for task tracking and audit logs
- **Docker**: Production-ready multi-stage Dockerfile and Docker Compose setup
- **Security**: Token-based Taiga API authentication, least-privilege principles

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/abdulhmid/taiga-push.git
cd taiga-push
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
TAIGA_URL=https://api.taiga.io
TAIGA_TOKEN=Bearer <your_taiga_api_token>
DATABASE_URL=postgresql+asyncpg://taiga_push:secret@db:5432/taiga_push
```

### 3. Start the Service
```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Taiga Import
**`POST /api/v1/taiga/import`**

Import tasks from a document into Taiga.

Request:
- Content type: `multipart/form-data`
- Fields:
  - `taiga_url`
  - `token`
  - `project_id`
  - `sprint_name` (optional)
  - `sprint_start` (optional)
  - `sprint_end` (optional)
  - `document` — upload the TXT or PDF file directly

Example:
```bash
curl -X POST http://localhost:8000/api/v1/taiga/import \
  -F "taiga_url=https://api.taiga.io" \
  -F "token=Bearer <TOKEN>" \
  -F "project_id=12345" \
  -F "sprint_name=Sprint 1" \
  -F "sprint_start=2026-05-01" \
  -F "sprint_end=2026-05-15" \
  -F "document=@tasks.txt"
```

Response:
```json
{
  "created_tasks": 5,
  "failed_rows": [],
  "audit_log": [
    "2026-04-30T12:00:00Z - Starting Taiga import request",
    "2026-04-30T12:00:01Z - Parsed 5 row(s) from document",
    "2026-04-30T12:00:05Z - Taiga import request completed"
  ]
}
```

### Task Management

**`POST /api/v1/tasks`** – Create a local task
**`GET /api/v1/tasks`** – List all local tasks

### Health Endpoints

**`GET /api/v1/health`** – Basic health check
**`GET /api/v1/health/ready`** – Readiness probe (checks DB + optionally Taiga)
**`GET /api/v1/health/live`** – Liveness probe

See [docs/api.md](docs/api.md) for full endpoint documentation.

## Document Format

The input document (PDF or TXT) must contain parseable columns:
- **Talent**: Taiga assignee username or full name
- **Note**: Task subject/description
- **Estimation**: Numeric effort value (e.g., `3.5` or `4`)

Example TXT format:
```
Talent,Note,Estimation
Alice,Implement login flow,3
Bob,Design dashboard,5
```

For PDF files, extract to plain text first for best results.

## Architecture

```
┌─────────────────────────────────────────┐
│ FastAPI Application (app/main.py)       │
├─────────────────────────────────────────┤
│ Endpoints                               │
│ ├── /taiga/import (Taiga integration)  │
│ ├── /tasks (local DB)                  │
│ └── /health (readiness/liveness)       │
├─────────────────────────────────────────┤
│ Services                                │
│ ├── TaigaImportService                 │
│ ├── TaigaClient (HTTP)                 │
│ └── DocumentParser (PDF/TXT)           │
├─────────────────────────────────────────┤
│ Database (SQLAlchemy + AsyncPG)        │
│ └── PostgreSQL (tasks, audit logs)     │
└─────────────────────────────────────────┘
```

## Project Structure

```
app/
├── main.py                 # FastAPI app entry
├── core/
│   ├── config.py          # Settings & environment
│   └── database.py        # SQLAlchemy setup
├── api/v1/endpoints/
│   ├── taiga_import.py    # Taiga import endpoint
│   ├── tasks.py           # Local task CRUD
│   └── health.py          # Health checks
├── clients/
│   └── taiga_client.py    # Taiga API client
├── services/
│   └── taiga_import_service.py  # Import business logic
├── models/
│   └── task.py            # SQLAlchemy models
├── schemas/
│   ├── taiga.py           # Taiga import schemas
│   └── task.py            # Task schemas
└── utils/
    ├── doc_parser.py      # PDF/TXT parsing
    └── audit.py           # Audit logging

docs/
├── api.md                 # Full API reference
└── samples/               # Example documents

tests/
├── test_health.py         # Health endpoint tests
├── test_doc_parser.py     # Parser unit tests
└── test_config.py         # Config tests

docker-compose.yml         # Dev + Prod setup
Dockerfile                 # Multi-stage build
requirements.txt           # Python dependencies
.env.example              # Sample environment
```

## Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `TAIGA_URL` | Taiga API root URL | `https://api.taiga.io` |
| `TAIGA_TOKEN` | Taiga API token (from request) | `Bearer xxx` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@db:5432/db` |

Environment variables are loaded from `.env` at startup.

## Security & Compliance

- **Audit Logging**: All operations recorded with timestamps for ISO 27001 compliance
- **Least Privilege**: Token not stored in code; passed at request time
- **Data Minimization**: Sensitive data not cached unnecessarily
- **CORS**: Configured to allow cross-origin requests (adjustable in production)
- **Input Validation**: Pydantic v2 schemas validate all request data
- **Error Handling**: Structured error responses with appropriate HTTP codes

## Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Locally (without Docker)
```bash
uvicorn app.main:app --reload
```

### Run Tests
```bash
pytest tests/ -v
```

### Check Syntax
```bash
python3 -m py_compile app/**/*.py
```

## Deployment

### Docker Compose (Local/Dev)
```bash
docker compose up --build
```

### Docker Compose (Production)
Create `docker-compose.prod.yml` with:
- Non-root user
- Volume mounts for logs
- Environment-specific credentials
- Resource limits

### Kubernetes
Export as Helm chart or use:
```bash
docker push <registry>/taiga-push:latest
kubectl apply -f k8s/deployment.yaml
```

## Troubleshooting

### `.env: no such file or directory`
```bash
cp .env.example .env
```

### Database connection refused
Ensure `docker-compose.yml` has `db` service and `DATABASE_URL` matches the connection string.

### Taiga API errors
- Verify `TAIGA_TOKEN` has sufficient permissions
- Check `taiga_url` is correctly formatted (should end with `/api/v1` for self-hosted)
- Ensure `project_id` exists in Taiga

### Document parsing fails
- Verify PDF is converted to plain text first
- Check document has columns: `Talent`, `Note`, `Estimation`
- Ensure `Estimation` is numeric (not text)

## License

See LICENSE file.

## Contributing

Pull requests welcome. Please ensure:
1. Code passes syntax validation
2. Tests pass
3. Docs are updated
4. Commit messages follow conventional commits

## Support

For issues, questions, or contributions, open an issue on GitHub.
