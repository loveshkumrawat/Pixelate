import json
from typing import Dict
from supporting import env
from connection.kafka_broker import producer
from connection.redis_conctn import redis_server
from kafka.admin import NewTopic, KafkaAdminClient

bucket_name :str = 'files'

def load_chain(file_id: str):
	
	# Chain signature
	chain_sig = f"Chain-{file_id}"
	
	# Get chain from cache
	chain = redis_server.get(chain_sig)
	if chain: return eval(chain)
	
	# Else load the chain
	with open(".chain", "r") as f: chain = f.read()
	redis_server.set(chain_sig, chain)
	return eval(chain)

def chain_handler(payload: Dict, executed_channel: str = None):
	
	file_id :int = payload["reference"]["file_id"]

	# Loading the chain
	chain = load_chain(file_id)
	
	# Checking if the chain ended
	if payload["offset"] == len(chain): return

	# Checking if any component has been done executing
	if executed_channel:
		
		# Adding the executed channel to the execution dependency
		redis_server.sadd(file_id, executed_channel)
		print(f"{executed_channel} done executing | {payload['reference']['file_name']} | {file_id}")
		
		# Getting the previous chain
		prev_chain = chain[payload["offset"] - 1]
		prev_chain = {prev_chain} if isinstance(prev_chain, str) else set(prev_chain)
		
		# Checking if the execution dependency is satisfied
		if prev_chain - redis_server.smembers(file_id): return
		# Cleaning the unnecessary dependency
		else: redis_server.delete(file_id)
	
	# Getting the next chain
	next_chain = chain[payload["offset"]]
	if isinstance(next_chain, str): next_chain = {next_chain}
	
	# Injecting the dependency injections
	for component in next_chain:
		print(f"{component} initiated | {payload['reference']['file_name']} | {file_id}")
		producer.produce(
			topic=component,
			value=json.dumps(payload)
		)

		producer.flush()

def create_topics(components, num_partitions, replication_factor, topic_configs={"cleanup.policy":"delete", "retention.ms":60}):

	kafka_admin = KafkaAdminClient(bootstrap_servers=f"{env.KAFKA_HOST}:{env.KAFKA_PORT}")

	try:
		kafka_admin.create_topics([
			NewTopic(
				name=component,
				num_partitions=num_partitions,
				replication_factor=replication_factor,
				topic_configs=topic_configs
			)
			
			for component in components
		])
		return "Topics created"
	
	except Exception as e: return "Topics already exists"