import uvicorn as uvicorn
from fastapi import FastAPI, UploadFile
from services import page_spliter
from services import json_text_extractor,text_extractor
from services.router_service import *
from connection.mongo_db_connection import database
app = FastAPI()

@app.post("/add_file")
def add_file(file: UploadFile):
    data = file.file.read()
    upload_file_to_minio(data,file.filename)

@app.get("/pageSplitter")
def split_page(file_id,file_name):
    page_spliter.convert_to_image(file_id, file_name)

@app.get("/jsonExtractor")
def json_extraction(page_id:int):
    json_text_extractor.extract_text(page_id)

@app.post("/textExtractor")
def txt_extractor(file_id:int,file_name:str):
    text_extractor.text_extract_from_file(file_id,file_name)

@app.get("/getJsonData")
def get_json_data(id):
    collection = database[f'{id}']
    cursor = collection.find()
    for x in cursor:
        print(x)


if __name__=='__main__':
    uvicorn.run("router:app",port=8001,reload=True)


