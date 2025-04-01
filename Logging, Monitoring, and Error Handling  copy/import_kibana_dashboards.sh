#!/bin/bash

# Script to import sample dashboards into Kibana using the Kibana API

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

echo "Importing sample dashboards into Kibana..."
echo "----------------------------------------------------------------------"

# Check if the sample dashboards file exists
if [ ! -f kibana_sample_dashboards.ndjson ]; then
    echo "Error: kibana_sample_dashboards.ndjson file not found"
    exit 1
fi

# Import the dashboards using the Kibana API
echo "Importing dashboards using the Kibana API..."
curl -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
    -H "kbn-xsrf: true" \
    -H "Content-Type: multipart/form-data" \
    -u "$ELASTIC_USERNAME:$ELASTIC_PASSWORD" \
    -F "file=@kibana_sample_dashboards.ndjson"

# Check if the import was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Dashboards imported successfully!"
    echo ""
    echo "The following dashboards are now available in Kibana:"
    echo "- Log Analysis Dashboard"
    echo "- Metrics Dashboard"
    echo "- Operational Overview Dashboard"
    echo ""
    echo "To view the dashboards, go to Kibana > Dashboard"
else
    echo ""
    echo "Error: Failed to import dashboards"
    echo "Please try importing them manually through the Kibana UI:"
    echo "1. Go to Stack Management > Saved Objects"
    echo "2. Click Import"
    echo "3. Select the kibana_sample_dashboards.ndjson file"
    echo "4. Click Import"
fi
