#!/usr/bin/env python3
"""
Script to check if logs are being indexed in Elastic Cloud.
This script queries the Elastic Cloud deployment to verify that logs are being indexed.
"""

import requests
import json
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

# Elastic Cloud credentials
ELASTIC_CLOUD_URL = "https://aiif-logging.es.us-east-2.aws.elastic-cloud.com:443"
ELASTIC_CLOUD_USERNAME = "elastic"
ELASTIC_CLOUD_PASSWORD = "8gwuBTOzZjmVMVqSMLqqtEcP"

def check_indices():
    """Check what indices exist in Elasticsearch."""
    print("Checking indices in Elasticsearch...")
    
    try:
        response = requests.get(
            f"{ELASTIC_CLOUD_URL}/_cat/indices?v",
            auth=HTTPBasicAuth(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            verify=True
        )
        
        if response.status_code == 200:
            print("✓ Successfully connected to Elasticsearch")
            print("Available indices:")
            print(response.text)
        else:
            print(f"✗ Failed to get indices: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error connecting to Elasticsearch: {e}")

def check_filebeat_indices():
    """Check for Filebeat indices in Elasticsearch."""
    print("\nChecking for Filebeat indices...")
    
    try:
        response = requests.get(
            f"{ELASTIC_CLOUD_URL}/_cat/indices/filebeat-*?v",
            auth=HTTPBasicAuth(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            verify=True
        )
        
        if response.status_code == 200:
            if response.text.strip():
                print("✓ Found Filebeat indices:")
                print(response.text)
            else:
                print("✗ No Filebeat indices found")
        else:
            print(f"✗ Failed to get Filebeat indices: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error checking Filebeat indices: {e}")

def check_test_agent_indices():
    """Check for test agent indices in Elasticsearch."""
    print("\nChecking for test agent indices...")
    
    try:
        response = requests.get(
            f"{ELASTIC_CLOUD_URL}/_cat/indices/test_agent_*?v",
            auth=HTTPBasicAuth(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            verify=True
        )
        
        if response.status_code == 200:
            if response.text.strip():
                print("✓ Found test agent indices:")
                print(response.text)
            else:
                print("✗ No test agent indices found")
        else:
            print(f"✗ Failed to get test agent indices: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error checking test agent indices: {e}")

def search_logs():
    """Search for logs in Elasticsearch."""
    print("\nSearching for logs in Elasticsearch...")
    
    # Calculate timestamp for the last week
    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)
    timestamp_range = {
        "range": {
            "@timestamp": {
                "gte": one_week_ago.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "lte": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        }
    }
    
    # Search query for any logs
    query = {
        "query": {
            "bool": {
                "must": [
                    timestamp_range
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": 10
    }
    
    # Search query for filebeat logs specifically
    filebeat_query = {
        "query": {
            "bool": {
                "must": [
                    timestamp_range,
                    {
                        "match": {
                            "input.type": "container"
                        }
                    }
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": 10
    }
    
    # Search query for test agent logs specifically
    test_agent_query = {
        "query": {
            "bool": {
                "must": [
                    timestamp_range,
                    {
                        "match": {
                            "agent_name": "test_agent_1"
                        }
                    }
                ]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": 10
    }
    
    try:
        # Search across all indices
        print("\nSearching all indices:")
        response = requests.post(
            f"{ELASTIC_CLOUD_URL}/_search",
            auth=HTTPBasicAuth(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            json=query,
            headers={"Content-Type": "application/json"},
            verify=True
        )
        
        if response.status_code == 200:
            result = response.json()
            hits = result.get("hits", {}).get("hits", [])
            
            if hits:
                print(f"✓ Found {len(hits)} logs in Elasticsearch")
                print("\nSample logs:")
                for hit in hits[:3]:  # Show first 3 logs
                    source = hit.get("_source", {})
                    print(f"- Index: {hit.get('_index')}")
                    print(f"  Timestamp: {source.get('@timestamp')}")
                    print(f"  Agent: {source.get('agent_name')}")
                    print(f"  Event: {source.get('event_type')}")
                    print(f"  Message: {source.get('message')}")
                    print()
            else:
                print("✗ No logs found in Elasticsearch")
        else:
            print(f"✗ Failed to search logs: {response.status_code}")
            print(response.text)
            
        # Search for filebeat logs
        print("\nSearching for Filebeat logs:")
        response = requests.post(
            f"{ELASTIC_CLOUD_URL}/_search",
            auth=HTTPBasicAuth(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            json=filebeat_query,
            headers={"Content-Type": "application/json"},
            verify=True
        )
        
        if response.status_code == 200:
            result = response.json()
            hits = result.get("hits", {}).get("hits", [])
            
            if hits:
                print(f"✓ Found {len(hits)} Filebeat logs in Elasticsearch")
                print("\nSample Filebeat logs:")
                for hit in hits[:3]:  # Show first 3 logs
                    source = hit.get("_source", {})
                    print(f"- Index: {hit.get('_index')}")
                    print(f"  Timestamp: {source.get('@timestamp')}")
                    print(f"  Input Type: {source.get('input', {}).get('type')}")
                    print(f"  Message: {source.get('message')}")
                    print()
            else:
                print("✗ No Filebeat logs found in Elasticsearch")
        else:
            print(f"✗ Failed to search Filebeat logs: {response.status_code}")
            print(response.text)
            
        # Search for test agent logs
        print("\nSearching for Test Agent logs:")
        response = requests.post(
            f"{ELASTIC_CLOUD_URL}/test_agent_*/_search",
            auth=HTTPBasicAuth(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
            json=test_agent_query,
            headers={"Content-Type": "application/json"},
            verify=True
        )
        
        if response.status_code == 200:
            result = response.json()
            hits = result.get("hits", {}).get("hits", [])
            
            if hits:
                print(f"✓ Found {len(hits)} Test Agent logs in Elasticsearch")
                print("\nSample Test Agent logs:")
                for hit in hits[:3]:  # Show first 3 logs
                    source = hit.get("_source", {})
                    print(f"- Index: {hit.get('_index')}")
                    print(f"  Timestamp: {source.get('@timestamp')}")
                    print(f"  Agent: {source.get('agent_name')}")
                    print(f"  Event Type: {source.get('event_type')}")
                    print(f"  Severity: {source.get('severity')}")
                    print(f"  Message: {source.get('message')}")
                    print()
            else:
                print("✗ No Test Agent logs found in Elasticsearch")
        else:
            print(f"✗ Failed to search Test Agent logs: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error searching logs: {e}")

def main():
    """Main function."""
    print("=== Checking Elastic Cloud Logs ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Elasticsearch URL: {ELASTIC_CLOUD_URL}")
    
    check_indices()
    check_filebeat_indices()
    check_test_agent_indices()
    search_logs()
    
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    main()
