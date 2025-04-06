#!/bin/bash

# Define the log file path
LOG_FILE="chat.log"

# Check if the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: $LOG_FILE does not exist"
    exit 1
fi

# Empty the log file
echo "" > "$LOG_FILE"

# Check if the operation was successful
if [ $? -eq 0 ]; then
    echo "Successfully emptied $LOG_FILE"
else
    echo "Error: Failed to empty $LOG_FILE"
    exit 1
fi 