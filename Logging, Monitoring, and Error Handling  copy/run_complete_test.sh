#!/bin/bash

# Run a complete test of the logging, monitoring, and error handling infrastructure
# This script will:
# 1. Start all services
# 2. Run the validation script
# 3. Run the test agent
# 4. Provide instructions for checking the results

echo "=== Starting Complete Test ==="
echo "This script will run a complete test of the infrastructure:"
echo "1. Start all services"
echo "2. Run the validation script"
echo "3. Run the test agent"
echo "4. Provide instructions for checking the results"
echo ""
echo "Press Ctrl+C at any time to stop the test"
echo ""
echo "Press Enter to continue..."
read

# Step 1: Start all services
echo "=== Step 1: Starting Services ==="
docker-compose down
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
echo "This may take a minute or two..."

# Function to check if a service is ready
check_service() {
    local service=$1
    local url=$2
    local max_attempts=$3
    local attempt=1
    
    echo "Checking $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✓ $service is ready"
            return 0
        fi
        
        echo "  Attempt $attempt/$max_attempts: $service not ready yet, waiting..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "✗ $service did not become ready in time"
    return 1
}

# Check if Elasticsearch is ready
check_service "Elasticsearch" "http://localhost:9200" 12

# Check if Kibana is ready
check_service "Kibana" "http://localhost:5601" 12

# Check if Prometheus is ready
check_service "Prometheus" "http://localhost:9090" 6

# Check if Grafana is ready
check_service "Grafana" "http://localhost:3000" 6

# Step 2: Run the validation script
echo ""
echo "=== Step 2: Running Validation Script ==="
echo "This will validate the infrastructure components..."
echo ""
echo "Press Enter to continue..."
read

# Install dependencies
pip install -r requirements.txt

# Run the validation script
python validate_infrastructure.py

echo ""
echo "Validation complete. Press Enter to continue to the test agent..."
read

# Step 3: Run the test agent
echo ""
echo "=== Step 3: Running Test Agent ==="
echo "The test agent will run for 60 seconds to generate logs and metrics..."
echo ""

# Run the test agent for 60 seconds
timeout 60s python test_agent.py || true

echo ""
echo "Test agent completed."

# Step 4: Provide instructions for checking the results
echo ""
echo "=== Step 4: Checking Results ==="
echo "You can now check the results in the following dashboards:"
echo ""
echo "1. Kibana (http://localhost:5601)"
echo "   - Create index patterns for 'filebeat-*' and 'orchestrator-logs-*'"
echo "   - Go to Discover to view logs"
echo "   - Filter by agent_name to see logs from 'orchestrator' and 'test_agent_1'"
echo ""
echo "2. Prometheus (http://localhost:9090)"
echo "   - Query metrics like 'tasks_dispatched' and 'errors_encountered'"
echo "   - Check that metrics are labeled by task_type and error_type"
echo ""
echo "3. Grafana (http://localhost:3000)"
echo "   - Login with admin/admin"
echo "   - View the pre-configured dashboard"
echo "   - Check that metrics are being displayed correctly"
echo ""
echo "4. PostgreSQL"
echo "   - Connect to the database (localhost:5432, orchestrator_db/orchestrator_admin/orchestrator_password)"
echo "   - Check the task_states, task_history, and agents tables"
echo ""
echo "=== Complete Test Finished ==="
echo "You can now explore the infrastructure and develop your own agents."
