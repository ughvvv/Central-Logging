#!/bin/bash

# Script to create index patterns in Kibana using the Kibana API

# Load environment variables from .env file
if [ -f .env ]; then
    # Export variables one by one to avoid issues with spaces and special characters
    export KIBANA_URL=$(grep -v '^#' .env | grep KIBANA_URL | cut -d '=' -f2-)
    export ELASTIC_USERNAME=$(grep -v '^#' .env | grep ELASTIC_USERNAME | cut -d '=' -f2-)
    export ELASTIC_PASSWORD=$(grep -v '^#' .env | grep ELASTIC_PASSWORD | cut -d '=' -f2-)
    export ELASTICSEARCH_URL=$(grep -v '^#' .env | grep ELASTICSEARCH_URL | cut -d '=' -f2-)
else
    echo "Error: .env file not found"
    exit 1
fi

echo "Creating index patterns in Kibana..."
echo "----------------------------------------------------------------------"

# Function to create an index pattern
create_index_pattern() {
    local pattern=$1
    local title=$2
    
    echo "Creating index pattern: $title ($pattern)"
    
    # Create the index pattern using the Kibana API
    curl -X POST "$KIBANA_URL/api/saved_objects/index-pattern/$pattern" \
        -H "kbn-xsrf: true" \
        -H "Content-Type: application/json" \
        -u "$ELASTIC_USERNAME:$ELASTIC_PASSWORD" \
        -d "{
            \"attributes\": {
                \"title\": \"$pattern\",
                \"timeFieldName\": \"@timestamp\"
            }
        }"
    
    echo ""
}

# Create the index patterns
create_index_pattern "orchestrator-logs-*" "Orchestrator Logs"
create_index_pattern "filebeat-*" "Filebeat Logs"
create_index_pattern "metricbeat-*" "Metricbeat Metrics"

echo ""
echo "Index patterns created successfully!"
echo ""
echo "The following index patterns are now available in Kibana:"
echo "- orchestrator-logs-*"
echo "- filebeat-*"
echo "- metricbeat-*"
echo ""
echo "To view the data, go to Kibana > Discover and select an index pattern"
