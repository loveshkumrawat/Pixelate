import datetime
import pytesseract
from io import BytesIO
from PIL import Image
from minio import S3Error
from supporting.logs import logger
from fastapi import HTTPException, status
from supporting.helper import bucket_name
from text_extractor.db_connection import session
from text_extractor.models import TextExtractor
from connection.minio_client_connection import minioClient


def clean_text(text: str):
    
    cleaned_text = ""
    for char in text.split('\n'):
        if char != "":
            cleaned_text += char + "\n"
    return cleaned_text


def text_extract_from_file(file_id: int, file_name: str):
    
    # add file details to database
    try:
        db_entry = TextExtractor(id=file_id, file_name=file_name, fetch_time=datetime.datetime.now())
        session.add(db_entry)
        session.commit()

        logger.debug(f"File details added to 'Text Extractor' database")
    
    except Exception as e:
        
        logger.error("error in adding file details to 'Text Extractor' database", exc_info=e)
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="error in adding file details to 'Text Extractor' database")
    
    # get list of files from minio
    objects = minioClient.list_objects(bucket_name, f'{file_id}/pages', recursive=True)
    
    img_count = 0
    for object in objects:

        if not object.object_name.endswith('.jpg'): continue
        
        # get image from minio
        try:
            img = minioClient.get_object(bucket_name, object.object_name)
            logger.debug(f"Image '{object.object_name}' fetched from minio")
        
        except S3Error as e:
            
            logger.error("error while getting image from minio", exc_info=e)
            db_entry.status = 'unsuccessful'
            db_entry.error = e
            session.commit()
            
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="error while getting image from minio")
        
        # text extraction from image
        text = pytesseract.image_to_string(Image.open(BytesIO(img.read())), lang='eng')
        logger.info(f"Text extracted from image '{object.object_name}'")

        # Text Cleaning
        text = clean_text(text)
        text_bytes = bytes(text, 'utf-8')
        
        # upload text file to minio
        try:
            minioClient.put_object(
                bucket_name=bucket_name,
                object_name=f"{file_id}/pages/page{img_count}/pages{img_count}.txt",
                data=BytesIO(text_bytes),
                length=len(text_bytes)
            )

            img_count += 1
            logger.debug(f"Text uploaded to minio for image '{object.object_name}'")
        
        except S3Error as e:
            logger.error("error while uploading text to minio", exc_info=e)
            db_entry.status = 'unsuccessful'
            db_entry.error = e
            session.commit()
            
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="error while uploading text to minio")
    
    # Update database on successful completion
    db_entry.submission_time = datetime.datetime.now()
    db_entry.status = 'successful'
    session.commit()
    
    logger.info(f'Text extracted from file with {file_id} file id')
