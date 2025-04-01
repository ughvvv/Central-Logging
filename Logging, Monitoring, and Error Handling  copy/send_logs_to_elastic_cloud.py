#!/usr/bin/env python3
"""
Script to send logs directly to Elastic Cloud.
This script reads the logs from the test agent and sends them to Elastic Cloud.
"""

import json
import requests
import sys
import time
from datetime import datetime

# Elastic Cloud credentials
ELASTIC_CLOUD_URL = "https://aiif-logging.es.us-east-2.aws.elastic-cloud.com:443"
ELASTIC_CLOUD_USERNAME = "elastic"
ELASTIC_CLOUD_PASSWORD = "8gwuBTOzZjmVMVqSMLqqtEcP"

def send_log_to_elastic_cloud(log_data):
    """Send a log entry to Elastic Cloud."""
    # Parse the log data
    try:
        log_entry = json.loads(log_data)
    except json.JSONDecodeError:
        print(f"Error parsing log data: {log_data}")
        return False
    
    # Add @timestamp field if not present
    if "@timestamp" not in log_entry:
        log_entry["@timestamp"] = log_entry.get("timestamp", datetime.utcnow().isoformat() + "Z")
    
    # Create index name based on agent_name
    agent_name = log_entry.get("agent_name", "unknown")
    index_name = f"{agent_name.lower()}-logs-{datetime.utcnow().strftime('%Y.%m.%d')}"
    
    # Send log to Elastic Cloud
    url = f"{ELASTIC_CLOUD_URL}/{index_name}/_doc"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            url,
            auth=(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            headers=headers,
            json=log_entry,
            verify=True
        )
        
        if response.status_code in (200, 201):
            print(f"✓ Log sent to Elastic Cloud: {response.json().get('_id')}")
            return True
        else:
            print(f"✗ Failed to send log to Elastic Cloud: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error sending log to Elastic Cloud: {e}")
        return False

def main():
    """Main function."""
    print("=== Sending Logs to Elastic Cloud ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Elasticsearch URL: {ELASTIC_CLOUD_URL}")
    
    # Check if Elastic Cloud is accessible
    try:
        response = requests.get(
            ELASTIC_CLOUD_URL,
            auth=(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            verify=True
        )
        
        if response.status_code == 200:
            print("✓ Successfully connected to Elasticsearch")
            print(f"  Version: {response.json().get('version', {}).get('number', 'unknown')}")
        else:
            print(f"✗ Failed to connect to Elasticsearch: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"✗ Error connecting to Elasticsearch: {e}")
        return
    
    # Read logs from stdin
    print("\nReading logs from stdin. Press Ctrl+C to stop.")
    try:
        for line in sys.stdin:
            line = line.strip()
            if line:
                send_log_to_elastic_cloud(line)
    except KeyboardInterrupt:
        print("\nStopped reading logs.")
    
    print("\n=== Sending Complete ===")

if __name__ == "__main__":
    main()
