import io
import pytesseract
from datetime import datetime
from PIL import Image
from pytesseract import Output
from connection.minio_client_connection import minioClient
import globals
from fastapi import HTTPException, status
from metadata_extractor.mongo_db_connection import database
from metadata_extractor.models import MetaDataExtractor
from metadata_extractor.db_connection import session

global pre_word_block, pre_word_para, pre_word_line


def extract_text(file_id: int, file_name: str):
    file = MetaDataExtractor(id=file_id, file_name=file_name, fetch_time=datetime.now())
    session.add(file)
    session.commit()
    data = session.query(MetaDataExtractor).filter(MetaDataExtractor.id == file_id).first()
    objects = get_no_of_pages(file_id)
    page_count = int(sum(1 for _ in objects) / 2)
    path = f'{file_id}/pages'
    for pc in range(0, page_count):
        try:
            response = minioClient.get_object(
                bucket_name=globals.bucket_name,
                object_name=f"{path}/page{pc}/pages{pc}.jpg"
            )
            img = Image.open(io.BytesIO(response.data))
            d = pytesseract.image_to_data(img, output_type=Output.DICT)
            n_boxes = len(d['level'])
            ans_dict = {}
            block_list = []
            para_list = []
            word_list = []
            line_list = []
            ans_dict.update({'page_no': pc})
            ans_dict.update({'blocks': block_list})
            set_global_var(d, n_boxes)
            global pre_word_block, pre_word_para, pre_word_line
            i = 0
            for i in range(n_boxes):
                my_file = {}
                if d['text'][i] == ' ' or d['text'][i] == '':
                    continue

                if d['block_num'][i] != pre_word_block:
                    check_block_change(i, d, word_list, para_list, block_list, line_list)

                elif d['block_num'][i] == pre_word_block and d['par_num'][i] != pre_word_para:
                    check_para_change(i, d, para_list, word_list, line_list)

                elif d['line_num'][i] != pre_word_line:
                    check_line_change(i, d, line_list, word_list)

                (x, y, w, h, text, para_num, block_num) = (
                    d['left'][i], d['top'][i], d['width'][i], d['height'][i], d['text'][i], d['par_num'][i],
                    d['block_num'][i])
                my_file.update(({'word_no': i}))
                my_file.update({"word": text})
                my_file.update({"top": y})
                my_file.update({"left": x})
                my_file.update({"bottom": y + h})
                my_file.update({"right": x + w})

                pre_word_block = d['block_num'][i]
                pre_word_para = d['par_num'][i]
                pre_word_line = d['line_num'][i]
                word_list.append(my_file)

            if len(ans_dict) == 0:
                check_block_change(i, d, word_list, para_list, block_list)

            elif len(ans_dict['blocks']) != 0 and ans_dict['blocks'][len(ans_dict['blocks']) - 1][
                'block_no'] != pre_word_block:
                check_block_change(i, d, word_list, para_list, block_list, line_list)

            elif len(ans_dict['blocks']) != 0 and ans_dict['blocks'][len(ans_dict['blocks']) - 1]['paragraphs'][
                len(ans_dict['blocks'][len(ans_dict['blocks']) - 1]['paragraphs']) - 1]['para_no']:
                check_para_change(i, d, para_list, word_list, line_list)
            print(ans_dict)
            collection = database[f'{file_id}']
            collection.insert_one(ans_dict)

            data.status = 'successful'
            data.submission_time = datetime.now()
            data.error = 'NULL'
            session.commit()

        except Exception as e:

            data.status = 'unsuccessful'
            data.error = f'{e}'
            session.commit()
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f'{e}')


def check_line_change(i, d, line_list, word_list):
    global pre_word_line

    line_dict = {}
    l_first_word_y = word_list[0]['top']
    l_first_word_x = word_list[0]['left']
    l_last_word_x = word_list[len(word_list) - 1]['right']
    l_last_word_y = word_list[len(word_list) - 1]['bottom']

    line_dict.update({"line_no": pre_word_line})
    temp_word_list = list(word_list)
    line_dict.update({"words": temp_word_list})
    word_list.clear()

    line_dict.update({"categories": ['line']})
    line_dict.update({"top": l_first_word_y})
    line_dict.update({"left": l_first_word_x})
    line_dict.update({"bottom": l_last_word_y})
    line_dict.update({"right": l_last_word_x})

    line_list.append(line_dict)

    if i != len(d['level']):
        pre_word_line = d['line_num'][i]


def set_global_var(d, n_boxes):
    for i in range(n_boxes):
        if d['text'][i] == ' ' or d['text'][i] == '':
            continue
        global pre_word_block, pre_word_para, pre_word_line
        pre_word_block = d['block_num'][i]
        pre_word_para = d['par_num'][i]
        pre_word_line = d['line_num'][i]
        break


def check_block_change(i, d, word_list, para_list, block_list, line_list):
    global pre_word_block

    block_dict = {}

    check_para_change(i, d, para_list, word_list, line_list)

    b_first_word_x = para_list[0]['lines'][0]["words"][0]['left']
    b_first_word_y = para_list[0]['lines'][0]["words"][0]['top']
    b_last_word_x = para_list[len(para_list)-1]['lines'][len(para_list[len(para_list)-1]['lines'])-1]['words'][len(para_list[len(para_list)-1]['lines'][len(para_list[len(para_list)-1]['lines'])-1]['words'])-1]['right']
    b_last_word_y = para_list[len(para_list)-1]['lines'][len(para_list[len(para_list)-1]['lines'])-1]['words'][len(para_list[len(para_list)-1]['lines'][len(para_list[len(para_list)-1]['lines'])-1]['words'])-1]['bottom']

    block_dict.update({'block_no': pre_word_block})
    temp_para_list = list(para_list)
    block_dict.update({"paragraphs": temp_para_list})

    block_dict.update({"categories": ['block']})
    block_dict.update({"top": b_first_word_y})
    block_dict.update({"left": b_first_word_x})
    block_dict.update({"bottom": b_last_word_y})
    block_dict.update({"right": b_last_word_x})

    block_list.append(block_dict)
    para_list.clear()

    if i != len(d['level']):
        pre_word_block = d['block_num'][i]


def check_para_change(i, d, para_list, word_list, line_list):
    global pre_word_para
    para_dict = {}

    check_line_change(i, d, line_list, word_list)

    p_first_word_x = line_list[0]['words'][0]['left']
    p_first_word_y = line_list[0]['words'][0]['top']
    p_last_word_x = line_list[len(line_list) - 1]['words'][len(line_list[len(line_list) - 1]['words']) - 1]['right']
    p_last_word_y = line_list[len(line_list) - 1]['words'][len(line_list[len(line_list) - 1]['words']) - 1]['bottom']

    para_dict.update({"para_no": pre_word_para})
    temp_line_list = list(line_list)
    para_dict.update({"lines": temp_line_list})

    para_dict.update({"categories": ['para']})
    para_dict.update({"top": p_first_word_y})
    para_dict.update({"left": p_first_word_x})
    para_dict.update({"bottom": p_last_word_y})
    para_dict.update({"right": p_last_word_x})

    para_list.append(para_dict)
    line_list.clear()

    if i != len(d['level']):
        pre_word_para = d['par_num'][i]


def get_no_of_pages(file_id):
    path = f'{file_id}/pages'
    objects = minioClient.list_objects(
        bucket_name=globals.bucket_name,
        prefix=path,
        recursive=True
    )
    return objects


