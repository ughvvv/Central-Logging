# Agent Onboarding Guide

This document provides instructions for integrating new agents with the central logging, monitoring, and error handling infrastructure.

## Overview

When developing a new agent for the multi-agent system, you should integrate with:

1. **Logging Infrastructure**: Use the JSON logging utility to emit structured logs
2. **Metrics Infrastructure**: Expose Prometheus metrics for monitoring
3. **Error Handling**: Implement proper error handling with retry logic
4. **Database Integration**: Use the PostgreSQL database for persistent state (optional)

## Logging Integration

### Step 1: Import the Logging Utility

```python
from logger_util import setup_logger, log
```

### Step 2: Set Up a Logger for Your Agent

```python
# Initialize the logger with your agent's name
logger = setup_logger(name="my_agent_logger")
```

### Step 3: Log Events with the Required Fields

```python
# Log an event with correlation ID
task_id = "xyz123" # Example task ID
log(
    logger,
    "INFO",  # Severity level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    "Processing task XYZ",  # Message
    "my_agent_name",  # Agent name
    "task_processing",  # Event type
    metadata={  # Metadata (optional)
        "task_id": task_id,
        "details": "Additional context"
    },
    correlation_id=task_id # Pass correlation ID (often the task_id)
)

# Log an error (exception info is automatically captured for ERROR/CRITICAL)
try:
    # ... operation that might fail ...
    raise ValueError("Something went wrong")
except Exception as e:
    log(
        logger,
        "ERROR",
        f"Failed operation for task {task_id}",
        "my_agent_name",
        "operation_failed",
        metadata={"task_id": task_id},
        correlation_id=task_id
    )
```

### Step 4: Define Standard Event Types

For consistency, use these standard event types when applicable:

- `system_startup`: When your agent starts
- `system_shutdown`: When your agent shuts down
- `task_received`: When a task is received
- `task_processing`: When processing begins
- `task_completed`: When a task is completed
- `error`: When an error occurs

You can also define custom event types specific to your agent's functionality.

## Metrics Integration

### Step 1: Import the Metrics Utility

```python
from metrics import (
    start_metrics_server,
    increment_tasks_dispatched,
    increment_errors,
    increment_active_tasks,
    decrement_active_tasks,
    TaskTimer
)
```

### Step 2: Start the Metrics Server

```python
# Start the metrics server on a unique port
start_metrics_server(port=8001)  # Choose a unique port for your agent
```

### Step 3: Track Metrics in Your Code

```python
# Track task dispatches
increment_tasks_dispatched(task_type="my_task_type")

# Track errors
increment_errors(error_type="validation_error")

# Track active tasks
increment_active_tasks(agent_type="my_agent")
try:
    # Do work
    pass
finally:
    # Always decrement when done
    decrement_active_tasks(agent_type="my_agent")

# Time operations
with TaskTimer(task_type="my_task_type"):
    # Operation to time
    process_task()
```

### Step 4: Define Custom Metrics (Optional)

If you need custom metrics specific to your agent, define them in a separate file:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define custom metrics
my_custom_counter = Counter(
    'my_custom_counter',
    'Description of my custom counter',
    ['label1', 'label2']
)

# Use custom metrics
my_custom_counter.labels(label1="value1", label2="value2").inc()
```

## Error Handling

### Step 1: Define Error Types

```python
class TransientError(Exception):
    """Error that can be retried."""
    pass

class PermanentError(Exception):
    """Error that cannot be retried."""
    pass
```

### Step 2: Implement Retry Logic

```python
def process_with_retry(task, max_retries=3):
    retries = 0
    
    while retries <= max_retries:
        try:
            # Attempt the operation
            return process_task(task)
        except TransientError as e:
            retries += 1
            increment_errors("transient")
            
            # Log retry attempt
            log(
                logger,
                "WARNING",
                f"Transient error, retrying ({retries}/{max_retries})",
                "my_agent",
                "transient_error_retry",
                {
                    "task_id": task["id"],
                    "error": str(e),
                    "retry_count": retries
                }
            )
            
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
                    "ERROR",
                    f"Max retries exceeded",
                    "my_agent",
                    "max_retries_exceeded",
                    {
                        "task_id": task["id"],
                        "error": str(e)
                    }
                )
                return False
        except PermanentError as e:
            # Log permanent error
            increment_errors("permanent")
            log(
                logger,
                "ERROR",
                f"Permanent error",
                "my_agent",
                "permanent_error",
                {
                    "task_id": task["id"],
                    "error": str(e)
                }
            )
            return False
```

## Database Integration (Optional)

If your agent needs to store state or data, use the PostgreSQL database:

### Database Schema

The database includes the following tables:

1. **task_states**: Tracks the current state of tasks in the system
   - `task_id`: Unique identifier for the task
   - `task_type`: Type of task (e.g., research, content_generation)
   - `agent_name`: Name of the agent assigned to the task
   - `state`: Current state (e.g., queued, in_progress, completed)
   - `priority`: Task priority (e.g., low, medium, high)
   - `created_at`: When the task was created
   - `updated_at`: When the task was last updated
   - `completed_at`: When the task was completed (if applicable)
   - `metadata`: Additional task data as JSON

2. **agents**: Registry of available agents and their capabilities
   - `agent_name`: Unique name of the agent
   - `agent_type`: Type of agent (e.g., research_agent, writing_agent)
   - `status`: Current status (e.g., active, inactive)
   - `last_heartbeat`: Timestamp of the last heartbeat
   - `capabilities`: Agent capabilities as JSON
   - `metadata`: Additional agent data as JSON

3. **task_history**: Historical record of completed tasks
   - Similar to task_states but includes execution results
   - `success`: Whether the task was successful
   - `error_type`: Type of error if unsuccessful
   - `error_message`: Error message if unsuccessful
   - `duration_ms`: Task execution duration in milliseconds

4. **system_config**: System-wide configuration settings
   - `config_key`: Configuration key
   - `config_value`: Configuration value as JSON
   - `description`: Description of the configuration
   - `updated_at`: When the configuration was last updated

### Connecting to the Database

```python
import psycopg2
import json

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="orchestrator_db",
    user="orchestrator_admin",
    password="orchestrator_password"
)

# Create a cursor
cur = conn.cursor()

# Example: Update agent heartbeat
def update_agent_heartbeat(agent_name):
    cur.execute(
        "UPDATE agents SET last_heartbeat = NOW() WHERE agent_name = %s",
        (agent_name,)
    )
    conn.commit()

# Example: Record task start
def record_task_start(task_id, task_type, agent_name, priority, metadata):
    cur.execute(
        """
        INSERT INTO task_states 
        (task_id, task_type, agent_name, state, priority, created_at, updated_at, metadata)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s)
        """,
        (task_id, task_type, agent_name, "in_progress", priority, json.dumps(metadata))
    )
    conn.commit()

# Example: Record task completion
def record_task_completion(task_id, success, error_type=None, error_message=None):
    # Update task_states
    cur.execute(
        """
        UPDATE task_states 
        SET state = %s, completed_at = NOW(), updated_at = NOW() 
        WHERE task_id = %s
        RETURNING task_type, agent_name, priority, created_at, metadata
        """,
        ("completed" if success else "failed", task_id)
    )
    
    # Get task details
    result = cur.fetchone()
    if result:
        task_type, agent_name, priority, created_at, metadata = result
        
        # Calculate duration
        cur.execute("SELECT EXTRACT(EPOCH FROM (NOW() - %s)) * 1000", (created_at,))
        duration_ms = int(cur.fetchone()[0])
        
        # Insert into task_history
        cur.execute(
            """
            INSERT INTO task_history 
            (task_id, task_type, agent_name, state, priority, created_at, 
             completed_at, duration_ms, success, error_type, error_message, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s)
            """,
            (task_id, task_type, agent_name, 
             "completed" if success else "failed", 
             priority, created_at, duration_ms, success, 
             error_type, error_message, metadata)
        )
    
    conn.commit()

# Don't forget to close the connection when done
# cur.close()
# conn.close()
```

## Running Your Agent

### Running Locally

```bash
python my_agent.py
```

### Running in Docker

Create a Dockerfile for your agent:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY logger_util.py .
COPY metrics.py .
COPY my_agent.py .

# Expose port for metrics
EXPOSE 8001

# Run the agent
CMD ["python", "my_agent.py"]
```

Build and run the Docker container:

```bash
docker build -t my_agent -f Dockerfile.my_agent .
docker run --name my_agent --network logging-network -p 8001:8001 my_agent
```

## Visualization and Dashboards

When creating custom dashboards for your agent, you need to be aware of how Elasticsearch maps fields and how to properly query them in Grafana.

### Elasticsearch Field Mapping

When logs are sent to Elasticsearch, string fields are dynamically mapped as both:

1. A full-text searchable field (the field name itself)
2. A non-analyzed keyword field (the field name with a `.keyword` suffix)

For example, a field named `event_type` will be mapped as:
- `event_type`: Full-text searchable, tokenized, and analyzed
- `event_type.keyword`: Exact match, not analyzed, suitable for aggregations

### Grafana Dashboard Best Practices

When creating Grafana dashboards that use Elasticsearch as a data source:

1. For aggregations (terms, filters, etc.), always use the `.keyword` suffix for string fields:
   ```
   "field": "event_type.keyword"  // Correct for aggregations
   ```

2. For full-text search, use the field name without the suffix:
   ```
   "query": "event_type:task_completed"  // Correct for full-text search
   ```

3. For numeric and date fields, no suffix is needed.

For more details, see the documentation in `memlog/elasticsearch_field_mapping.md`.

## Checklist for Agent Integration

- [ ] Implement JSON logging with the required fields
- [ ] Define and use appropriate event types
- [ ] Expose Prometheus metrics
- [ ] Implement proper error handling with retry logic
- [ ] Set up database integration if needed
- [ ] Test logging appears in Kibana (check for correlation IDs and exception details)
- [ ] Test metrics appear in Prometheus/Grafana
- [ ] Document any agent-specific event types or metrics
- [ ] Create Grafana dashboards using proper field mapping (`.keyword` suffix for string aggregations) - see `memlog/elasticsearch_field_mapping.md`
- [ ] Configure agent's log level via `LOG_LEVEL` environment variable if needed (defaults to INFO)
