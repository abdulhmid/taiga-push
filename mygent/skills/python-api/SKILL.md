---
name: Python API Developer (FastAPI)
description: |
  Membuat, mengembangkan, dan memperbaiki RESTful API menggunakan Python + FastAPI.
  Gunakan skill ini ketika user meminta: "buat API", "buat endpoint", "develop backend API", 
  "CRUD API", "integrasi database", "buat authentication", "migrasi dari Flask / Django", 
  atau "improve performance API Python".
version: 1.1
last_updated: 2026-04-27
tags: [python, fastapi, backend, api, rest, pydantic]
---

# Skill: Python API Developer (FastAPI)

## Goal
Menghasilkan kode API Python yang **production-ready**, clean, scalable, type-safe, async-friendly, dengan dokumentasi otomatis (Swagger/ReDoc), error handling yang baik, dan struktur yang mudah dikembangkan.

## When to Use This Skill
- User meminta pembuatan API baru atau fitur backend.
- Perbaikan/refactoring kode API existing.
- Desain arsitektur backend (routers, services, repositories).
- Integrasi dengan database (SQLAlchemy, Tortoise, Prisma, dll.), authentication (JWT, OAuth2), atau third-party services.
- Jangan gunakan jika user hanya minta script sederhana (gunakan skill coding general).

## Latest Stable & Best Practices (Update 2026)
- **FastAPI**: 0.136.x (terbaru per April 2026)
- **Python**: 3.12 atau 3.13 (rekomendasi)
- **Pydantic**: v2 (model_config)
- Gunakan **modular structure** (domain/feature based)
- Selalu gunakan **async** untuk I/O bound operations
- Pisahkan: Routers → Services → Repositories → Models/Schemas
- Gunakan dependency injection (`Depends`)
- Error handling dengan custom HTTPException + structured response
- Security: OAuth2PasswordBearer, JWT, CORS middleware, rate limiting
- Testing: pytest + httpx + pytest-asyncio

## Recommended Project Structure (2026 Best Practice)

```bash
project/
├── app/
│   ├── main.py
│   ├── core/               # config, security, database, logging
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/  # routers per feature (users.py, items.py)
│   ├── models/             # SQLAlchemy / Tortoise models
│   ├── schemas/            # Pydantic schemas (request/response)
│   ├── services/           # business logic
│   ├── repositories/       # data access layer
│   ├── dependencies/       # reusable Depends
│   └── utils/
├── alembic/                # migrations (jika pakai SQLAlchemy)
├── tests/
├── requirements.txt
└── .env
```

## Quality Gates & Compliance Standards

### 1. Health Check Implementation (Required)
Setiap API **WAJIB** memiliki endpoint health check untuk monitoring dan orchestration:

```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter
from app.core.database import get_db_connection_status
from app.core.redis import get_redis_status

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check - response cepat"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/ready")
async def readiness_check():
    """Readiness probe - cek dependencies (DB, Redis, etc.)"""
    db_status = await get_db_connection_status()
    redis_status = await get_redis_status()
    
    is_ready = db_status["healthy"] and redis_status["healthy"]
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "dependencies": {
            "database": db_status,
            "redis": redis_status
        }
    }

@router.get("/health/live")
async def liveness_check():
    """Liveness probe - apakah process masih berjalan"""
    return {"status": "alive"}
```

**Implementation Requirements:**
- `/health` - Basic endpoint (tanpa dependency check)
- `/health/ready` - Readiness probe (cek DB, cache, external services)
- `/health/live` - Liveness probe (process alive check)
- Response time < 100ms untuk `/health`
- Timeout handling untuk dependency checks

### 2. OWASP Security Standards (2026)
Setiap endpoint **WAJIB** comply dengan OWASP Top 10:

#### A01: Broken Access Control
```python
# Gunakan dependency injection untuk authorization
from app.dependencies.auth import get_current_user, require_role

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role(["admin"]))
):
    # Implementation
```

#### A02: Cryptographic Failures
```python
# Enkripsi data sensitif & gunakan HTTPS
from app.core.security import encrypt_data, decrypt_data

# Password hashing dengan Argon2 (bukan bcrypt)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

#### A03: Injection
```python
# Selalu gunakan parameterized queries (SQLAlchemy ORM)
# Validasi input dengan Pydantic v2
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        return v
```

#### A04: Insecure Design
```python
# Rate limiting dengan slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # Max 5 requests per minute
async def login(request: Request, credentials: OAuth2PasswordRequestForm):
    # Implementation
```

#### A05: Security Misconfiguration
```python
# Secure headers dengan middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.security import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-domain.com"],  # Jangan gunakan "*"
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

#### A06: Vulnerable and Outdated Components
```python
# requirements.txt - Pin versions
fastapi==0.136.0
uvicorn[standard]==0.34.0
pydantic==2.10.0
sqlalchemy==2.0.36
alembic==1.15.0
python-jose[cryptography]==3.4.0
argon2-cffi==23.1.0
slowapi==0.2.0
```

#### A07: Authentication Failures
```python
# JWT dengan expiry & refresh token
from app.core.security import create_access_token, create_refresh_token

access_token = create_access_token(
    data={"sub": user.email, "type": "access"},
    expires_delta=timedelta(minutes=15)
)
refresh_token = create_refresh_token(
    data={"sub": user.email, "type": "refresh"},
    expires_delta=timedelta(days=7)
)
```

#### A08: Software and Data Integrity Failures
```python
# Validasi integrity dengan hashing
import hashlib
from app.core.security import verify_signature

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hashlib.sha256(f"{secret}.{payload}".encode()).hexdigest()
    return secrets.compare_digest(expected, signature)
```

#### A09: Security Logging and Monitoring Failures
```python
# Structured logging dengan audit trail
from loguru import logger
import structlog

logger.add(
    "logs/security.log",
    format="{time:ISO8601} | {level} | {message}",
    level="INFO",
    rotation="1 day",
    retention="30 days"
)

# Log semua authentication events
logger.info("login_attempt", extra={
    "user_email": email,
    "ip_address": request.client.host,
    "user_agent": request.headers.get("user-agent"),
    "success": True/False
})
```

#### A10: Server-Side Request Forgery (SSRF)
```python
# Validasi URL sebelum fetch
from urllib.parse import urlparse
import ipaddress

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        return False
    
    # Block private IP ranges
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        return not ip.is_private
    except ValueError:
        return False
```

### 3. ISO 27001 Compliance Architecture

#### Referensi Arsitektur untuk Compliance

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (WAF)                      │
│              (AWS ALB / Cloudflare / Nginx)                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│         - Rate Limiting                                     │
│         - Authentication (JWT Validation)                   │
│         - Request Validation                                │
│         - CORS Policy                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Application Layer (FastAPI)                 │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │   Routers   │  Services   │Repositories │   Models    │ │
│  │  (Endpoints)│ (Business   │  (Data      │  (Schema)   │ │
│  │             │   Logic)    │  Access)    │             │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Security Middleware                    │   │
│  │  - Input Sanitization                               │   │
│  │  - SQL Injection Prevention                         │   │
│  │  - XSS Protection                                   │   │
│  │  - CSRF Protection                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   S3/MinIO   │      │
│  │  (Primary)   │  │   (Cache)    │  │  (Storage)   │      │
│  │  - SSL/TLS   │  │  - Auth      │  │  - Signed    │      │
│  │  - Encryption│  │  - Encryption│  │    URLs      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Monitoring & Audit Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Logging    │  │  Metrics     │  │   Tracing    │      │
│  │  (ELK Stack) │  │ (Prometheus) │  │  (Jaeger)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

#### ISO 27001 Control Implementation

| ISO Control | Implementation | File/Component |
|-------------|----------------|----------------|
| A.9.2.1 (User Registration) | `POST /auth/register` dengan email verification | `app/api/v1/endpoints/auth.py` |
| A.9.2.6 (Password Management) | Argon2 hashing, min 8 chars, complexity rules | `app/core/security.py` |
| A.9.4.2 (Privileged Access) | Role-based access control (RBAC) | `app/dependencies/auth.py` |
| A.12.4.1 (Event Logging) | Structured logging dengan audit trail | `app/core/logging_config.py` |
| A.13.1.1 (Network Controls) | CORS, firewall rules, VPC | `app/main.py`, infra config |
| A.13.1.3 (Segregation) | Database user permissions, schema separation | DB migration scripts |
| A.14.2.1 (Secure Development) | Input validation, parameterized queries | All endpoints |
| A.16.1.1 (Incident Response) | Error handling, alerting | `app/core/exceptions.py` |

### 4. Testing Requirements (Quality Gate)

```python
# tests/test_health.py
async def test_health_endpoint():
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# tests/test_security.py
async def test_sql_injection_prevention():
    response = await client.get("/users?id=1' OR '1'='1")
    assert response.status_code == 422  # Validation error

async def test_rate_limiting():
    for _ in range(10):
        response = await client.post("/login", data=credentials)
    assert response.status_code == 429  # Too Many Requests
```

### 5. Compliance Checklist

Sebelum deploy, pastikan:

- [ ] Health check endpoints implemented (`/health`, `/health/ready`, `/health/live`)
- [ ] OWASP Top 10 controls implemented
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options)
- [ ] Rate limiting enabled
- [ ] Input validation dengan Pydantic
- [ ] Authentication & authorization implemented
- [ ] Audit logging enabled
- [ ] Database encryption at-rest & in-transit
- [ ] Secrets management (environment variables / vault)
- [ ] Error handling tidak leak sensitive information
- [ ] CORS configured properly
- [ ] HTTPS enforced in production
- [ ] Dependencies up-to-date (run `pip-audit` / `safety`)
- [ ] Security tests passing

### 6. Auto-Generated Unit Tests (Required)

Setiap endpoint/function yang dibuat **WAJIB** memiliki unit test dengan coverage minimal 80%.

#### A. Test Structure & Organization

```bash
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures & test config
├── unit/                       # Unit tests (isolated)
│   ├── __init__.py
│   ├── test_schemas.py         # Pydantic model tests
│   ├── test_services.py        # Business logic tests
│   ├── test_repositories.py    # Data access tests
│   └── test_dependencies.py    # Auth & dependency tests
├── integration/                # Integration tests (API + DB)
│   ├── __init__.py
│   ├── test_auth.py            # Authentication flows
│   ├── test_users.py           # User CRUD operations
│   ├── test_health.py          # Health check endpoints
│   └── test_security.py        # OWASP security tests
├── e2e/                        # End-to-end tests (opsional)
│   └── test_user_journey.py
└── utils/
    ├── __init__.py
    └── factories.py            # Test data factories
```

#### B. Test Template untuk Setiap Endpoint

**Template: tests/unit/test_services.py**
```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

class TestUserService:
    """Unit tests untuk UserService - isolated, no DB"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def user_service(self, mock_db):
        """Service instance dengan mock DB"""
        return UserService(db=mock_db)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_db):
        """Test happy path - user berhasil dibuat"""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!"
        )
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_value"
        )
        
        # Mock repository return value
        with patch.object(user_service.user_repo, 'create', return_value=mock_user):
            # Act
            result = await user_service.create_user(user_data)
            
            # Assert
            assert result is not None
            assert result.username == "testuser"
            assert result.email == "test@example.com"
            user_service.user_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, mock_db):
        """Test validation - email sudah terdaftar"""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="existing@example.com",
            password="SecurePass123!"
        )
        
        # Mock repository raise exception
        with patch.object(
            user_service.user_repo, 
            'create',
            side_effect=ValueError("Email already registered")
        ):
            # Act & Assert
            with pytest.raises(ValueError, match="Email already registered"):
                await user_service.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service, mock_db):
        """Test - user tidak ditemukan"""
        # Arrange
        user_id = 999
        
        with patch.object(
            user_service.user_repo, 
            'get_by_id',
            return_value=None
        ):
            # Act & Assert
            result = await user_service.get_user_by_id(user_id)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_service, mock_db):
        """Test - user berhasil dihapus"""
        # Arrange
        user_id = 1
        mock_user = User(id=1, username="testuser", email="test@example.com")
        
        with patch.object(user_service.user_repo, 'get_by_id', return_value=mock_user):
            with patch.object(user_service.user_repo, 'delete') as mock_delete:
                # Act
                await user_service.delete_user(user_id)
                
                # Assert
                mock_delete.assert_called_once_with(1)
```

**Template: tests/integration/test_users.py**
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.core.database import Base
from app.core.security import create_access_token

@pytest.fixture
async def client():
    """Test client dengan test database"""
    # Setup test database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def auth_token(client):
    """Generate valid JWT token untuk authenticated requests"""
    token_data = {"sub": "test@example.com", "type": "access"}
    return create_access_token(token_data)

class TestUserEndpoints:
    """Integration tests untuk User API"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, client):
        """Test endpoint POST /api/v1/users"""
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass123!"
        }
        
        response = await client.post("/api/v1/users", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "password" not in data  # Security check
    
    @pytest.mark.asyncio
    async def test_get_users_authenticated(self, client, auth_token):
        """Test endpoint GET /api/v1/users dengan auth"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = await client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_users_unauthenticated(self, client):
        """Test endpoint GET /api/v1/users tanpa auth (should fail)"""
        response = await client.get("/api/v1/users")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client, auth_token):
        """Test endpoint GET /api/v1/users/{id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create user first
        create_payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        create_response = await client.post("/api/v1/users", json=create_payload)
        user_id = create_response.json()["id"]
        
        # Get user
        response = await client.get(f"/api/v1/users/{user_id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["id"] == user_id
    
    @pytest.mark.asyncio
    async def test_update_user(self, client, auth_token):
        """Test endpoint PUT /api/v1/users/{id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create user
        create_payload = {
            "username": "oldname",
            "email": "old@example.com",
            "password": "SecurePass123!"
        }
        create_response = await client.post("/api/v1/users", json=create_payload)
        user_id = create_response.json()["id"]
        
        # Update user
        update_payload = {"username": "newname"}
        response = await client.put(
            f"/api/v1/users/{user_id}",
            json=update_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()["username"] == "newname"
    
    @pytest.mark.asyncio
    async def test_delete_user(self, client, auth_token):
        """Test endpoint DELETE /api/v1/users/{id}"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create user
        create_payload = {
            "username": "tobedeleted",
            "email": "delete@example.com",
            "password": "SecurePass123!"
        }
        create_response = await client.post("/api/v1/users", json=create_payload)
        user_id = create_response.json()["id"]
        
        # Delete user
        response = await client.delete(f"/api/v1/users/{user_id}", headers=headers)
        
        assert response.status_code == 204
        
        # Verify deleted
        get_response = await client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert get_response.status_code == 404
```

**Template: tests/conftest.py**
```python
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Override database URL untuk testing
settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop untuk async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create fresh database session untuk setiap test"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    session = session_maker()
    
    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client dengan overridden database dependency"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
```

#### C. Test Coverage Requirements

```yaml
# .coveragerc atau pyproject.toml
[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/main.py",
    "*/core/config.py"
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod"
]
fail_under = 80  # Minimal 80% coverage
show_missing = true
```

#### D. Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_services.py -v

# Run with coverage + fail if < 80%
pytest --cov=app --cov-fail-under=80

# Generate coverage XML untuk SonarQube
pytest --cov=app --cov-report=xml:coverage.xml
```

### 7. SonarQube Integration

#### A. SonarQube Configuration

**sonar-project.properties**
```properties
# Project identification
sonar.projectKey=my-fastapi-app
sonar.projectName=My FastAPI Application
sonar.projectVersion=1.0.0

# Source code location
sonar.sources=app
sonar.tests=tests
sonar.sourceEncoding=UTF-8

# Python specific
sonar.language=py
sonar.python.version=3.12,3.13

# Coverage reports
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml

# Quality gate thresholds
sonar.python.coverage.branchCoverage=true

# Exclusions
sonar.exclusions=**/tests/**,**/__pycache__/**,**/*.pyc,**/alembic/**

# Issue exclusions (false positives)
sonar.issue.ignore.multicriteria=e1
sonar.issue.ignore.multicriteria.e1.ruleKey=python:S107
sonar.issue.ignore.multicriteria.e1.resourceKey=**/endpoints/*.py
```

#### B. CI/CD Pipeline Integration

**GitHub Actions (.github/workflows/sonarqube.yml)**
```yaml
name: SonarQube Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-and-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Shallow clones should be disabled
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov httpx aiosqlite
    
    - name: Run tests with coverage
      run: |
        pytest --cov=app --cov-report=xml:coverage.xml --cov-report=term-missing
    
    - name: Generate test results XML
      run: |
        pytest --junitxml=test-results.xml
    
    - name: SonarQube Scan
      uses: SonarSource/sonarqube-scan-action@v4
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
    
    - name: Quality Gate Check
      uses: SonarSource/sonarqube-quality-gate-action@v1
      id: quality-gate
      timeout-minutes: 5
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    
    - name: Fail on Quality Gate Failure
      if: ${{ steps.quality-gate.outputs.quality-gate-result == 'FAILED' }}
      run: |
        echo "Quality gate failed!"
        exit 1
```

**GitLab CI (.gitlab-ci.yml)**
```yaml
stages:
  - test
  - sonarqube

test:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-asyncio pytest-cov httpx aiosqlite
    - pytest --cov=app --cov-report=xml:coverage.xml
    - pytest --junitxml=test-results.xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
      junit: test-results.xml
  coverage: '/TOTAL.*\s+(\d+%)/'

sonarqube-check:
  stage: sonarqube
  image: 
    name: sonarsource/sonar-scanner-cli:latest
    entrypoint: [""]
  script:
    - sonar-scanner
      -Dsonar.projectKey=$CI_PROJECT_NAME
      -Dsonar.sources=app
      -Dsonar.tests=tests
      -Dsonar.python.coverage.reportPaths=coverage.xml
      -Dsonar.python.xunit.reportPath=test-results.xml
      -Dsonar.host.url=$SONAR_HOST_URL
      -Dsonar.login=$SONAR_TOKEN
  only:
    - main
    - develop
```

#### C. SonarQube Quality Gate Criteria

**Recommended Quality Gate Thresholds:**

| Metric | Threshold | Critical |
|--------|-----------|----------|
| **Coverage** | ≥ 80% | Blocker |
| **Bugs** | 0 | Blocker |
| **Vulnerabilities** | 0 | Critical |
| **Security Hotspots** | Reviewed | Major |
| **Code Smells** | ≤ 5% | Minor |
| **Duplications** | ≤ 3% | Major |
| **Cognitive Complexity** | ≤ 15 per function | Major |
| **Maintainability Rating** | A | Major |
| **Reliability Rating** | A | Critical |
| **Security Rating** | A | Critical |

#### D. SonarQube Rules untuk Python

**sonar-python-rules.md** (Create di root project)
```markdown
# SonarQube Python Rules Configuration

## Critical Rules (Must Pass)
- python:S2004 - Packages should not be imported more than once
- python:S3626 - Jump statements should not be redundant
- python:S5719 - "assert" should not be used in tests
- python:S5659 - JWT tokens should not be vulnerable to algorithm confusion attacks
- python:S5445 - Sensitive information should not be exposed

## Security Rules
- python:S2076 - OS commands should not be vulnerable to injection attacks
- python:S2083 - Regular expressions should not be vulnerable to DoS attacks
- python:S3047 - Function arguments should not be used in their default values
- python:S4721 - Access to OS path functions should be safe
- python:S5042 - SQL queries should not be vulnerable to injection attacks

## Code Quality Rules
- python:S107 - Methods should not have too many parameters (ignore for endpoints)
- python:S138 - Functions should not have too many lines of code
- python:S1523 - Exec should not be used
- python:S1905 - Redundant exceptions should not be caught
- python:S5632 - "jsonschema" should be used for JSON schema validation
```

#### E. Pre-commit Hooks untuk Quality Assurance

**.pre-commit-config.yaml**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --extend-ignore=E203]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-PyYAML
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### 8. Quality Gate Summary

**Setiap development WAJIB melewati quality gates ini:**

```yaml
Quality Gates:
  ✅ Unit Tests: Coverage ≥ 80%
  ✅ Integration Tests: All critical paths covered
  ✅ Security Tests: OWASP Top 10 validation
  ✅ SonarQube:
    - Bugs: 0
    - Vulnerabilities: 0
    - Security Rating: A
    - Coverage: ≥ 80%
    - Duplications: ≤ 3%
  ✅ Pre-commit Hooks: All pass
  ✅ Health Checks: Implemented
  ✅ ISO 27001: Compliance checklist passed
```

### References
- OWASP Top 10 2024: https://owasp.org/www-project-top-ten/
- ISO 27001:2022 Controls: https://www.iso.org/standard/27001
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Pydantic v2 Validation: https://docs.pydantic.dev/latest/
- SonarQube Python: https://docs.sonarqube.org/latest/analysis/languages/python/
- pytest Best Practices: https://docs.pytest.org/en/latest/
- pytest-cov: https://pytest-cov.readthedocs.io/
- Pre-commit Hooks: https://pre-commit.com/