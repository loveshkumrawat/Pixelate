import io
import os

import cv2
import pytesseract
from minio import S3Error
import globals
from connection.minio_client_connection import minioClient


def text_extract_from_file(file_id: int, file_name: str):
    no_of_images = no_of_objects_in_file(file_id)
    for i in range(no_of_images):
        img = get_img_from_file(file_name, file_id, i)
        config = '-l eng --oem 1 --psm 3'
        text = pytesseract.image_to_string(img, config=config)
        text_bytes = bytes(text, 'utf-8')
        minioClient.put_object(globals.bucket_name,
                               f"{file_id}/pages/page{i}/page{i}.txt",
                               io.BytesIO(text_bytes),
                               len(text_bytes))
        print(f"Page{i}-----Text Extraction Done ")


def get_img_from_file(current_file_name: str, current_file_id: int, page_no: str):
    current_file_name = current_file_name.replace(".pdf", "")
    try:
        print(f"{current_file_id}/pages/page{page_no}/page{page_no}.jpg")
        img = minioClient.get_object(bucket_name=globals.bucket_name,
                                     object_name=f"{current_file_id}/pages/page{page_no}/pages{page_no}.jpg")
        contents = img.read()
        with open(f"{os.getcwd()}/files/{current_file_name}_page_{page_no}.jpg", "wb") as f:
            f.write(contents)
    except S3Error as e:
        print(e)
    return cv2.imread(f"{os.getcwd()}/files/{current_file_name}_page_{page_no}.jpg")


def no_of_objects_in_file(current_file_id: int):
    try:
        objects = minioClient.list_objects(globals.bucket_name, f'{current_file_id}/pages', recursive=True)
        file_count = sum(1 for _ in objects)
    except S3Error as err:
        print(err)
    return file_count
