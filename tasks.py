# faust -A tasks worker -l info --web-port 600_

import faust
from faust import TopicT
from supporting import env
from supporting.helper import chain_handler
# from file_upload.service import upload_file_to_minio
from page_splitter.service import convert_to_image
from text_extractor.service import text_extract_from_file
from metadata_extractor.service import extract_metadata


app = faust.App("FaustApp", broker=f"kafka://{env.KAFKA_HOST}:{env.KAFKA_PORT}")

import create_topics
# file_upload_T: TopicT = app.topic('file_upload_T')
page_splitter_T: TopicT = app.topic('page_splitter_T')
text_extractor_T: TopicT = app.topic('text_extractor_T')
metadata_extractor_T: TopicT = app.topic('metadata_extractor_T')
text_meta_T: TopicT = app.topic('text_meta_T')

# @app.agent(channel=file_upload_T, concurrency=2)
# async def upload_file_to_minio_agent(payload_stream : faust.streams.Stream):
	
# 	async for reference in payload_stream:

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
async def convert_to_image_agent(payload_stream : faust.streams.Stream):

	async for payload in payload_stream:
		
		# Page Splitter Service
		convert_to_image(**payload["reference"])
		
		# Chain Handler
		payload["offset"] += 1
		chain_handler(payload, executed_channel="page_splitter_T")

		# # Dependency Injections
		# producer.produce(
		# 	topic='text_extractor_T',
		# 	value=json.dumps(payload),
		# 	partition=0
		# )

		# producer.produce(
		# 	topic='metadata_extractor_T',
		# 	value=json.dumps(payload),
		# 	partition=3
		# )

		# producer.flush()
		
		# await text_extractor_T.send(key="text_extractor", partition=0, value=json.dumps(reference))
		# await metadata_extractor_T.send(key="metadata_extractor", partition=3, value=json.dumps(reference))

@app.agent(channel=text_extractor_T, concurrency=2)
async def text_extract_from_file_agent(payload_stream : faust.streams.Stream):

	async for payload in payload_stream:
		
		# Text Extractor Service
		text_extract_from_file(**payload["reference"])

		# Chain Handler
		payload["offset"] += 1
		chain_handler(payload, executed_channel="text_extractor_T")

@app.agent(channel=metadata_extractor_T, concurrency=2)
async def extract_metadata_agent(payload_stream : faust.streams.Stream):

	async for payload in payload_stream:
		
		# Metadata Extractor Service
		extract_metadata(**payload["reference"])

		# Chain Handler
		payload["offset"] += 1
		chain_handler(payload, executed_channel="metadata_extractor_T")

@app.agent(channel=text_meta_T, concurrency=2)
async def text_meta_agent(payload_stream : faust.streams.Stream):
	
	async for payload in payload_stream:
		
		# Text Meta Service
		print(f"After Text & Meta Extraction for {payload['reference']['file_id']}")

		# Chain Handler
		payload["offset"] += 1
		chain_handler(payload, executed_channel="text_meta_T")

# extract_metadata_agent.add_dependency(text_extract_from_file_agent)

if __name__ == '__main__':
	worker = app.Worker(loglevel='info')
	worker.execute_from_commandline()