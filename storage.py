import os
from dotenv import load_dotenv
from minio import Minio

load_dotenv()
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
MINIO_ROOT_USER = os.getenv('MINIO_ROOT_USER')
MINIO_ROOT_PASSWORD = os.getenv('MINIO_ROOT_PASSWORD')
MINIO_BUCKET = os.getenv('MINIO_BUCKET')

minio_client = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)