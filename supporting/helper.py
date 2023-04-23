import json
from supporting import env
from typing import Dict, Set
from connection.kafka_broker import producer
from kafka.admin import NewTopic, KafkaAdminClient

bucket_name :str = 'files'
execution_dependency : Dict[int, Set[str]] = {}

def load_chain():
	
	with open(".chain", "r") as f: chain = f.read()
	return eval(chain)

def chain_handler(payload: Dict, executed_channel: str = None):
	
	# Loading the chain
	chain = load_chain()
	
	# Checking if the chain ended
	if payload["offset"] == len(chain): return

	# Checking if any component has been done executing
	if executed_channel:
		
		# Adding the executed channel to the execution dependency
		execution_dependency.setdefault(payload["reference"]["file_id"], set()).add(executed_channel)
		print(f"{executed_channel} done executing | {payload['reference']['file_name']} | {payload['reference']['file_id']}")
		
		# Getting the previous chain
		prev_chain = chain[payload["offset"] - 1]
		prev_chain = {prev_chain} if isinstance(prev_chain, str) else set(prev_chain)
		
		#TODO: Problem while completion of all previous components at a same time
		# Checking if the execution dependency is satisfied
		if prev_chain - execution_dependency[payload["reference"]["file_id"]]: return
		# Cleaning the unnecessary dependency
		else: execution_dependency.pop(payload["reference"]["file_id"])
	
	# Getting the next chain
	next_chain = chain[payload["offset"]]
	if isinstance(next_chain, str): next_chain = {next_chain}
	
	# Injecting the dependency injections
	for component in next_chain:
		print(f"{component} initiated")
		producer.produce(
			topic=component,
			value=json.dumps(payload)
		)

		producer.flush()

def create_topics(components, num_partitions, replication_factor, topic_configs={"cleanup.policy":"delete", "delete.retention.ms":60}):

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