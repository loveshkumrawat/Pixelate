import json
from typing import Dict, Set
from supporting.logs import logger
from connection.kafka_broker import producer

bucket_name :str = 'files'
execution_dependency : Dict[int, Set[str]] = {}

def load_chain():
	
	with open(".chain", "r") as f: chain = f.read()
	return eval(chain)

def chain_handler(payload: Dict, executed_channel: str = None):
	
	# Loading the chain
	chain = load_chain()
	
	# Checking if the chain ended
	if payload["offset"] == len(chain):
		logger.info(f"File '{payload['reference']['file_name']}' has been processed successfully")
		return

	# Checking if any component has been done executing
	if executed_channel:
		
		# Adding the executed channel to the execution dependency
		execution_dependency.setdefault(payload["reference"]["file_id"], set()).add(executed_channel)
		logger.info(f"Execution Dependency: {executed_channel} done executing for {payload['reference']['file_name']}")
		
		# Getting the previous chain
		prev_chain = chain[payload["offset"] - 1]
		prev_chain = {prev_chain} if isinstance(prev_chain, str) else set(prev_chain)
		
		# Checking if the execution dependency is satisfied
		if prev_chain - execution_dependency[payload["reference"]["file_id"]]: return
		# Cleaning the unnecessary dependency
		else: execution_dependency.pop(payload["reference"]["file_id"])
	
	# Getting the next chain
	next_chain = chain[payload["offset"]]
	if isinstance(next_chain, str): next_chain = {next_chain}
	
	# Injecting the dependency injections
	for component in next_chain:
		print(component)
		producer.produce(
			topic=component,
			value=json.dumps(payload)
		)

		producer.flush()