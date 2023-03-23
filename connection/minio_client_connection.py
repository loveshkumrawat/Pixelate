from minio import Minio
from supporting import env

try:
    minioClient = Minio(
        endpoint=f"{env.MINIO_HOST}:{env.MINIO_PORT}",
        access_key=env.MINIO_ACCESS_KEY,
        secret_key=env.MINIO_SECRET_KEY,
        secure=False
    )
except Exception as e:
    print(e)
