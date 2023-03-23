<<<<<<< HEAD
import pymongo
=======
# Require to wait for the services to start
from time import sleep
sleep(5)

>>>>>>> 715906921d29971bab8ab9d6cf033f13475ed9d0
import uvicorn as uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, status
from file_upload.service import upload_file_to_minio
from page_splitter.service import convert_to_image
from text_extractor.service import text_extract_from_file
from metadata_extractor.service import extract_text
from metadata_extractor.mongo_db_connection import database

app = FastAPI()


@app.post("/extractor")
def add_file(file: UploadFile):
    try:

        # check if file is empty or not
        data = file.file.read()
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded File is Empty")

        # upload file
        file_id: int = upload_file_to_minio(data, file.filename)

        # page splitter
        convert_to_image(file_id, file.filename)

        # text extractor
        text_extract_from_file(file_id, file.filename)

        # metadata extractor
        extract_text(file_id, file.filename)

        # return Successful message
        return {"message": "Extraction Done",
                "file_id": file_id}

    except Exception as e:
        print(e)
        return {"message": e}


@app.get("/getData")
def get_meta_data(file_id: int, page_no: int):
    try:
        database.validate_collection(f'{file_id}')
    except pymongo.errors.OperationFailure:
        return {'message': 'collection does not exist'}

    collection = database[f'{file_id}']
    filter_criteria = {"page_no": page_no}
    data = collection.find_one({'page_no': page_no},{'_id':0})
    print(data)
    return  data

    # for x in data:
    #     return x


if __name__ == '__main__': uvicorn.run("router:app", port=3000, reload=True)
