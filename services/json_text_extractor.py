import cv2
import pytesseract
from pytesseract import Output
from connection.minio_client_connection import minioClient
import globals
from connection.mongo_db_connection import collection


def extract_text(id):
    path = f'{id}/pages'
    objects = minioClient.list_objects(
        bucket_name=globals.bucket_name,
        prefix=path,
        recursive=True
    )

    file_count = sum(1 for _ in objects)
    for fc in range(0, file_count):
        my_dict = {}
        my_dict.update({'pageNo': fc})
        my_data = []
        minioClient.fget_object(bucket_name=globals.bucket_name, object_name=f"{path}/page{fc}/pages{fc}.jpg",
                                file_path=f'files/pages{fc}.jpg')
        img = cv2.imread(f'./files/pages{fc}.jpg')
        d = pytesseract.image_to_data(img, output_type=Output.DICT)
        n_boxes = len(d['level'])

        for i in range(n_boxes):

            my_file = {}
            if d['text'][i] == ' ' or d['text'][i] == '':
                continue
            (x, y, w, h, text, para_num, block_num) = (
                d['left'][i], d['top'][i], d['width'][i], d['height'][i], d['text'][i], d['par_num'][i],
                d['block_num'][i])
            my_file.update({"word": text})
            my_file.update({"top": y})
            my_file.update({"left": x})
            my_file.update({"bottom": x+w})
            my_file.update({"right": y+h})
            my_file.update({'blockNum': block_num})
            my_file.update({'paraNum': para_num})
            my_data.append(my_file)
        my_dict.update({'words': my_data})
        # collection.insert_one(my_dict)
        #print(my_dict)






