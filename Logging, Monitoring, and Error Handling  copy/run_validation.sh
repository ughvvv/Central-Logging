#!/bin/bash

# Run validation for the logging, monitoring, and error handling infrastructure

echo "=== Starting Infrastructure Validation ==="
echo "Step 1: Starting Docker Compose services..."

# Start Docker Compose services
docker-compose up -d

# Wait for services to be ready
echo "Step 2: Waiting for services to be ready..."
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

echo "Step 3: Installing Python dependencies..."
pip install -r requirements.txt

echo "Step 4: Running validation script..."
python3 validate_infrastructure.py

echo "=== Validation Complete ==="
echo "You can now check the services at:"
echo "- Elasticsearch: http://localhost:9200"
echo "- Kibana: http://localhost:5601"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo "- PostgreSQL: localhost:5432 (orchestrator_db/orchestrator_admin/orchestrator_password)"
