#!/bin/bash

# Script to run the entire infrastructure, test agent, and open visualization tools

echo "Starting the entire infrastructure, test agent, and visualization tools..."
echo "----------------------------------------------------------------------"

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

# Step 1: Start the infrastructure with Kibana
echo "Step 1: Starting the infrastructure with Kibana..."
./run_kibana_infrastructure.sh

# Step 2: Run the test agent in the background
echo "Step 2: Starting the test agent in the background..."
./run_test_agent.sh &
TEST_AGENT_PID=$!

# Step 3: Wait a bit for the test agent to generate some data
echo "Step 3: Waiting for the test agent to generate some data..."
sleep 15

# Step 4: Create Kibana index patterns
echo "Step 4: Creating Kibana index patterns..."
if [ -f ./create_kibana_index_patterns.sh ]; then
    ./create_kibana_index_patterns.sh
else
    echo "Warning: create_kibana_index_patterns.sh script not found"
    echo "Please create the index patterns manually through the Kibana UI"
fi

# Step 5: Import Kibana dashboards
echo "Step 5: Importing Kibana dashboards..."
if [ -f ./import_kibana_dashboards.sh ]; then
    ./import_kibana_dashboards.sh
else
    echo "Warning: import_kibana_dashboards.sh script not found"
    echo "Please import the dashboards manually through the Kibana UI"
fi

# Step 6: Open Prometheus
echo "Step 6: Opening Prometheus..."
if [ -f ./open_prometheus.sh ]; then
    ./open_prometheus.sh
else
    echo "Warning: open_prometheus.sh script not found"
    echo "Please open http://localhost:9090 in your browser manually"
fi

echo ""
echo "All components are now running!"
echo ""
echo "Access points:"
echo "- Kibana: $KIBANA_URL"
echo "  Username: $ELASTIC_USERNAME"
echo "  Password: $ELASTIC_PASSWORD"
echo ""
echo "- Prometheus: http://localhost:9090"
echo ""
echo "The test agent is running in the background (PID: $TEST_AGENT_PID)"
echo "To stop the test agent, run: kill $TEST_AGENT_PID"
echo ""
echo "Kibana setup has been automated:"
echo "- Index patterns have been created"
echo "- Sample dashboards have been imported"
echo ""
echo "To view the dashboards, go to Kibana > Dashboard"
echo "Available dashboards:"
echo "- Log Analysis Dashboard"
echo "- Metrics Dashboard"
echo "- Operational Overview Dashboard"
