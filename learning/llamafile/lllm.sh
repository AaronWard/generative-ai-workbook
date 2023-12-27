#!/bin/bash

# Model directory path
MODEL_DIR="/Users/award40/Desktop/personal/github/_models/"
SERVER_PID_FILE="/tmp/lllm_server_pids"

# Function to list all available models
list_models() {
    echo "Available models:"
    echo "  - mistral-main"
    echo "  - mistral-server"
    echo "  - wizard-main"
    echo "  - wizard-server"
}

# Function to run LLM models
lllm() {
    if [[ $1 == "--list-models" ]]; then
        list_models
        return
    fi

    if [[ $1 == "--shutdown-servers" ]]; then
        if [ -f "$SERVER_PID_FILE" ]; then
            while read -r pid; do
                if ps -p $pid > /dev/null; then
                    echo "Shutting down server with PID $pid"
                    kill $pid
                else
                    echo "No running server found with  $pid"
                fi
            done < "$SERVER_PID_FILE"
            > "$SERVER_PID_FILE" # Clear the PID file after shutdown
        else
            echo "No server is currently running."
        fi
        return
    fi

    local prompt=$1
    local model_alias=$2
    local temp=${3:-0.7}
    local port=${4:-8080}
    local model_file

    # Determine the model file based on alias
    case "$model_alias" in
        mistral-main)
            model_file="${MODEL_DIR}mistral-7b-instruct-v0.1-Q4_K_M-main.llamafile --nobrowser --log-disable"
            ;;
        mistral-server)
            model_file="${MODEL_DIR}mistral-7b-instruct-v0.1-Q4_K_M-server.llamafile --port ${port} --nobrowser --log-disable"
            ;;
        wizard-main)
            model_file="${MODEL_DIR}wizardcoder-python-13b-main.llamafile --nobrowser --log-disable"
            ;;
        wizard-server)
            model_file="${MODEL_DIR}wizardcoder-python-13b-server.llamafile --port ${port} --nobrowser --log-disable"
            ;;
        *)
            echo "Unknown model alias: $model_alias"
            return 1
            ;;
    esac

    # Execute the model with appropriate parameters
    if [[ $model_alias == *"-server" ]]; then
        echo "Running server on port ${port}..."
        $model_file &
        echo $! >> "$SERVER_PID_FILE"
    else
        $model_file --temp $temp -p "$prompt"
    fi
}

# Usage examples:
# lllm "list 5 pros and cons of python" mistral-main
# lllm "" mistral-server 0.7 8081
# lllm --list-models
# lsof -i -P
# ps aux | grep wizard
