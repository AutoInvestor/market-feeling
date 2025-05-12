# stock_api/config.py

import os
import toml
from typing import Optional
from pydantic import BaseSettings, Field, SecretStr


def load_toml_config(config_file: str = "config.toml") -> dict:
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(base, "..")
    path = os.path.join(root, config_file)
    return toml.load(path) if os.path.exists(path) else {}


_toml = load_toml_config()


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(
        _toml.get("app", {}).get("environment", "production"),
        env="ENVIRONMENT",
    )

    HOST: str = Field(
        _toml.get("server", {}).get("host", "0.0.0.0"),
        env="HOST",
    )
    PORT: int = Field(
        _toml.get("server", {}).get("port", 8000),
        env="PORT",
    )

    # MongoDB Atlas (secret—only required in production)
    MONGODB_URI: Optional[SecretStr] = Field(
        _toml.get("app", {}).get("mongodb_uri", None),
        env="MONGODB_URI",
    )
    MONGODB_DB: str = Field(
        _toml.get("app", {}).get("mongodb_db", "market_feeling"),
        env="MONGODB_DB",
    )

    # Google Pub/Sub
    GCP_PROJECT: str = Field(
        _toml.get("app", {}).get("gcp_project", ""),
        env="GCP_PROJECT",
    )
    PUBSUB_TOPIC: str = Field(
        _toml.get("app", {}).get("pubsub_topic", ""),
        env="PUBSUB_TOPIC",
    )
    PUBSUB_SUBSCRIPTION_CORE: str = Field(
        _toml.get("app", {}).get("pubsub_subscription", ""),
        env="PUBSUB_SUBSCRIPTION_CORE",
    )

    class Config:
        # load a .env file for local testing
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
