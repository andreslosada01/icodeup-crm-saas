from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


V2_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "Icodeup 360"
    app_host: str = "127.0.0.1"
    app_port: int = 8020
    frontend_dir: str = str(V2_ROOT / "frontend" / "static")
    secret_key: str = ""
    session_cookie_name: str = "icodeup_session"
    session_hours: int = 12
    database_url: str = ""
    tenant_mode: str = "shared_schema"
    platform_tenant_slug: str = "icodeup-platform"
    enable_demo_seeds: bool = False
    enable_demo_data: bool = False
    platform_admin_email: str = ""
    platform_admin_password: str = ""

    model_config = SettingsConfigDict(env_file=V2_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def is_configured(self) -> bool:
        return bool(self.secret_key and self.database_url)


settings = Settings()
