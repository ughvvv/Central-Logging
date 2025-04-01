#!/usr/bin/env python3
"""
Validation Script for Logging, Monitoring, and Error Handling Infrastructure

This script tests the various components of the infrastructure:
1. Generates logs of different severity levels
2. Produces metrics
3. Simulates errors to test error handling
4. Verifies database connectivity
"""

import time
import random
import uuid
import sys
import json
import requests
import psycopg2
from datetime import datetime

from logger_util import setup_logger, log
from metrics import (
    start_metrics_server,
    increment_tasks_dispatched,
    increment_errors,
    increment_active_tasks,
    decrement_active_tasks,
    TaskTimer
)

# Set up logger
logger = setup_logger(name="validation_script")

# Define test agent types
TEST_AGENT_TYPES = [
    "research_agent",
    "writing_agent",
    "editing_agent",
    "fact_checking_agent"
]

# Define test task types
TEST_TASK_TYPES = [
    "research",
    "content_generation",
    "editing",
    "fact_checking"
]

def generate_test_task():
    """Generate a sample task for testing."""
    task_type = random.choice(TEST_TASK_TYPES)
    
    return {
        "task_id": str(uuid.uuid4()),
        "task_type": task_type,
        "priority": random.choice(["low", "medium", "high"]),
        "created_at": time.time(),
        "data": {
            "topic": random.choice([
                "Artificial Intelligence",
                "Climate Change",
                "Space Exploration",
                "Quantum Computing"
            ]),
            "complexity": random.randint(1, 5)
        }
    }

def test_logging():
    """Test logging at different severity levels with different event types."""
    print("\n=== Testing Logging ===")
    
    # Log system startup
    log(
        logger,
        "INFO",
        "Validation script starting up",
        "validation_script",
        "system_startup",
        {
            "version": "0.1.0",
            "environment": "testing"
        }
    )
    print("✓ Generated system_startup log (INFO)")
    
    # Log at different severity levels
    log(
        logger,
        "DEBUG",
        "This is a debug message",
        "validation_script",
        "debug_event",
        {
            "detail": "Testing debug level"
        }
    )
    print("✓ Generated debug_event log (DEBUG)")
    
    log(
        logger,
        "INFO",
        "This is an info message",
        "validation_script",
        "info_event",
        {
            "detail": "Testing info level"
        }
    )
    print("✓ Generated info_event log (INFO)")
    
    log(
        logger,
        "WARNING",
        "This is a warning message",
        "validation_script",
        "warning_event",
        {
            "detail": "Testing warning level"
        }
    )
    print("✓ Generated warning_event log (WARNING)")
    
    log(
        logger,
        "ERROR",
        "This is an error message",
        "validation_script",
        "error_event",
        {
            "detail": "Testing error level"
        }
    )
    print("✓ Generated error_event log (ERROR)")
    
    log(
        logger,
        "CRITICAL",
        "This is a critical message",
        "validation_script",
        "critical_event",
        {
            "detail": "Testing critical level"
        }
    )
    print("✓ Generated critical_event log (CRITICAL)")
    
    # Log task lifecycle events
    task = generate_test_task()
    agent_type = random.choice(TEST_AGENT_TYPES)
    
    log(
        logger,
        "INFO",
        f"Received task {task['task_id']}",
        "validation_script",
        "task_received",
        {
            "task_id": task["task_id"],
            "task_type": task["task_type"]
        }
    )
    print(f"✓ Generated task_received log for task {task['task_id']}")
    
    log(
        logger,
        "INFO",
        f"Dispatching task {task['task_id']} to {agent_type}",
        "validation_script",
        "task_dispatch",
        {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "agent_type": agent_type,
            "priority": task["priority"]
        }
    )
    print(f"✓ Generated task_dispatch log for task {task['task_id']}")
    
    log(
        logger,
        "INFO",
        f"Task in progress {task['task_id']} by {agent_type}",
        "validation_script",
        "task_in_progress",
        {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "agent_type": agent_type
        }
    )
    print(f"✓ Generated task_in_progress log for task {task['task_id']}")
    
    log(
        logger,
        "INFO",
        f"Task {task['task_id']} completed by {agent_type}",
        "validation_script",
        "task_completed",
        {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "agent_type": agent_type
        }
    )
    print(f"✓ Generated task_completed log for task {task['task_id']}")
    
    print("Logging test completed. Check Kibana to verify logs.")

def test_metrics():
    """Test metrics generation and collection."""
    print("\n=== Testing Metrics ===")
    
    # Start metrics server
    start_metrics_server(port=8000)
    print("✓ Started metrics server on port 8000")
    
    # Generate tasks_dispatched metrics
    for task_type in TEST_TASK_TYPES:
        for _ in range(random.randint(1, 5)):
            increment_tasks_dispatched(task_type=task_type)
            print(f"✓ Incremented tasks_dispatched for {task_type}")
    
    # Generate errors_encountered metrics
    error_types = ["transient", "permanent", "validation", "timeout", "unexpected"]
    for error_type in error_types:
        for _ in range(random.randint(0, 3)):
            increment_errors(error_type=error_type)
            print(f"✓ Incremented errors_encountered for {error_type}")
    
    # Test active_tasks gauge
    for agent_type in TEST_AGENT_TYPES:
        active_count = random.randint(1, 3)
        for _ in range(active_count):
            increment_active_tasks(agent_type=agent_type)
            print(f"✓ Incremented active_tasks for {agent_type}")
        
        # Simulate some work
        time.sleep(2)
        
        for _ in range(active_count):
            decrement_active_tasks(agent_type=agent_type)
            print(f"✓ Decremented active_tasks for {agent_type}")
    
    # Test task latency
    for task_type in TEST_TASK_TYPES:
        with TaskTimer(task_type=task_type):
            # Simulate task execution
            time.sleep(random.uniform(0.1, 1.0))
            print(f"✓ Recorded task_latency for {task_type}")
    
    print("Metrics test completed. Check Prometheus/Grafana to verify metrics.")
    
    # Verify metrics endpoint
    try:
        response = requests.get("http://localhost:8000/metrics")
        if response.status_code == 200:
            print("✓ Metrics endpoint is accessible")
            # Print a sample of the metrics
            metrics_sample = response.text.split("\n")[:10]
            print("Sample metrics:")
            for line in metrics_sample:
                if line and not line.startswith("#"):
                    print(f"  {line}")
        else:
            print(f"✗ Failed to access metrics endpoint: {response.status_code}")
    except Exception as e:
        print(f"✗ Error accessing metrics endpoint: {e}")

def test_error_handling():
    """Test error handling and retry logic."""
    print("\n=== Testing Error Handling ===")
    
    class TransientError(Exception):
        """Error that can be retried."""
        pass
    
    class PermanentError(Exception):
        """Error that cannot be retried."""
        pass
    
    def process_with_retry(task, max_retries=3):
        """Process a task with retry logic for transient errors."""
        retries = 0
        
        while retries <= max_retries:
            try:
                # Simulate an operation that might fail
                if random.random() < 0.7:  # 70% chance of transient error on first try
                    raise TransientError("Simulated transient error")
                
                # If we get here, the operation succeeded
                log(
                    logger,
                    "INFO",
                    f"Task {task['task_id']} processed successfully",
                    "validation_script",
                    "task_success",
                    {
                        "task_id": task["task_id"],
                        "retries": retries
                    }
                )
                print(f"✓ Task {task['task_id']} processed successfully after {retries} retries")
                return True
            
            except TransientError as e:
                retries += 1
                increment_errors("transient")
                
                # Log retry attempt
                log(
                    logger,
                    "WARNING",
                    f"Transient error, retrying ({retries}/{max_retries})",
                    "validation_script",
                    "transient_error_retry",
                    {
                        "task_id": task["task_id"],
                        "error": str(e),
                        "retry_count": retries,
                        "max_retries": max_retries
                    }
                )
                print(f"✓ Logged transient error for task {task['task_id']}, retry {retries}/{max_retries}")
                
                # Exponential backoff with maximum limit
                if retries <= max_retries:
                    backoff_time = 0.5 * (2 ** retries)
                    if backoff_time > 10:
                        backoff_time = 10
                    print(f"  Backing off for {backoff_time:.2f} seconds")
                    time.sleep(backoff_time)
                else:
                    # Log max retries exceeded
                    log(
                        logger,
                        "ERROR",
                        f"Max retries exceeded for task {task['task_id']}",
                        "validation_script",
                        "max_retries_exceeded",
                        {
                            "task_id": task["task_id"],
                            "error": str(e),
                            "retry_count": retries,
                            "max_retries": max_retries
                        }
                    )
                    print(f"✓ Logged max retries exceeded for task {task['task_id']}")
                    return False
    
    # Test retry logic with a few tasks
    for i in range(3):
        task = generate_test_task()
        process_with_retry(task)
    
    # Test permanent error
    task = generate_test_task()
    try:
        raise PermanentError("Simulated permanent error")
    except PermanentError as e:
        increment_errors("permanent")
        log(
            logger,
            "ERROR",
            f"Permanent error for task {task['task_id']}",
            "validation_script",
            "permanent_error",
            {
                "task_id": task["task_id"],
                "error": str(e)
            }
        )
        print(f"✓ Logged permanent error for task {task['task_id']}")
    
    # Test unexpected error
    task = generate_test_task()
    try:
        # Simulate an unexpected error
        raise ValueError("Simulated unexpected error")
    except Exception as e:
        increment_errors("unexpected")
        log(
            logger,
            "CRITICAL",
            f"Unexpected error for task {task['task_id']}",
            "validation_script",
            "error",
            {
                "task_id": task["task_id"],
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        print(f"✓ Logged unexpected error for task {task['task_id']}")
    
    print("Error handling test completed. Check Kibana for error logs.")

def test_database():
    """Test database connectivity and operations."""
    print("\n=== Testing Database Connectivity ===")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="orchestrator_db",
            user="orchestrator_admin",
            password="orchestrator_password"
        )
        print("✓ Connected to PostgreSQL database")
        
        # Create a cursor
        cur = conn.cursor()
        
        # Test querying system_config
        cur.execute("SELECT config_key, config_value FROM system_config")
        configs = cur.fetchall()
        print(f"✓ Retrieved {len(configs)} system configurations")
        for config in configs:
            print(f"  - {config[0]}: {config[1]}")
        
        # Test querying agents
        cur.execute("SELECT agent_name, agent_type, status FROM agents")
        agents = cur.fetchall()
        print(f"✓ Retrieved {len(agents)} agents")
        for agent in agents:
            print(f"  - {agent[0]} ({agent[1]}): {agent[2]}")
        
        # Test inserting a task
        task = generate_test_task()
        agent_type = random.choice(TEST_AGENT_TYPES)
        
        cur.execute(
            """
            INSERT INTO task_states 
            (task_id, task_type, agent_name, state, priority, created_at, updated_at, metadata)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s)
            """,
            (
                task["task_id"], 
                task["task_type"], 
                agent_type, 
                "in_progress", 
                task["priority"], 
                json.dumps(task["data"])
            )
        )
        conn.commit()
        print(f"✓ Inserted task {task['task_id']} into task_states")
        
        # Test updating a task
        cur.execute(
            """
            UPDATE task_states 
            SET state = %s, completed_at = NOW(), updated_at = NOW() 
            WHERE task_id = %s
            """,
            ("completed", task["task_id"])
        )
        conn.commit()
        print(f"✓ Updated task {task['task_id']} to completed state")
        
        # Test inserting into task_history
        cur.execute(
            """
            INSERT INTO task_history 
            (task_id, task_type, agent_name, state, priority, created_at, completed_at, 
             duration_ms, success, error_type, error_message, metadata)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s, %s, %s)
            """,
            (
                task["task_id"], 
                task["task_type"], 
                agent_type, 
                "completed", 
                task["priority"], 
                random.randint(100, 5000),  # duration_ms
                True,  # success
                None,  # error_type
                None,  # error_message
                json.dumps(task["data"])  # metadata
            )
        )
        conn.commit()
        print(f"✓ Inserted task {task['task_id']} into task_history")
        
        # Close the connection
        cur.close()
        conn.close()
        print("✓ Closed database connection")
        
    except Exception as e:
        print(f"✗ Database error: {e}")
    
    print("Database test completed.")

def verify_elasticsearch():
    """Verify Elasticsearch is running and accessible."""
    print("\n=== Verifying Elasticsearch ===")
    
    try:
        response = requests.get("http://localhost:9200")
        if response.status_code == 200:
            print("✓ Elasticsearch is running")
            print(f"  Version: {response.json().get('version', {}).get('number', 'unknown')}")
        else:
            print(f"✗ Failed to connect to Elasticsearch: {response.status_code}")
    except Exception as e:
        print(f"✗ Error connecting to Elasticsearch: {e}")

def verify_kibana():
    """Verify Kibana is running and accessible."""
    print("\n=== Verifying Kibana ===")
    
    try:
        response = requests.get("http://localhost:5601/api/status")
        if response.status_code == 200:
            print("✓ Kibana is running")
            status = response.json()
            print(f"  Status: {status.get('status', {}).get('overall', {}).get('level', 'unknown')}")
        else:
            print(f"✗ Failed to connect to Kibana: {response.status_code}")
    except Exception as e:
        print(f"✗ Error connecting to Kibana: {e}")

def verify_prometheus():
    """Verify Prometheus is running and accessible."""
    print("\n=== Verifying Prometheus ===")
    
    try:
        response = requests.get("http://localhost:9090/-/healthy")
        if response.status_code == 200:
            print("✓ Prometheus is running")
        else:
            print(f"✗ Failed to connect to Prometheus: {response.status_code}")
    except Exception as e:
        print(f"✗ Error connecting to Prometheus: {e}")

def verify_grafana():
    """Verify Grafana is running and accessible."""
    print("\n=== Verifying Grafana ===")
    
    try:
        response = requests.get("http://localhost:3000/api/health")
        if response.status_code == 200:
            print("✓ Grafana is running")
            status = response.json()
            print(f"  Status: {status.get('database', 'unknown')}")
        else:
            print(f"✗ Failed to connect to Grafana: {response.status_code}")
    except Exception as e:
        print(f"✗ Error connecting to Grafana: {e}")

def main():
    """Main function to run all validation tests."""
    print("=== Starting Infrastructure Validation ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Verify services are running
    verify_elasticsearch()
    verify_kibana()
    verify_prometheus()
    verify_grafana()
    
    # Run tests
    test_logging()
    test_metrics()
    test_error_handling()
    test_database()
    
    print("\n=== Validation Complete ===")
    print("Next steps:")
    print("1. Check Kibana (http://localhost:5601) to verify logs are being indexed correctly")
    print("2. Check Prometheus (http://localhost:9090) to verify metrics are being collected")
    print("3. Check Grafana (http://localhost:3000) to verify dashboards are displaying metrics")
    print("4. Check PostgreSQL to verify database operations were successful")

if __name__ == "__main__":
    main()
