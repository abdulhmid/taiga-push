from app.core.config import get_settings


def test_database_url_is_configured():
    settings = get_settings()
    assert settings.database_url, "DATABASE_URL should be configured"
    assert settings.database_url.startswith("sqlite+") or settings.database_url.startswith("postgresql+")
