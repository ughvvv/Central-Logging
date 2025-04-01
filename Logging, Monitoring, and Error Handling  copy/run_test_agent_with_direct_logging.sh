#!/bin/bash

# Run the test agent and pipe its output to the send_logs_to_elastic_cloud.py script

echo "=== Starting Test Agent with Direct Logging to Elastic Cloud ==="
echo "Step 1: Checking if infrastructure is running..."

# Check if Prometheus is running
if ! curl -s -f "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    echo "Prometheus is not running. Please start the infrastructure first with:"
    echo "  ./run_cloud_infrastructure.sh"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 -U orchestrator_admin > /dev/null 2>&1; then
    echo "PostgreSQL is not running. Please start the infrastructure first with:"
    echo "  ./run_cloud_infrastructure.sh"
    exit 1
fi

echo "✓ Infrastructure is running"

echo "Step 2: Installing Python dependencies..."
pip install -r requirements.txt

echo "Step 3: Running test agent with direct logging to Elastic Cloud..."
echo "The test agent will:"
echo "- Register itself in the database"
echo "- Create test tasks"
echo "- Process tasks with simulated errors and retries"
echo "- Log events directly to Elastic Cloud"
echo "- Expose metrics on port 8001"
echo ""
echo "Press Ctrl+C to stop the agent"
echo ""

# Run the test agent and pipe its output to the send_logs_to_elastic_cloud.py script
python3 test_agent.py | tee >(./send_logs_to_elastic_cloud.py)

# This will only execute if the agent exits normally
echo "=== Test Agent Stopped ==="
