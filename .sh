# List topics
kafka-topics --bootstrap-server localhost:9092 --list

# Delete topic
kafka-topics --bootstrap-server localhost:9092 --topic page_splitter_T --delete

# Describe topic
kafka-topics --bootstrap-server localhost:9092 --topic page_splitter_T --describe

# Alter topic partitions (increase)
kafka-topics --bootstrap-server localhost:9092 --alter --topic page_splitter_T --partitions 6

# List topics objects
kafka-console-consumer --bootstrap-server localhost:9092 --topic page_splitter_T --from-beginning --timeout-ms 1000

# Partition details
kafka-console-consumer --bootstrap-server localhost:9092 --topic page_splitter_T --partition 0 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic page_splitter_T --partition 1 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic page_splitter_T --partition 2 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic page_splitter_T --partition 3 --from-beginning --timeout-ms 1000

kafka-console-consumer --bootstrap-server localhost:9092 --topic text_extractor_T --partition 0 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic text_extractor_T --partition 1 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic text_extractor_T --partition 2 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic text_extractor_T --partition 3 --from-beginning --timeout-ms 1000

kafka-console-consumer --bootstrap-server localhost:9092 --topic metadata_extractor_T --partition 0 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic metadata_extractor_T --partition 1 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic metadata_extractor_T --partition 2 --from-beginning --timeout-ms 1000
kafka-console-consumer --bootstrap-server localhost:9092 --topic metadata_extractor_T --partition 3 --from-beginning --timeout-ms 1000
