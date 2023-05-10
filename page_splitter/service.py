import io
from datetime import datetime
from fastapi import HTTPException, status
import fitz
from minio import S3Error
from supporting.helper import bucket_name
from connection.minio_client_connection import minioClient
from file_upload.db_connection import session
from supporting.logs import logger
from page_splitter.db_connection import session
from page_splitter.models import PageSplitter


def convert_to_image(file_id: int, file_name: str):

    response = get_file_from_minio(file_id, file_name)
    data_entry = add_file_details_to_db(file_id, file_name)
    
    doc = fitz.open(stream=response.data, filetype="pdf")
    
    for page_no, page in enumerate(doc):
        
        try:
            pix = page.get_pixmap(
                matrix=fitz.Identity,
                dpi=None,
                colorspace=fitz.csRGB,
                clip=None,
                alpha=False,
                annots=True
            )
            
            logger.debug(f"Page '{page_no}' converted to image")
        
        except Exception as e:
            data_entry.status = 'unsuccessful'
            data_entry.error = e
            session.commit()

            logger.error("error while pdf to image conversion", exc_info=e)
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="error while pdf to image conversion")
        
        try:
            page_name = f"pages{page.number}.jpg"
            img_bytes = pix.tobytes()

            minioClient.put_object(
                bucket_name=bucket_name,
                object_name=f"{file_id}/pages/page{page.number}/{page_name}",
                data=io.BytesIO(img_bytes),
                length=len(img_bytes),
                content_type="img/png"
            )

            logger.debug(f"Page '{page_no}' uploaded to minio")

        except Exception as e:
            data_entry.status = 'unsuccessful'
            data_entry.error = e
            session.commit()

            logger.error("error while image uploading", exc_info=e)
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="error while image uploading")

    data_entry.submission_time = datetime.now()
    data_entry.status = 'successful'
    session.commit()
    
    logger.info(f'File converted to images with {file_id} file id')


def get_file_from_minio(file_id: int, file_name: str):
    
    try:
        response = minioClient.get_object(
            bucket_name=bucket_name,
            object_name=f"{file_id}/files/{file_name}"
        )

        logger.debug(f"File data fetched with {file_id} file id")
        return response
    
    except S3Error as e:
        
        logger.error("error in fetching file data from minio", exc_info=e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="error in fetching file data from minio")


def add_file_details_to_db(file_id: int, file_name: str):

    try:
        file = PageSplitter(id=file_id, file_name=file_name, fetch_time=datetime.now())
        session.add(file)
        session.commit()

        logger.debug(f"File details added to 'Page Splitter' database")
        return file

    except S3Error as e:
        
        logger.error("error in adding file details to 'Page Splitter' database", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="error in adding file details to 'Page Splitter' database"
        )
