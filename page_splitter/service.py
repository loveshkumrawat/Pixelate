import io
from datetime import datetime
from fastapi import HTTPException, status
import fitz
from minio import S3Error
import globals
from connection.minio_client_connection import minioClient
from file_upload.db_connection import session
from supporting_files.logs import logger
from page_splitter.db_connection import session
from models import PageSplitter


def convert_to_image(file_id, file_name):
    fileObject = session.query(PageSplitter).filter(id == file_id)
    try:
        get_file_from_minio(file_id, file_name)
        doc = fitz.open(f'./files/{file_name}')
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Identity, dpi=None, colorspace=fitz.csRGB, clip=None, alpha=True,
                                  annots=True)
            page_name = f"pages{page.number}.jpg"
            img_bytes = pix.tobytes()
            minioClient.put_object(bucket_name=globals.bucket_name,
                                   object_name=f"{file_id}/pages/page{page.number}/{page_name}",
                                   data=io.BytesIO(img_bytes), length=len(img_bytes), content_type="img/png")

        fileObject.submission_time = datetime.now()
        fileObject.status = 'successful'
        session.commit()
    except Exception as e:

        logger.error('error in converting to image')
        fileObject.status = 'not successful'
        fileObject.error = f'{e}'
        session.commit()


def get_file_from_minio(file_id, file_name):
    try:
        minioClient.fget_object(globals.bucket_name, f"{file_id}/files/{file_name}", f"./files/{file_name}")
        logger.info(f"Successfully downloaded  from {globals.bucket_name}'.")
        file = PageSplitter(id=file_id, file_name=file_name, fetch_time=datetime.now())
        session.add(file)
        session.commit()

    except S3Error as e:
        logger.error("Error: {}".format(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='error in fetching file from minio')
