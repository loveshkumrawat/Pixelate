import io
from datetime import datetime
from minio import S3Error
from sqlalchemy import func
from file_upload.db_connection import session
from models import File
import globals
from connection.minio_client_connection import minioClient
from supporting_files.logs import logger
from fastapi import HTTPException,status


def upload_file_to_minio(data, filename):
    found = minioClient.bucket_exists(globals.bucket_name)
    if not found:
        minioClient.make_bucket(globals.bucket_name)
    try:
        file_id = add_file_to_database(filename)
        minioClient.put_object(bucket_name=globals.bucket_name, object_name=f"{file_id}/files/{filename}",
                               data=io.BytesIO(data), length=len(data), content_type="pdf")
        logger.info(f"Successfully uploaded to {globals.bucket_name}")
        return file_id
    except S3Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='error in uplaoding file to minio')
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