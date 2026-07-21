import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        return cls(
            host=_required_env("DB_HOST"),
            port=int(_required_env("DB_PORT")),
            name=_required_env("DB_NAME"),
            user=_required_env("DB_USER"),
            password=_required_env("DB_PASSWORD"),
        )


@dataclass(frozen=True)
class MinioSettings:
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str

    @classmethod
    def from_env(cls) -> "MinioSettings":
        return cls(
            endpoint=_required_env("MINIO_ENDPOINT"),
            access_key=_required_env("MINIO_ROOT_USER"),
            secret_key=_required_env("MINIO_ROOT_PASSWORD"),
            bucket=_required_env("MINIO_BUCKET"),
        )


@dataclass(frozen=True)
class RabbitMQSettings:
    host: str
    port: int
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "RabbitMQSettings":
        return cls(
            host=_required_env("RABBITMQ_HOST"),
            port=int(_required_env("RABBITMQ_PORT")),
            user=_required_env("RABBITMQ_DEFAULT_USER"),
            password=_required_env("RABBITMQ_DEFAULT_PASS"),
        )
