
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    redis_url: str = "redis://video-platform-redis:6379/0"

    rabbitmq_url: str = (
        "amqp://video_platform:VideoPlatform_2026"
        "@observability-rabbitmq:5672/"
    )

    upload_dir: str = "/app/storage/uploads"
    output_dir: str = "/app/storage/outputs"
    thumbnail_dir: str = "/app/storage/thumbnails"

    max_upload_mb: int = 500
    allowed_extensions: str = "mp4,mov,mkv,webm,avi"

    api_gateway_port: int = 8000

    upload_service_url: str = "http://upload-service:8001"
    metadata_service_url: str = "http://metadata-service:8002"
    orchestrator_url: str = "http://orchestrator-service:8003"
    delivery_service_url: str = "http://media-delivery:8006"

    class Config:
        env_file = ".env"


settings = Settings()
