from os import environ

LOG_LEVEL = environ.get("LOG_LEVEL", "INFO")

DB_HOST = environ.get("DB_HOST", "localhost")
DB_PORT = environ.get("DB_PORT", "5432")
DB_USER = environ.get("DB_USER", "postgres")
DB_PASSWORD = environ.get("DB_PASSWORD", "postgres")

MINIO_HOST = environ.get("MINIO_HOST", "localhost")
MINIO_PORT = environ.get("MINIO_PORT", "9000")
MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY", "minioadmin")

MONGO_DB_HOST = environ.get("MONGO_DB_HOST", "localhost")
MONGO_DB_PORT = environ.get("MONGO_DB_PORT", "5000")

KAFKA_HOST = environ.get("KAFKA_HOST", "localhost")
KAFKA_PORT = environ.get("KAFKA_PORT", "29092")