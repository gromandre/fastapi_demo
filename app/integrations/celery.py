from urllib.parse import quote

from celery import Celery

from app.core.config import RabbitMQSettings

settings = RabbitMQSettings.from_env()
encoded_user = quote(settings.user, safe="")
encoded_password = quote(settings.password, safe="")
BROKER_URL = (
    f"amqp://{encoded_user}:{encoded_password}@{settings.host}:{settings.port}//"
)

celery_app = Celery(
    "doc_analyser",
    broker=BROKER_URL,
    include=["worker.tasks"],
)
celery_app.conf.worker_enable_remote_control = False
