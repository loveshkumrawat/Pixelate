import io
import pytesseract
import globals
from connection.minio_client_connection import minioClient
from minio import S3Error
from PIL import Image


def no_of_objects_in_file(current_file_id: int):
    try:
        objects = minioClient.list_objects(globals.bucket_name, f'{current_file_id}/pages', recursive=True)
        file_count = sum(1 for _ in objects)
    except S3Error as err:
        print(err)
    return file_count


def get_img_from_file(current_file_id: int, page_no: int):
    try:
        img = minioClient.get_object(globals.bucket_name, f"{current_file_id}/pages/page{page_no}/pages{page_no}.png")
    except S3Error as e:
        print(e)
    return img


def clean_text(text: str):
    cleaned_text = ""
    for char in text.split('\n'):
        if char != "":
            cleaned_text += char + "\n"
    return cleaned_text


def text_extract_from_file(file_id: int, file_name: str):
    print("Inside Splitter")
    no_of_images = no_of_objects_in_file(file_id)
    print("no_of_images: " + str(no_of_images))
    for i in range(no_of_images):
        img = get_img_from_file(file_id, i)
        contents = img.read()
        text = pytesseract.image_to_string(Image.open(io.BytesIO(contents)), lang='eng')
        text = clean_text(text)
        text_bytes = bytes(text, 'utf-8')
        minioClient.put_object(globals.bucket_name,
                               f"{file_id}/pages/page{i}/pages{i}.txt",
                               io.BytesIO(text_bytes),
                               len(text_bytes))
        print(f"Page{i}-----Text Extraction Done ")
