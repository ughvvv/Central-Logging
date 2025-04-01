#!/bin/bash

# Run the logging, monitoring, and error handling infrastructure using Elastic Cloud
# This script will:
# 1. Start the local services (Filebeat, Prometheus, Grafana, PostgreSQL)
# 2. Run the validation script
# 3. Run the test agent
# 4. Provide instructions for checking the results

echo "=== Starting Cloud-Based Infrastructure ==="
echo "This script will run the infrastructure using Elastic Cloud:"
echo "1. Start the local services (Filebeat, Prometheus, Grafana, PostgreSQL)"
echo "2. Run the validation script"
echo "3. Run the test agent"
echo "4. Provide instructions for checking the results"
echo ""

# Step 1: Start all services
echo "=== Step 1: Starting Services ==="
docker-compose -f docker-compose.cloud.yml down
docker-compose -f docker-compose.cloud.yml up -d

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
    # Don't fail the script if a service isn't ready
    return 0
}

# Check if Prometheus is ready
check_service "Prometheus" "http://localhost:9090" 6

# Check if Grafana is ready
check_service "Grafana" "http://localhost:3000" 12

# Check if Elastic Cloud is accessible
check_service "Elasticsearch (Cloud)" "https://aiif-logging.es.us-east-2.aws.elastic-cloud.com:443" 6

# Step 2: Run the validation script
echo ""
echo "=== Step 2: Running Validation Script ==="
echo "This will validate the infrastructure components..."
echo ""

# Install dependencies
pip install -r requirements.txt

# Run the validation script
python3 validate_cloud_infrastructure.py

echo ""
echo "Validation complete."

# Step 3: Run the test agent
echo ""
echo "=== Step 3: Running Test Agent ==="
echo "The test agent will run for 60 seconds to generate logs and metrics..."
echo ""

# Run the test agent for 60 seconds (macOS doesn't have timeout command)
python3 test_agent.py &
TEST_AGENT_PID=$!
sleep 60
kill $TEST_AGENT_PID 2>/dev/null || true

echo ""
echo "Test agent completed."

# Step 4: Provide instructions for checking the results
echo ""
echo "=== Step 4: Checking Results ==="
echo "You can now check the results in the following dashboards:"
echo ""
echo "1. Kibana (https://aiif-logging.kb.us-east-2.aws.elastic-cloud.com)"
echo "   - Login with elastic/8gwuBTOzZjmVMVqSMLqqtEcP"
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
echo "   - Elasticsearch data source has been configured to connect to Elastic Cloud"
echo ""
echo "4. PostgreSQL"
echo "   - Connect to the database (localhost:5432, orchestrator_db/orchestrator_admin/orchestrator_password)"
echo "   - Check the task_states, task_history, and agents tables"
echo ""
echo "=== Cloud Infrastructure Setup Complete ==="
echo "You can now explore the infrastructure and develop your own agents."
