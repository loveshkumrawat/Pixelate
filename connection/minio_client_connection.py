from minio import Minio

try:
    minioClient = Minio(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
except Exception as e:
    print(e)
