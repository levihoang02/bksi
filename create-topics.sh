#!/bin/bash

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 15  # Adjust the sleep time as necessary

# Define an array of topics to create
TOPICS=("highlight" "sumarize" "report" "highlight-res" "sumarize-res" "report-res")  # Add your topic names here
REPLICATION_FACTOR=3
PARTITIONS=2

# Loop through each topic and create it if it doesn't exist
for TOPIC_NAME in "${TOPICS[@]}"; do
  EXISTING_TOPICS=$(docker exec kafka1 kafka-topics --list --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094)

  if echo "$EXISTING_TOPICS" | grep -q "$TOPIC_NAME"; then
    echo "Topic '$TOPIC_NAME' already exists."
  else
    echo "Creating topic '$TOPIC_NAME'..."
    docker exec kafka1 kafka-topics --create --topic "$TOPIC_NAME" --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --replication-factor $REPLICATION_FACTOR --partitions $PARTITIONS
    echo "Topic '$TOPIC_NAME' created."
  fi
done