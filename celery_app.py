import os
from dotenv import load_dotenv
from celery import Celery
from urllib.parse import quote

load_dotenv()
RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

encoded_user = quote(RABBITMQ_DEFAULT_USER, safe="")
encoded_password = quote(RABBITMQ_DEFAULT_PASS, safe="")
BROKER_URL = f"amqp://{encoded_user}:{encoded_password}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"

celery_app = Celery(
    'doc_analyser',
    broker=BROKER_URL,
    include=["tasks"],
)
celery_app.conf.worker_enable_remote_control = False
