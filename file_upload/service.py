import io
from datetime import datetime
from minio import S3Error
from sqlalchemy import func
from file_upload.db_connection import session
from file_upload.models import File
from supporting.helper import bucket_name
from connection.minio_client_connection import minioClient
from supporting.logs import logger
from fastapi import HTTPException, status


def upload_file_to_minio(data, filename:str):

    # check if file is empty or not
    if not data:
        logger.warn("Uploaded File is Empty")
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Uploaded File is Empty")

    # Create bucket if it doesn't exist
    bucket = minioClient.bucket_exists(bucket_name)
    if not bucket: minioClient.make_bucket(bucket_name)
    
    file_id:int = add_file_to_database(filename)

    try:
        
        minioClient.put_object(
            bucket_name=bucket_name,
            object_name=f"{file_id}/files/{filename}",
            data=io.BytesIO(data),
            length=len(data),
            content_type="pdf"
        )
        
        logger.info(f'File uploaded with {file_id} file id')
        return file_id
    
    except S3Error as e:
        
        logger.error("error in uplaoding file to minio", exc_info=e)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="error in uplaoding file to minio")



def add_file_to_database(file_name:str):
    
    file_id = (session.query(func.max(File.id)).scalar() or 0) + 1

    try:
        file = File(
            id=file_id,
            file_name=file_name,
            file_path=f"{file_id}/files/{file_name}",
            uploaded_time=datetime.now()
        )
        
        session.add(file)
        session.commit()

        logger.debug(f"File details added to 'File Upload' database")
        return file_id
    
    except Exception as e:
        
        logger.error("error in adding file details to 'File Upload' database", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="error in adding file details to 'File Upload' database"
        )