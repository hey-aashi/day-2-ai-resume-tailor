from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="AI Resume Tailor")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    app_debug: bool = Field(default=True)
    upload_dir: str = Field(default="uploads")
    output_dir: str = Field(default="outputs")
    max_upload_size_mb: int = Field(default=10)
    allowed_extensions: str = Field(default=".pdf")
    rate_limit_enabled: bool = Field(default=False)
    rate_limit_requests_per_minute: int = Field(default=60)
    google_api_key: str | None = Field(default=None)

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
UPLOAD_PATH = Path(settings.upload_dir)
OUTPUT_PATH = Path(settings.output_dir)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
