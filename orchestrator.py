#!/usr/bin/env python3
"""
Orchestrator Stub for Multi-Agent System

This is a stub implementation of the orchestrator that demonstrates
the logging, monitoring, and error handling infrastructure.
"""

import time
import random
import uuid
import sys
from logger_util import setup_logger, log
from metrics import (
    start_metrics_server,
    increment_tasks_dispatched,
    increment_errors,
    TaskTimer
)

# Custom exceptions
class TransientError(Exception):
    """Error that can be retried."""
    pass

class PermanentError(Exception):
    """Error that cannot be retried."""
    pass

# Set up logger
logger = setup_logger(name="orchestrator_logger")

# Define agent types (for demonstration)
AGENT_TYPES = [
    "research_agent",
    "writing_agent",
    "editing_agent",
    "fact_checking_agent"
]

def generate_task():
    """
    Generate a sample task for demonstration.
    
    Returns:
        dict: A task object
    """
    task_type = random.choice([
        "research",
        "content_generation",
        "editing",
        "fact_checking"
    ])
    
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

def dispatch_task(task, agent_type):
    """
    Simulate dispatching a task to an agent.
    
    Args:
        task (dict): The task to dispatch
        agent_type (str): The type of agent to dispatch to
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Log task dispatch
    log(
        logger,
        "INFO",
        f"Dispatching task {task['task_id']} to {agent_type}",
        "orchestrator",
        "task_dispatch",
        {
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "agent_type": agent_type,
            "priority": task["priority"]
        }
    )
    
    # Increment metrics
    increment_tasks_dispatched()
    
    # Simulate random failure (1 in 10 chance)
    if random.randint(1, 10) == 1:
        if random.choice([True, False]):
            # Transient error
            raise TransientError(f"Failed to dispatch task {task['task_id']} to {agent_type} (transient)")
        else:
            # Permanent error
            raise PermanentError(f"Failed to dispatch task {task['task_id']} to {agent_type} (permanent)")
    
    # Simulate processing time
    time.sleep(random.uniform(0.1, 0.5))
    
    return True

def process_task_with_retry(task, max_retries=3):
    """
    Process a task with retry logic for transient errors.
    
    Args:
        task (dict): The task to process
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        bool: True if successful, False otherwise
    """
    agent_type = random.choice(AGENT_TYPES)
    retries = 0
    
    while retries <= max_retries:
        try:
            with TaskTimer():
                return dispatch_task(task, agent_type)
        except TransientError as e:
            retries += 1
            increment_errors("transient")
            
            # Log retry attempt
            log(
                logger,
                "WARNING",
                f"Transient error, retrying ({retries}/{max_retries})",
                "orchestrator",
                "transient_error_retry",
                {
                    "task_id": task["task_id"],
                    "error": str(e),
                    "retry_count": retries,
                    "max_retries": max_retries
                }
            )
            
            # Exponential backoff
            if retries <= max_retries:
                backoff_time = 0.5 * (2 ** retries)
                time.sleep(backoff_time)
            else:
                # Log max retries exceeded
                log(
                    logger,
                    "ERROR",
                    f"Max retries exceeded for task {task['task_id']}",
                    "orchestrator",
                    "max_retries_exceeded",
                    {
                        "task_id": task["task_id"],
                        "error": str(e),
                        "retry_count": retries,
                        "max_retries": max_retries
                    }
                )
                return False
        except PermanentError as e:
            # Log permanent error
            increment_errors("permanent")
            log(
                logger,
                "ERROR",
                f"Permanent error for task {task['task_id']}",
                "orchestrator",
                "permanent_error",
                {
                    "task_id": task["task_id"],
                    "error": str(e)
                }
            )
            return False
        except Exception as e:
            # Log unexpected error
            increment_errors("unexpected")
            log(
                logger,
                "CRITICAL",
                f"Unexpected error for task {task['task_id']}",
                "orchestrator",
                "error",
                {
                    "task_id": task["task_id"],
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return False

def main():
    """Main function to run the orchestrator stub."""
    # Start metrics server
    start_metrics_server(port=8000)
    
    # Log system startup
    log(
        logger,
        "INFO",
        "Orchestrator starting up",
        "orchestrator",
        "system_startup",
        {
            "version": "0.1.0",
            "environment": "development"
        }
    )
    
    try:
        # Main loop
        while True:
            # Generate a task
            task = generate_task()
            
            # Process the task
            process_task_with_retry(task)
            
            # Sleep before next iteration
            time.sleep(1)
    except KeyboardInterrupt:
        # Log system shutdown
        log(
            logger,
            "INFO",
            "Orchestrator shutting down",
            "orchestrator",
            "system_shutdown",
            {}
        )
        sys.exit(0)

if __name__ == "__main__":
    main()
