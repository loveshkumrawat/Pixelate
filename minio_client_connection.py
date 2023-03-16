from minio import Minio

minioClient = Minio(endpoint="localhost:9000",
                    access_key="minioadmin",
                    secret_key="minioadmin",
                    secure=False)
