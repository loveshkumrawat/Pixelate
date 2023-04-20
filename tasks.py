# faust -A tasks worker -l info

import json
import faust
from typing import List
from faust import TopicT
from supporting import env
from connection.kafka_broker import producer
from file_upload.service import upload_file_to_minio
from page_splitter.service import convert_to_image
from text_extractor.service import text_extract_from_file
from metadata_extractor.service import extract_metadata


app = faust.App("FaustApp", broker=f"kafka://{env.KAFKA_HOST}:{env.KAFKA_PORT}")

import create_topics
# file_upload_T: TopicT = app.topic('file_upload_T')
page_splitter_T: TopicT = app.topic('page_splitter_T')
text_extractor_T: TopicT = app.topic('text_extractor_T')
metadata_extractor_T: TopicT = app.topic('metadata_extractor_T')

# @app.agent(channel=file_upload_T, concurrency=2)
# async def upload_file_to_minio_agent(reference_stream : List[str]):
	
# 	async for reference in reference_stream:

#		import base64
# 		file_data = base64.b64decode(reference['file_data'])
# 		file_name = reference['file_name']
		
# 		# Upload File Service
# 		file_id: int = upload_file_to_minio(file_data, file_name)

# 		# Dependency Injections
# 		producer.produce(
# 			topic='page_splitter_T',
# 			value=json.dumps({'file_id': file_id, 'file_name': file_name})
# 		)
		
# 		producer.flush()

@app.agent(channel=page_splitter_T, concurrency=2)
async def convert_to_image_agent(reference_stream : List[str]):

	async for reference in reference_stream:
		
		# Page Splitter Service
		convert_to_image(**reference)

		# Dependency Injections
		producer.produce(
			topic='text_extractor_T',
			value=json.dumps(reference)
		)

		producer.produce(
			topic='metadata_extractor_T',
			value=json.dumps(reference)
		)

		producer.flush()

@app.agent(channel=text_extractor_T, concurrency=2)
async def text_extract_from_file_agent(reference_stream : List[str]):

	async for reference in reference_stream:
		
		# Text Extractor Service
		text_extract_from_file(**reference)

		# Dependency Injections
		...

@app.agent(channel=metadata_extractor_T, concurrency=2)
async def extract_metadata_agent(reference_stream : List[str]):

	async for reference in reference_stream:
		
		# Metadata Extractor Service
		extract_metadata(**reference)

		# Dependency Injections
		...