# faust -A tasks worker -l info --web-port 600_

import faust
from faust import TopicT
from supporting import env
from supporting.logs import logger
from supporting.helper import chain_handler, create_topics
from page_splitter.service import convert_to_image
from text_extractor.service import text_extract_from_file
from metadata_extractor.service import extract_metadata


app = faust.App("FaustApp", broker=f"kafka://{env.KAFKA_HOST}:{env.KAFKA_PORT}")

# Topics creation
create_topics(
	components=[
		"page_splitter_T",
		"text_extractor_T",
		"metadata_extractor_T",
		"mark_complete_T"
	],
	num_partitions=4,
	replication_factor=1
)

page_splitter_T: TopicT = app.topic('page_splitter_T')
text_extractor_T: TopicT = app.topic('text_extractor_T')
metadata_extractor_T: TopicT = app.topic('metadata_extractor_T')
mark_complete_T: TopicT = app.topic('mark_complete_T')

@app.agent(channel=page_splitter_T, concurrency=2)
async def convert_to_image_agent(payload_stream : faust.streams.Stream):

	async for payload in payload_stream:
		
		# Page Splitter Service
		convert_to_image(**payload["reference"])
		
		# Chain Handler
		payload["offset"] += 1
		chain_handler(payload, executed_channel="page_splitter_T")

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

@app.agent(channel=mark_complete_T, concurrency=2)
async def mark_complete_agent(payload_stream : faust.streams.Stream):
	
	async for payload in payload_stream:
		
		# Mark complete service
		print(f"Marking complete processing of {payload['reference']['file_name']} | {payload['reference']['file_id']}")

		# Chain Handler
		payload["offset"] += 1
		chain_handler(payload, executed_channel="mark_complete_T")

# extract_metadata_agent.add_dependency(text_extract_from_file_agent)

if __name__ == '__main__':
	worker = app.Worker(loglevel='info')
	worker.execute_from_commandline()