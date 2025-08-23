"""
Configuration management for Web Scraper Service
"""
import os
from dataclasses import dataclass
from typing import Optional
from pydantic_settings import BaseSettings  # Changed this line!
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database Configuration
    database_host: str = Field(default="postgres", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(default="warhammer_meta", env="DATABASE_NAME")
    database_user: str = Field(default="warhammer_user", env="DATABASE_USER")
    database_password: str = Field(default="warhammer_secret_2024", env="DATABASE_PASSWORD")

    # Redis Configuration
    redis_host: str = Field(default="redis", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # Scraper Configuration
    scraper_env: str = Field(default="development", env="SCRAPER_ENV")
    log_level: str = Field(default="INFO", env="SCRAPER_LOG_LEVEL")
    wahapedia_base_url: str = Field(default="https://wahapedia.ru", env="WAHAPEDIA_BASE_URL")
    rate_limit_delay: float = Field(default=2.0, env="RATE_LIMIT_DELAY")

    # Application paths
    log_dir: str = Field(default="/app/logs", env="LOG_DIR")
    data_dir: str = Field(default="/app/data", env="DATA_DIR")
    # services/web-scraper/src/config.py (updated fields)
class Settings(BaseSettings):

    # Game Version Configuration (simplified)
    game_version_id: str = Field(
        default="10th",
        env="GAME_VERSION_ID",
        description="Game version identifier (e.g., 10th, 9th)"
    )
    game_version_name: str = Field(
        default="10th Edition",
        env="GAME_VERSION_NAME",
        description="Human-readable version name"
    )
    scraper_service: str = Field(
        default="wahapedia",
        env="SCRAPER_SERVICE",
        description="Which scraper service to use"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return (
                f"postgresql://{self.database_user}:{self.database_password}"
                f"@{self.database_host}:{self.database_port}/{self.database_name}"
                )

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.scraper_env.lower() in ("development", "dev", "local")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.scraper_env.lower() in ("production", "prod")


# Create global settings instance
settings = Settings()


# Service identification
SERVICE_NAME = "web-scraper"
SERVICE_VERSION = "0.1.0"
USER_AGENT = f"WH40K-Meta-Analyzer/{SERVICE_VERSION} (Web Scraper Bot)"

# Redis Channel Names
class RedisChannels:
    """Redis pub/sub channel definitions"""
    FACTION_DISCOVERED = "scraper:faction:discovered"
    UNIT_EXTRACTED = "scraper:unit:extracted"
    ENHANCEMENT_FOUND = "scraper:enhancement:found"
    WARGEAR_FOUND = "scraper:wargear:found"
    SCRAPING_STARTED = "scraper:status:started"
    SCRAPING_COMPLETED = "scraper:status:completed"
    SCRAPING_FAILED = "scraper:status:failed"
    VERSION_CHANGE_DETECTED = "scraper:version:change"

# Message Types
class MessageTypes:
    """Message type identifiers for Redis pub/sub"""
    FACTION_DISCOVERED = "faction_discovered"
    UNIT_EXTRACTED = "unit_extracted"
    ENHANCEMENT_FOUND = "enhancement_found"
    WARGEAR_FOUND = "wargear_found"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    VERSION_CHANGE = "version_change"

# Add these fields to Settings class if they are missing
# (This is a patch - you should properly add these to the Settings class)
if not hasattr(settings, "database_user"):
    settings.database_user = "warhammer_user"
if not hasattr(settings, "database_password"):
    settings.database_password = "warhammer_secret_2024"
if not hasattr(settings, "database_host"):
    settings.database_host = "postgres"
if not hasattr(settings, "database_port"):
    settings.database_port = 5432
if not hasattr(settings, "database_name"):
    settings.database_name = "warhammer_meta"
