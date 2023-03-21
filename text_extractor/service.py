import datetime
import globals
import pytesseract
from io import BytesIO
from PIL import Image
from minio import S3Error

from connection.minio_client_connection import minioClient
from text_extractor.db_connection import session
from text_extractor.models import TextExtractor


def no_of_objects_in_file(file_id: int, file_name: str):
    try:
        db_entry = TextExtractor(id=file_id, file_name=file_name, fetch_time=datetime.datetime.now())
        session.add(db_entry)
        session.commit()
        objects = minioClient.list_objects(globals.bucket_name, f'{file_id}/pages', recursive=True)
        file_count = sum(1 for _ in objects)
        return file_count
    except S3Error as err:
        print(err)
        session.query(TextExtractor).filter(TextExtractor.id == file_id).update(
            {TextExtractor.error: err})
        session.commit()


def get_img_from_file(file_id: int, page_no: int):
    try:
        img = minioClient.get_object(globals.bucket_name, f"{file_id}/pages/page{page_no}/pages{page_no}.jpg")
        return img
    except S3Error as e:
        print(e)
        session.query(TextExtractor).filter(TextExtractor.id == file_id).update(
            {TextExtractor.error: e})
        session.commit()


def clean_text(text: str):
    cleaned_text = ""
    for char in text.split('\n'):
        if char != "":
            cleaned_text += char + "\n"
    return cleaned_text


def text_extract_from_file(file_id: int, file_name: str):
    try:
        no_of_images = no_of_objects_in_file(file_id, file_name)
        for i in range(no_of_images):
            img = get_img_from_file(file_id, i)
            contents = img.read()
            text = pytesseract.image_to_string(Image.open(BytesIO(contents)), lang='eng')
            text = clean_text(text)
            text_bytes = bytes(text, 'utf-8')
            minioClient.put_object(globals.bucket_name,
                                   f"{file_id}/pages/page{i}/pages{i}.txt",
                                   BytesIO(text_bytes),
                                   len(text_bytes))
            print(f"Page{i}-----Text Extraction Done ")
        session.query(TextExtractor).filter(TextExtractor.id == file_id).update(
            {TextExtractor.status: "Successful",
             TextExtractor.submission_time: datetime.datetime.now()}
        )
        session.commit()
    except Exception as e:
        print(e)
        session.query(TextExtractor).filter(TextExtractor.id == file_id).update(
            {TextExtractor.error: e})
        session.commit()