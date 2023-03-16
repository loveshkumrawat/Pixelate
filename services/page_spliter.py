# pip install PyMuPDF Pillow
import io
from datetime import datetime
from models import File
import fitz
from minio import S3Error
import globals
from connection.minio_client_connection import minioClient
from connection.postgres_database_connection import session
from logs.logs import logger

def convert_to_image(file_id, file_name):
    try:
        get_file_from_minio(file_id, file_name)
        doc = fitz.open(f'./files/{file_name}')
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Identity, dpi=None, colorspace=fitz.csRGB, clip=None, alpha=True,
                                  annots=True)
            page_name = f"pages{page.number}.jpg"
            img_bytes = pix.tobytes()
            minioClient.put_object(bucket_name=globals.bucket_name, object_name=f"{file_id}/pages/page{page.number}/{page_name}",
                                   data=io.BytesIO(img_bytes), length=len(img_bytes), content_type="img/png")

    except:
        logger.error('error in converting to image')


def get_file_from_minio(file_id, file_name):
    try:
        minioClient.fget_object(globals.bucket_name, f"{file_id}/files/{file_name}", f"./files/{file_name}")
        logger.info(f"Successfully downloaded  from {globals.bucket_name}'.")
        try:
            file = session.query(File).filter(File.id == file_id).first()
            file.submitted_time = datetime.now()
            session.commit()
        except:
            logger.error('submitted time not updated ')

    except S3Error as e:
        logger.error("Error: {}".format(e))



