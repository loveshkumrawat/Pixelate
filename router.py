import uvicorn as uvicorn
from fastapi import FastAPI, UploadFile
from file_upload.service import upload_file_to_minio
from page_splitter.service import convert_to_image
from text_extractor.service import text_extract_from_file
from metadata_extractor.service import extract_text

app = FastAPI()


@app.post("/extractor")
def add_file(file: UploadFile):
    try:
        # upload file
        data = file.file.read()
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
        return {"message": "Some exception have arise, Try again."}


if __name__ == '__main__':
    uvicorn.run("router:app", port=8001, reload=True)
