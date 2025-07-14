#!/bin/bash
set -e

# The first argument to this script determines which service to run.
COMMAND=$1

# Function to start the FastAPI application
start_api() {
    echo "Starting IDX Agent API..."
    # Use exec to replace the shell process with the uvicorn process
    exec uvicorn api.main:app --host "0.0.0.0" --port 8001
}

# Function to start the Streamlit UI
start_ui() {
    echo "Starting IDX Agent UI..."
    # Use exec to replace the shell process with the streamlit process
    exec streamlit run ui/app.py --server.port 8502 --server.address 0.0.0.0
}

# Check the command and execute the corresponding function
if [ "$COMMAND" = "api" ]; then
    start_api
elif [ "$COMMAND" = "ui" ]; then
    start_ui
else
    echo "Error: Invalid command specified: '$COMMAND'"
    echo "Usage: $0 {api|ui}"
    exit 1
fi