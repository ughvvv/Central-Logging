#!/usr/bin/env python3
"""
Test Script for Enhanced Logging Features

This script demonstrates and validates the enhanced features of the
central logging utility (`logger_util.py`), including:
- Dynamic log levels via the LOG_LEVEL environment variable.
- Automatic exception info capture for ERROR/CRITICAL levels.
- Correlation ID logging.
"""

import logging
import uuid
import os
import sys

# Ensure logger_util is importable (adjust path if necessary)
try:
    from logger_util import setup_logger, log
except ImportError:
    print("Error: Could not import logger_util. Make sure it's in the Python path.")
    sys.exit(1)

# --- Test Configuration ---
AGENT_NAME = "logging_test_script"

# --- Setup Logger ---
# The log level is determined by the LOG_LEVEL environment variable
# Default is INFO if LOG_LEVEL is not set or invalid
logger = setup_logger(name=f"{AGENT_NAME}_logger")

print(f"--- Logger Setup Complete ---")
print(f"Logger Name: {logger.name}")
print(f"Effective Log Level: {logging.getLevelName(logger.getEffectiveLevel())}")
print(f"To change the log level, set the LOG_LEVEL environment variable")
print(f"(e.g., export LOG_LEVEL=DEBUG) before running this script.")
print("-" * 30)

# --- Test Functions ---

def test_log_levels():
    """Log messages at various levels."""
    print("\n--- Testing Log Levels ---")
    correlation_id = str(uuid.uuid4())
    log(logger, "DEBUG", "This is a DEBUG message.", AGENT_NAME, "debug_test", correlation_id=correlation_id)
    log(logger, "INFO", "This is an INFO message.", AGENT_NAME, "info_test", correlation_id=correlation_id)
    log(logger, "WARNING", "This is a WARNING message.", AGENT_NAME, "warning_test", correlation_id=correlation_id)
    log(logger, "ERROR", "This is an ERROR message (without exception).", AGENT_NAME, "error_test_no_exc", correlation_id=correlation_id)
    log(logger, "CRITICAL", "This is a CRITICAL message (without exception).", AGENT_NAME, "critical_test_no_exc", correlation_id=correlation_id)
    print("Check console output. Only messages at or above the set LOG_LEVEL should appear.")
    print("-" * 30)

def test_correlation_id():
    """Log messages with and without correlation IDs."""
    print("\n--- Testing Correlation ID ---")
    task_id_1 = str(uuid.uuid4())
    task_id_2 = str(uuid.uuid4())

    log(logger, "INFO", "Starting task 1", AGENT_NAME, "task_start", metadata={"task_id": task_id_1}, correlation_id=task_id_1)
    log(logger, "INFO", "Processing step A for task 1", AGENT_NAME, "task_step_a", metadata={"task_id": task_id_1}, correlation_id=task_id_1)
    log(logger, "INFO", "Starting task 2", AGENT_NAME, "task_start", metadata={"task_id": task_id_2}, correlation_id=task_id_2)
    log(logger, "INFO", "Processing step B for task 1", AGENT_NAME, "task_step_b", metadata={"task_id": task_id_1}, correlation_id=task_id_1)
    log(logger, "INFO", "Processing step A for task 2", AGENT_NAME, "task_step_a", metadata={"task_id": task_id_2}, correlation_id=task_id_2)
    log(logger, "INFO", "Task 1 finished", AGENT_NAME, "task_end", metadata={"task_id": task_id_1}, correlation_id=task_id_1)
    log(logger, "INFO", "Task 2 finished", AGENT_NAME, "task_end", metadata={"task_id": task_id_2}, correlation_id=task_id_2)
    log(logger, "INFO", "General system event (no specific task correlation)", AGENT_NAME, "system_event") # No correlation_id passed

    print(f"Check log output (or Kibana if shipping logs).")
    print(f"Logs for task 1 should have correlation_id: {task_id_1}")
    print(f"Logs for task 2 should have correlation_id: {task_id_2}")
    print(f"The 'system_event' log should not have a correlation_id in metadata.")
    print("-" * 30)

def test_exception_logging():
    """Test automatic exception info capture."""
    print("\n--- Testing Exception Logging ---")
    correlation_id = str(uuid.uuid4())
    try:
        # Simulate an error
        x = 1 / 0
    except ZeroDivisionError as e:
        log(
            logger,
            "ERROR",
            f"Caught a ZeroDivisionError: {e}",
            AGENT_NAME,
            "zero_division_test",
            metadata={"details": "Attempted division by zero"},
            correlation_id=correlation_id
        ) # Exception info should be automatically included

    try:
        # Simulate another error
        my_dict = {"key": "value"}
        val = my_dict["non_existent_key"]
    except KeyError as e:
        # Logging at WARNING level - should NOT include exception info automatically
        log(
            logger,
            "WARNING",
            f"Caught a KeyError but logging as WARNING: {e}",
            AGENT_NAME,
            "key_error_warning_test",
            metadata={"details": "Accessed non-existent key"},
            correlation_id=correlation_id
        )
        # Logging at ERROR level - SHOULD include exception info automatically
        log(
            logger,
            "ERROR",
            f"Caught a KeyError and logging as ERROR: {e}",
            AGENT_NAME,
            "key_error_error_test",
            metadata={"details": "Accessed non-existent key"},
            correlation_id=correlation_id
        )

    print("Check log output (or Kibana).")
    print("ERROR/CRITICAL logs generated within the 'except' blocks should contain 'metadata.exception' field with traceback.")
    print("The WARNING log for KeyError should NOT contain 'metadata.exception'.")
    print("-" * 30)

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Starting logging feature tests for agent: {AGENT_NAME}")

    test_log_levels()
    test_correlation_id()
    test_exception_logging()

    print("\n--- Testing Complete ---")
    print("Review the JSON log output above (or in Kibana if shipping logs).")
    print("Verify that log levels, correlation IDs, and exception details appear as expected based on the LOG_LEVEL setting.")
