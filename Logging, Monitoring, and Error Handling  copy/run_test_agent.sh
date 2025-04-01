#!/bin/bash

# Run the test agent for the logging, monitoring, and error handling infrastructure

echo "=== Starting Test Agent ==="
echo "Step 1: Checking if infrastructure is running..."

# Check if Elasticsearch is running
if ! curl -s -f "http://localhost:9200" > /dev/null 2>&1; then
    echo "Elasticsearch is not running. Please start the infrastructure first with:"
    echo "  docker-compose up -d"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 -U orchestrator_admin > /dev/null 2>&1; then
    echo "PostgreSQL is not running. Please start the infrastructure first with:"
    echo "  docker-compose up -d"
    exit 1
fi

echo "✓ Infrastructure is running"

echo "Step 2: Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Step 3: Running test agent..."
echo "The test agent will:"
echo "- Register itself in the database"
echo "- Create test tasks"
echo "- Process tasks with simulated errors and retries"
echo "- Log events to Elasticsearch"
echo "- Expose metrics on port 8001"
echo ""
echo "Press Ctrl+C to stop the agent"
echo ""

python3 test_agent.py

# This will only execute if the agent exits normally
echo "=== Test Agent Stopped ==="
