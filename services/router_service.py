import os
from datetime import datetime
from minio import S3Error
from sqlalchemy import func
from Connection.postgres_database_connection import session
from models import File
import globals
from Connection.minio_client_connection import minioClient
from logs.logs import logger


def upload_file_to_minio(data, filename):
    with open(f"{os.getcwd()}/files/{filename}", "wb") as f:
        f.write(data)
    found = minioClient.bucket_exists(globals.bucket_name)
    if not found:
        minioClient.make_bucket(globals.bucket_name)
    try:
        file_id = add_file_to_database(filename)
        minioClient.fput_object(globals.bucket_name, f"{file_id}/files/{filename}", file_path=f"./files/{filename}")
        logger.info(f"Successfully uploaded to {globals.bucket_name}")

    except S3Error as e:
        logger.error("Error: {}".format(e))


def add_file_to_database(file_name):
    try:
        file_id = session.query(func.max(File.id)).scalar()
        if not file_id:
            file_id = 0
        file = File(id=file_id + 1, file_name=file_name, file_path=f"{file_id + 1}/files/{file_name}",
                    uploaded_time=datetime.now())
        session.add(file)
        session.commit()
        logger.info('file added in database')
        return file_id + 1
    except:
        logger.error('error in adding file data to database')

