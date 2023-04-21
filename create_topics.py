from supporting import env
from kafka.admin import NewTopic, KafkaAdminClient


kafka_admin = KafkaAdminClient(bootstrap_servers=f"{env.KAFKA_HOST}:{env.KAFKA_PORT}")

topic_configs = {"cleanup.policy":"delete", "delete.retention.ms":60}

try:
	kafka_admin.create_topics([
		# NewTopic(
		# 	name='file_upload_T',
		# 	num_partitions=4,
		# 	replication_factor=1,
		# 	topic_configs=topic_configs
		# ),
		NewTopic(
			name='page_splitter_T',
			num_partitions=4,
			replication_factor=1,
			topic_configs=topic_configs
		),
		NewTopic(
			name='text_extractor_T',
			num_partitions=4,
			replication_factor=1,
			topic_configs=topic_configs
		),
		NewTopic(
			name='metadata_extractor_T',
			num_partitions=4,
			replication_factor=1,
			topic_configs=topic_configs
		),
		NewTopic(
			name='text_meta_T',
			num_partitions=4,
			replication_factor=1,
			topic_configs=topic_configs
		)
	])
except Exception as e: print(e)