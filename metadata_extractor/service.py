import io
import pytesseract
from PIL import Image
from minio import S3Error
from datetime import datetime
from pytesseract import Output
from supporting.logs import logger
from fastapi import HTTPException, status
from supporting.helper import bucket_name
from metadata_extractor.db_connection import session
from metadata_extractor.models import MetaDataExtractor
from connection.minio_client_connection import minioClient
from metadata_extractor.mongo_db_connection import database


def get_position(top, left, height, width):
	return dict(
		top = top,
		left = left,
		bottom = top + height,
		right = left + width
	)


def extract_metadata(file_id: int, file_name: str):
	
	# add file details to database
	try:
		db_entry = MetaDataExtractor(id=file_id, file_name=file_name, fetch_time=datetime.now())
		session.add(db_entry)
		session.commit()

		logger.debug(f"File details added to 'MetaData Extractor' database")
	
	except Exception as e:
		
		logger.error("error in adding file details to 'MetaData Extractor' database", exc_info=e)
		raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="error in adding file details to 'MetaData Extractor' database")
	
	# get list of files from minio
	objects = minioClient.list_objects(bucket_name, f"{file_id}/pages", recursive=True)
	
	for object in objects:

		if not object.object_name.endswith(".jpg"): continue
		
		# get image from minio
		try:
			img = minioClient.get_object(bucket_name, object.object_name)
			logger.debug(f"Image '{object.object_name}' fetched from minio")
		
		except S3Error as e:
			
			logger.error("error while getting image from minio", exc_info=e)
			db_entry.status = "unsuccessful"
			db_entry.error = e
			session.commit()
			
			raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="error while getting image from minio")
			
		# metadata extraction from image
		pil_img = Image.open(io.BytesIO(img.data))
		img_metadata = pytesseract.image_to_data(pil_img, output_type=Output.DICT)
		logger.info(f"Metadata extracted from image '{object.object_name}'")
		
		db_metadata = dict(
			page_no = img_metadata["page_num"][0] - 1,
			blocks = []
		)

		for indx, level in enumerate(img_metadata["level"][1:], start=1):
			
			block_no = img_metadata["block_num"][indx]
			para_no = img_metadata["par_num"][indx]
			line_no = img_metadata["line_num"][indx]
			word_no = img_metadata["word_num"][indx]
			
			position = get_position(
				top=img_metadata["top"][indx],
				left=img_metadata["left"][indx],
				height=img_metadata["height"][indx],
				width=img_metadata["width"][indx]
			)

			if level == 2: db_metadata["blocks"].append(dict(
				block_no = block_no,
				paragraphs = [],
				categories = ["block"],
				**position
			))

			elif level == 3: db_metadata["blocks"][block_no - 1]["paragraphs"].append(dict(
				para_no = para_no,
				lines = [],
				categories = ["para"],
				**position
			))

			elif level == 4: db_metadata["blocks"][block_no - 1]["paragraphs"][para_no - 1]["lines"].append(dict(
				line_no = line_no,
				words = [],
				categories = ["line"],
				**position
			))

			elif level == 5: db_metadata["blocks"][block_no - 1]["paragraphs"][para_no - 1]["lines"][line_no - 1]["words"].append(dict(
				word_no = word_no,
				word = img_metadata["text"][indx],
				**position
			))
		
		# Storing metadata to the MongoDB
		collection = database[f"{file_id}"]
		collection.insert_one(db_metadata)
		logger.debug(f"Metadata of image '{object.object_name}' stored in MongoDB")
		
	# Update database on successful completion
	db_entry.status = "successful"
	db_entry.submission_time = datetime.now()
	session.commit()

	logger.info(f'Metadata extracted from file with {file_id} file id')
