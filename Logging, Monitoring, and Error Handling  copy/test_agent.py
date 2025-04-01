#!/usr/bin/env python3
"""
Test Agent

This is a simple test agent that demonstrates how to integrate with the
central logging, monitoring, and error handling infrastructure.
"""

import time
import random
import uuid
import sys
import json
import psycopg2
from datetime import datetime

# Import setup_logger and log from logger_util
from logger_util import setup_logger, log
from metrics import (
    start_metrics_server,
    increment_tasks_dispatched,
    increment_errors,
    increment_active_tasks,
    decrement_active_tasks,
    TaskTimer
)

# Custom exceptions
class TransientError(Exception):
    """Error that can be retried."""
    pass

class PermanentError(Exception):
    """Error that cannot be retried."""
    pass

# Set up logger (reads level from LOG_LEVEL env var)
logger = setup_logger(name="test_agent")

# Agent configuration
AGENT_NAME = "test_agent_1"
AGENT_TYPE = "test_agent"
AGENT_PORT = 8001  # Different from orchestrator port (8000)

# Database connection
def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="orchestrator_db",
        user="orchestrator_admin",
        password="orchestrator_password"
    )

def register_agent():
    """Register the agent in the database."""
    correlation_id = str(uuid.uuid4()) # Generate a correlation ID for this operation
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if agent already exists
        cur.execute(
            "SELECT agent_name FROM agents WHERE agent_name = %s",
            (AGENT_NAME,)
        )

        if cur.fetchone() is None:
            # Agent doesn't exist, insert it
            cur.execute(
                """
                INSERT INTO agents
                (agent_name, agent_type, status, last_heartbeat, capabilities, metadata)
                VALUES (%s, %s, %s, NOW(), %s, %s)
                """,
                (
                    AGENT_NAME,
                    AGENT_TYPE,
                    "active",
                    json.dumps({"skills": ["test_skill_1", "test_skill_2"]}),
                    json.dumps({"version": "1.0.0"})
                )
            )
            conn.commit()
            log(
                logger,
                "INFO",
                f"Agent {AGENT_NAME} registered",
                AGENT_NAME,
                "agent_registered",
                {"agent_type": AGENT_TYPE},
                correlation_id=correlation_id
            )
        else:
            # Agent exists, update heartbeat
            cur.execute(
                """
                UPDATE agents
                SET last_heartbeat = NOW(), status = 'active'
                WHERE agent_name = %s
                """,
                (AGENT_NAME,)
            )
            conn.commit()
            log(
                logger,
                "INFO",
                f"Agent {AGENT_NAME} heartbeat updated",
                AGENT_NAME,
                "agent_heartbeat",
                {"agent_type": AGENT_TYPE},
                correlation_id=correlation_id
            )

        cur.close()
        conn.close()
        return True
    except Exception as e:
        log(
            logger,
            "ERROR",
            f"Failed to register agent: {e}",
            AGENT_NAME,
            "agent_registration_failed",
            {"error": str(e), "error_type": type(e).__name__},
            correlation_id=correlation_id
        ) # Log function now handles exc_info automatically
        return False

def update_heartbeat():
    """Update the agent's heartbeat in the database."""
    correlation_id = str(uuid.uuid4()) # Generate a correlation ID for this operation
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE agents
            SET last_heartbeat = NOW()
            WHERE agent_name = %s
            """,
            (AGENT_NAME,)
        )
        conn.commit()

        cur.close()
        conn.close()
        # Optionally log heartbeat success if needed
        # log(logger, "DEBUG", "Heartbeat updated", AGENT_NAME, "heartbeat_success", correlation_id=correlation_id)
        return True
    except Exception as e:
        log(
            logger,
            "WARNING", # Changed to WARNING as it might not be critical
            f"Failed to update heartbeat: {e}",
            AGENT_NAME,
            "heartbeat_failed",
            {"error": str(e)},
            correlation_id=correlation_id
        ) # Log function now handles exc_info automatically for ERROR/CRITICAL
        return False

def get_pending_tasks():
    """Get pending tasks from the database."""
    correlation_id = str(uuid.uuid4()) # Generate a correlation ID for this operation
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT task_id, task_type, priority, metadata
            FROM task_states
            WHERE state = 'queued' AND agent_name IS NULL
            LIMIT 5
            """
        )

        tasks = []
        for row in cur.fetchall():
            tasks.append({
                "task_id": row[0],
                "task_type": row[1],
                "priority": row[2],
                "metadata": row[3]
            })

        cur.close()
        conn.close()
        return tasks
    except Exception as e:
        log(
            logger,
            "ERROR",
            f"Failed to get pending tasks: {e}",
            AGENT_NAME,
            "get_tasks_failed",
            {"error": str(e)},
            correlation_id=correlation_id
        ) # Log function now handles exc_info automatically
        return []

def claim_task(task_id):
    """Claim a task for processing."""
    correlation_id = task_id # Use task_id as correlation_id
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE task_states
            SET agent_name = %s, state = 'in_progress', updated_at = NOW()
            WHERE task_id = %s AND (agent_name IS NULL OR agent_name = %s)
            RETURNING task_type, priority, metadata
            """,
            (AGENT_NAME, task_id, AGENT_NAME)
        )

        result = cur.fetchone()
        conn.commit()

        cur.close()
        conn.close()

        if result:
            task_type, priority, metadata = result
            log(
                logger,
                "INFO",
                f"Task {task_id} claimed",
                AGENT_NAME,
                "task_claimed",
                {"task_id": task_id, "task_type": task_type, "priority": priority},
                correlation_id=correlation_id
            )
            return {
                "task_id": task_id,
                "task_type": task_type,
                "priority": priority,
                "metadata": metadata
            }
        else:
            # Log if task was already claimed by another agent (optional, could be noisy)
            # log(logger, "DEBUG", f"Task {task_id} already claimed or does not exist", AGENT_NAME, "claim_task_skipped", correlation_id=correlation_id)
            return None
    except Exception as e:
        log(
            logger,
            "ERROR",
            f"Failed to claim task {task_id}: {e}",
            AGENT_NAME,
            "claim_task_failed",
            {"task_id": task_id, "error": str(e)},
            correlation_id=correlation_id
        ) # Log function now handles exc_info automatically
        return None

def complete_task(task, success, error_type=None, error_message=None):
    """Mark a task as completed or failed."""
    correlation_id = task['task_id'] # Use task_id as correlation_id
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Update task state
        cur.execute(
            """
            UPDATE task_states
            SET state = %s, completed_at = NOW(), updated_at = NOW()
            WHERE task_id = %s
            RETURNING created_at
            """,
            ("completed" if success else "failed", task["task_id"])
        )

        result = cur.fetchone()
        if result:
            created_at = result[0]

            # Calculate duration
            cur.execute("SELECT EXTRACT(EPOCH FROM (NOW() - %s)) * 1000", (created_at,))
            duration_ms = int(cur.fetchone()[0])

            # Insert into task history
            cur.execute(
                """
                INSERT INTO task_history
                (task_id, task_type, agent_name, state, priority, created_at,
                completed_at, duration_ms, success, error_type, error_message, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s)
                """,
                (
                    task["task_id"],
                    task["task_type"],
                    AGENT_NAME,
                    "completed" if success else "failed",
                    task["priority"],
                    created_at,
                    duration_ms,
                    success,
                    error_type,
                    error_message,
                    json.dumps(task["metadata"]) if isinstance(task["metadata"], dict) else task["metadata"]
                )
            )

            conn.commit()

            log(
                logger,
                "INFO" if success else "ERROR",
                f"Task {task['task_id']} {'completed' if success else 'failed'}",
                AGENT_NAME,
                "task_completed" if success else "task_failed",
                {
                    "task_id": task["task_id"],
                    "task_type": task["task_type"],
                    "duration_ms": duration_ms,
                    "error_type": error_type,
                    "error_message": error_message
                },
                correlation_id=correlation_id
            ) # Log function now handles exc_info automatically for ERROR

        cur.close()
        conn.close()
        return True
    except Exception as e:
        log(
            logger,
            "ERROR",
            f"Failed to complete task {task['task_id']}: {e}",
            AGENT_NAME,
            "complete_task_failed",
            {"task_id": task["task_id"], "error": str(e)},
            correlation_id=correlation_id
        ) # Log function now handles exc_info automatically
        return False

def process_task(task):
    """Process a task with retry logic."""
    correlation_id = task['task_id'] # Use task_id as correlation_id
    max_retries = 3
    retries = 0

    # Increment active tasks
    increment_active_tasks(agent_type=AGENT_TYPE)

    try:
        # Log task processing start
        log(
            logger,
            "INFO",
            f"Processing task {task['task_id']}",
            AGENT_NAME,
            "task_processing",
            {"task_id": task["task_id"], "task_type": task["task_type"]},
            correlation_id=correlation_id
        )

        # Increment task counter
        increment_tasks_dispatched(task_type=task["task_type"])

        while retries <= max_retries:
            try:
                # Simulate task processing with potential failures
                with TaskTimer(task_type=task["task_type"]):
                    # 20% chance of transient error
                    if random.random() < 0.2:
                        raise TransientError("Simulated transient error")

                    # 10% chance of permanent error
                    if random.random() < 0.1:
                        raise PermanentError("Simulated permanent error")

                    # Simulate actual work
                    time.sleep(random.uniform(0.5, 2.0))

                    # Task completed successfully
                    complete_task(task, True)
                    return True

            except TransientError as e:
                retries += 1
                increment_errors(error_type="transient")

                # Log retry attempt
                log(
                    logger,
                    "WARNING",
                    f"Transient error, retrying ({retries}/{max_retries})",
                    AGENT_NAME,
                    "transient_error_retry",
                    {
                        "task_id": task["task_id"],
                        "error": str(e),
                        "retry_count": retries,
                        "max_retries": max_retries
                    },
                    correlation_id=correlation_id
                ) # Log function now handles exc_info automatically for ERROR/CRITICAL

                # Exponential backoff with maximum limit
                if retries <= max_retries:
                    backoff_time = 0.5 * (2 ** retries)
                    if backoff_time > 10:
                        backoff_time = 10
                    time.sleep(backoff_time)
                else:
                    # Log max retries exceeded
                    log(
                        logger,
                        "ERROR", # Log as ERROR since max retries exceeded
                        f"Max retries exceeded for task {task['task_id']}: {str(e)}",
                        AGENT_NAME,
                        "max_retries_exceeded", # Standardized event type
                        {
                            "task_id": task["task_id"],
                            "error": str(e),
                            "error_type": "transient" # Indicate original error type
                        },
                        correlation_id=correlation_id
                    ) # Log function now handles exc_info automatically
                    complete_task(
                        task,
                        False,
                        "transient", # Keep original error type for history
                        f"Max retries exceeded: {str(e)}"
                    )
                    return False

            except PermanentError as e:
                # Log permanent error
                increment_errors(error_type="permanent")
                log(
                    logger,
                    "ERROR",
                    f"Permanent error processing task {task['task_id']}: {str(e)}",
                    AGENT_NAME,
                    "permanent_error", # Standardized event type
                    {
                        "task_id": task["task_id"],
                        "error": str(e),
                        "error_type": "permanent"
                    },
                    correlation_id=correlation_id
                ) # Log function now handles exc_info automatically
                complete_task(
                    task,
                    False,
                    "permanent",
                    str(e)
                )
                return False

            except Exception as e:
                # Log unexpected error
                increment_errors(error_type="unexpected")
                log(
                    logger,
                    "CRITICAL", # Use CRITICAL for unexpected errors
                    f"Unexpected error processing task {task['task_id']}: {str(e)}",
                    AGENT_NAME,
                    "unexpected_error", # Standardized event type
                    {
                        "task_id": task["task_id"],
                        "error": str(e),
                        "error_type": type(e).__name__
                    },
                    correlation_id=correlation_id
                ) # Log function now handles exc_info automatically
                complete_task(
                    task,
                    False,
                    "unexpected",
                    str(e)
                )
                return False

    finally:
        # Always decrement active tasks
        decrement_active_tasks(agent_type=AGENT_TYPE)

def create_test_tasks(num_tasks=5):
    """Create test tasks in the database."""
    correlation_id = str(uuid.uuid4()) # Generate a correlation ID for this batch operation
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        task_types = ["research", "content_generation", "editing", "fact_checking"]
        priorities = ["low", "medium", "high"]

        for i in range(num_tasks):
            task_id = str(uuid.uuid4())
            task_type = random.choice(task_types)
            priority = random.choice(priorities)
            metadata = {
                "topic": random.choice([
                    "Artificial Intelligence",
                    "Climate Change",
                    "Space Exploration",
                    "Quantum Computing"
                ]),
                "complexity": random.randint(1, 5),
                "batch_correlation_id": correlation_id # Include batch ID
            }

            cur.execute(
                """
                INSERT INTO task_states
                (task_id, task_type, state, priority, created_at, updated_at, metadata)
                VALUES (%s, %s, %s, %s, NOW(), NOW(), %s)
                """,
                (
                    task_id,
                    task_type,
                    "queued",
                    priority,
                    json.dumps(metadata)
                )
            )

            log(
                logger,
                "INFO",
                f"Created test task {task_id} ({i+1}/{num_tasks})",
                AGENT_NAME,
                "test_task_created",
                {
                    "task_id": task_id,
                    "task_type": task_type,
                    "priority": priority
                },
                correlation_id=task_id # Use task_id for individual task creation log
            )

        conn.commit()
        cur.close()
        conn.close()
        log(logger, "INFO", f"Finished creating {num_tasks} test tasks.", AGENT_NAME, "test_tasks_batch_created", {"num_tasks": num_tasks}, correlation_id=correlation_id)
        return True
    except Exception as e:
        log(
            logger,
            "ERROR",
            f"Failed to create test tasks: {e}",
            AGENT_NAME,
            "create_test_tasks_failed",
            {"error": str(e)},
            correlation_id=correlation_id
        ) # Log function now handles exc_info automatically
        return False

def main():
    """Main function to run the test agent."""
    startup_correlation_id = str(uuid.uuid4()) # Correlation ID for startup sequence

    # Start metrics server on a different port than the orchestrator
    start_metrics_server(port=AGENT_PORT)

    # Log system startup
    log(
        logger,
        "INFO",
        f"Test agent {AGENT_NAME} starting up",
        AGENT_NAME,
        "system_startup",
        {
            "agent_type": AGENT_TYPE,
            "version": "1.0.0",
            "environment": "development"
        },
        correlation_id=startup_correlation_id
    )

    # Register agent
    if not register_agent(): # register_agent handles its own logging including correlation ID
        log(
            logger,
            "CRITICAL",
            "Failed to register agent, exiting",
            AGENT_NAME,
            "agent_registration_failed_critical", # More specific event type
            {},
            correlation_id=startup_correlation_id
        ) # Log function now handles exc_info automatically
        sys.exit(1)

    # Create some test tasks
    create_test_tasks(5) # create_test_tasks handles its own logging including correlation IDs

    # Main loop
    heartbeat_interval = 60  # seconds
    last_heartbeat = time.time()

    try:
        while True:
            # Update heartbeat periodically
            current_time = time.time()
            if current_time - last_heartbeat >= heartbeat_interval:
                update_heartbeat() # update_heartbeat handles its own logging
                last_heartbeat = current_time

            # Get pending tasks
            tasks = get_pending_tasks() # get_pending_tasks handles its own logging

            if tasks:
                for task_info in tasks:
                    # Claim the task
                    task = claim_task(task_info["task_id"]) # claim_task handles its own logging

                    if task:
                        # Process the task
                        process_task(task) # process_task handles its own logging

            # Sleep before next iteration
            time.sleep(5) # Increased sleep time slightly

    except KeyboardInterrupt:
        shutdown_correlation_id = str(uuid.uuid4()) # Correlation ID for shutdown sequence
        # Log system shutdown
        log(
            logger,
            "INFO",
            f"Test agent {AGENT_NAME} shutting down",
            AGENT_NAME,
            "system_shutdown",
            {},
            correlation_id=shutdown_correlation_id
        )
        sys.exit(0)
    except Exception as e: # Catch unexpected errors in main loop
        shutdown_correlation_id = str(uuid.uuid4())
        log(
            logger,
            "CRITICAL",
            f"Unexpected error in main loop, shutting down: {e}",
            AGENT_NAME,
            "main_loop_unexpected_error",
            {"error": str(e)},
            correlation_id=shutdown_correlation_id
        ) # Log function now handles exc_info automatically
        sys.exit(1)


if __name__ == "__main__":
    main()
