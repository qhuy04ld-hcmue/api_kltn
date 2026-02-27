from minio import Minio
from app.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
    BUCKETS
)

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


# Tự động tạo bucket nếu chưa tồn tại
def ensure_buckets():
    existing = [b.name for b in client.list_buckets()]

    for bucket in BUCKETS:
        if bucket not in existing:
            client.make_bucket(bucket)


# Gọi khi import file này
ensure_buckets()
