# # Require to wait for the services to start
# from time import sleep
# sleep(5)

import json
import pymongo
import uvicorn
from supporting.logs import logger
from fastapi import FastAPI, UploadFile
from connection.kafka_broker import producer
from file_upload.service import upload_file_to_minio
from page_splitter.service import convert_to_image
from text_extractor.service import text_extract_from_file
from metadata_extractor.service import extract_metadata
from metadata_extractor.mongo_db_connection import database

app = FastAPI()

@app.post("/process-file")
def process_file(file: UploadFile):
    
    file_id: int = upload_file_to_minio(file.file.read(), file.filename)
    
    # Dependency Injections
    producer.produce(
        topic='page_splitter_T',
        partition=1,
        value=json.dumps({
            'file_id': file_id,
            'file_name': file.filename
        })
    )
    
    producer.flush()
    
    return {"message": f"File Processing: {file.filename}"}

@app.post("/extractor")
def add_file(file: UploadFile):

    # Upload File Service
    file_id: int = upload_file_to_minio(file.file.read(), file.filename)

    # Page Splitter Service
    convert_to_image(file_id, file.filename)

    # Text Extractor Service
    text_extract_from_file(file_id, file.filename)

    # Metadata Extractor Service
    extract_metadata(file_id, file.filename)

    # Successful completion of all the services
    logger.info(f"Extraction Done for file_id: {file_id}")
    return {"message": "Extraction Done", "file_id": file_id}

@app.get("/getData")
def get_meta_data(file_id: int, page_no: int):
    try:
        database.validate_collection(f'{file_id}')
    except pymongo.errors.OperationFailure:
        return {'message': 'collection does not exist'}

    collection = database[f'{file_id}']
    data = collection.find_one({'page_no': page_no}, {'_id': 0})
    return data


if __name__ == '__main__': uvicorn.run("router:app", port=3000, reload=True)
