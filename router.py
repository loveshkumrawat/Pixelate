from fastapi import FastAPI, UploadFile
from services import page_spliter
from services import json_text_extractor
from services.router_service import *
app = FastAPI()

@app.post("/add_file")
def add_file(file: UploadFile):
    data = file.file.read()
    upload_file_to_minio(data,file.filename)

@app.get("/pageSplitter")
def split_page(file_id,file_name):
    page_spliter.convert_to_image(file_id, file_name)

@app.get("/textExtractor")
def text_extraction(page_id:int):
    json_text_extractor.extract_text(page_id)



