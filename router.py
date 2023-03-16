from fastapi import FastAPI, UploadFile
from Services import page_spliiter
from Services import json_text_extractor
from Services.router_service import *
app = FastAPI()

@app.post("/add_file")
def add_file(file: UploadFile):
    data = file.file.read()
    upload_file_to_minio(data,file.filename)

@app.get("/pageSplitter")
def split_page(file_id,file_name):
    page_spliiter.convert_to_image(file_id, file_name)

@app.get("/textExtractor")
def text_extraction(page_id:int):
    text_extractor.extract_text(page_id)


