#!/usr/bin/env python3
"""
Local Validation Script for Logging and Metrics Components

This script tests the Python components of the infrastructure:
1. Validates the logger_util.py functionality
2. Validates the metrics.py functionality
3. Checks that the orchestrator.py and test_agent.py files are valid Python

This script does not require Docker or external services.
"""

import os
import sys
import importlib.util
import json
import time
import random
import uuid
from datetime import datetime

def print_header(message):
    """Print a header message."""
    print("\n" + "=" * 80)
    print(message)
    print("=" * 80)

def print_success(message):
    """Print a success message."""
    print("✓ " + message)

def print_error(message):
    """Print an error message."""
    print("✗ " + message)

def validate_file_exists(file_path):
    """Validate that a file exists."""
    if os.path.isfile(file_path):
        print_success(f"File exists: {file_path}")
        return True
    else:
        print_error(f"File does not exist: {file_path}")
        return False

def import_module(file_path, module_name):
    """Import a module from a file path."""
    if not validate_file_exists(file_path):
        return None
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print_success(f"Successfully imported {module_name} from {file_path}")
        return module
    except Exception as e:
        print_error(f"Failed to import {module_name} from {file_path}: {e}")
        return None

def validate_logger_util():
    """Validate the logger_util.py functionality."""
    print_header("Validating logger_util.py")
    
    # Import the logger_util module
    logger_util = import_module("logger_util.py", "logger_util")
    if not logger_util:
        return False
    
    try:
        # Set up a logger
        logger = logger_util.setup_logger(name="validation_logger")
        print_success("Successfully set up logger")
        
        # Log a message
        log_message = f"Test log message at {datetime.now().isoformat()}"
        logger_util.log(
            logger,
            "INFO",
            log_message,
            "validation_script",
            "test_event",
            {
                "test_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat()
            }
        )
        print_success(f"Successfully logged message: {log_message}")
        
        # Log messages at different severity levels
        for severity in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logger_util.log(
                logger,
                severity,
                f"Test {severity} message",
                "validation_script",
                f"{severity.lower()}_event",
                {
                    "severity": severity
                }
            )
            print_success(f"Successfully logged {severity} message")
        
        return True
    except Exception as e:
        print_error(f"Error validating logger_util.py: {e}")
        return False

def validate_metrics():
    """Validate the metrics.py functionality."""
    print_header("Validating metrics.py")
    
    # Import the metrics module
    metrics = import_module("metrics.py", "metrics")
    if not metrics:
        return False
    
    try:
        # Start the metrics server in a separate thread
        metrics.start_metrics_server(port=8000)
        print_success("Successfully started metrics server on port 8000")
        
        # Increment tasks_dispatched
        metrics.increment_tasks_dispatched(task_type="test_task")
        print_success("Successfully incremented tasks_dispatched metric")
        
        # Increment errors_encountered
        metrics.increment_errors(error_type="test_error")
        print_success("Successfully incremented errors_encountered metric")
        
        # Increment and decrement active_tasks
        metrics.increment_active_tasks(agent_type="test_agent")
        print_success("Successfully incremented active_tasks metric")
        metrics.decrement_active_tasks(agent_type="test_agent")
        print_success("Successfully decremented active_tasks metric")
        
        # Test TaskTimer
        with metrics.TaskTimer(task_type="test_task"):
            time.sleep(0.1)
        print_success("Successfully used TaskTimer")
        
        # Try to access the metrics endpoint
        try:
            import requests
            response = requests.get("http://localhost:8000/metrics")
            if response.status_code == 200:
                print_success("Successfully accessed metrics endpoint")
                # Print a sample of the metrics
                metrics_sample = response.text.split("\n")[:10]
                print("Sample metrics:")
                for line in metrics_sample:
                    if line and not line.startswith("#"):
                        print(f"  {line}")
            else:
                print_error(f"Failed to access metrics endpoint: {response.status_code}")
        except Exception as e:
            print_error(f"Error accessing metrics endpoint: {e}")
        
        return True
    except Exception as e:
        print_error(f"Error validating metrics.py: {e}")
        return False

def validate_python_file(file_path):
    """Validate that a file is valid Python."""
    print_header(f"Validating {file_path}")
    
    if not validate_file_exists(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Try to compile the code
        compile(code, file_path, 'exec')
        print_success(f"Successfully compiled {file_path}")
        return True
    except SyntaxError as e:
        print_error(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print_error(f"Error validating {file_path}: {e}")
        return False

def main():
    """Main function."""
    print_header("Starting Local Validation")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("This script validates the Python components of the infrastructure without requiring Docker.")
    
    # Validate logger_util.py
    logger_util_valid = validate_logger_util()
    
    # Validate metrics.py
    metrics_valid = validate_metrics()
    
    # Validate orchestrator.py
    orchestrator_valid = validate_python_file("orchestrator.py")
    
    # Validate test_agent.py
    test_agent_valid = validate_python_file("test_agent.py")
    
    # Print summary
    print_header("Validation Summary")
    print(f"logger_util.py: {'✓' if logger_util_valid else '✗'}")
    print(f"metrics.py: {'✓' if metrics_valid else '✗'}")
    print(f"orchestrator.py: {'✓' if orchestrator_valid else '✗'}")
    print(f"test_agent.py: {'✓' if test_agent_valid else '✗'}")
    
    if logger_util_valid and metrics_valid and orchestrator_valid and test_agent_valid:
        print("\nAll Python components are valid!")
        print("\nNote: This validation does not test the Docker-based components (Elasticsearch, Kibana, Prometheus, Grafana, PostgreSQL).")
        print("To test those components, you need to install Docker and Docker Compose, then run ./run_validation.sh")
        return 0
    else:
        print("\nSome components failed validation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
