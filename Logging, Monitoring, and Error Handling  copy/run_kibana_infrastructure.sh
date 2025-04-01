#!/bin/bash

# Script to run the infrastructure with Kibana as the primary visualization tool

echo "Starting infrastructure with Kibana as the primary visualization tool..."
echo "----------------------------------------------------------------------"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is not running or not accessible"
    exit 1
fi

# Start the infrastructure
echo "Starting services (Filebeat, Metricbeat, Prometheus, PostgreSQL)..."
docker-compose -f docker-compose.kibana.yml up -d

# Wait for services to start
echo "Waiting for services to start (this may take a few seconds)..."
sleep 10

# Check if services are running
echo "Checking if services are running..."
if ! docker ps | grep -q "filebeat"; then
    echo "Warning: Filebeat container is not running"
fi

if ! docker ps | grep -q "metricbeat"; then
    echo "Warning: Metricbeat container is not running"
fi

if ! docker ps | grep -q "prometheus"; then
    echo "Warning: Prometheus container is not running"
fi

if ! docker ps | grep -q "postgres"; then
    echo "Warning: PostgreSQL container is not running"
fi

# Load environment variables from .env file
if [ -f .env ]; then
    # Export variables one by one to avoid issues with spaces and special characters
    export KIBANA_URL=$(grep -v '^#' .env | grep KIBANA_URL | cut -d '=' -f2-)
    export ELASTIC_USERNAME=$(grep -v '^#' .env | grep ELASTIC_USERNAME | cut -d '=' -f2-)
    export ELASTIC_PASSWORD=$(grep -v '^#' .env | grep ELASTIC_PASSWORD | cut -d '=' -f2-)
    export ELASTICSEARCH_URL=$(grep -v '^#' .env | grep ELASTICSEARCH_URL | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_WEB_SECURITY=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_WEB_SECURITY | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_EXTENSIONS=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_EXTENSIONS | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_PLUGINS=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_PLUGINS | cut -d '=' -f2-)
    export BROWSER_ARGS_NO_SANDBOX=$(grep -v '^#' .env | grep BROWSER_ARGS_NO_SANDBOX | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_POPUP_BLOCKING=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_POPUP_BLOCKING | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_NOTIFICATIONS=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_NOTIFICATIONS | cut -d '=' -f2-)
else
    echo "Warning: .env file not found, using default values"
    export KIBANA_URL="https://aiif-logging.kb.us-east-2.aws.elastic-cloud.com:443"
    export ELASTIC_USERNAME="elastic"
    export ELASTIC_PASSWORD="8gwuBTOzZjmVMVqSMLqqtEcP"
fi

echo ""
echo "Infrastructure is now running!"
echo ""
echo "Access points:"
echo "- Kibana: $KIBANA_URL"
echo "  Username: $ELASTIC_USERNAME"
echo "  Password: $ELASTIC_PASSWORD"
echo ""
echo "- Prometheus: http://localhost:9090"
echo ""
echo "Opening Kibana in your browser with auto-login..."

# Use the open_kibana.sh script to open Kibana with browser security bypassed
if [ -f ./open_kibana.sh ]; then
    ./open_kibana.sh
else
    echo "Warning: open_kibana.sh script not found"
    echo "Please open $KIBANA_URL in your browser manually and log in with:"
    echo "Username: $ELASTIC_USERNAME"
    echo "Password: $ELASTIC_PASSWORD"
fi

echo ""
echo "Next steps:"
echo "1. In Kibana, go to Stack Management > Index Patterns"
echo "2. Create index patterns for:"
echo "   - orchestrator-logs-*"
echo "   - filebeat-*"
echo "   - metricbeat-*"
echo "3. Go to Kibana > Dashboard to create visualizations"
echo ""
echo "To run the test agent and generate sample data:"
echo "./run_test_agent.sh"
