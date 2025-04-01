# Central Logging, Monitoring, and Error Handling Infrastructure

This repository contains the central logging, monitoring, and error-handling infrastructure for a multi-agent system. It uses the ELK stack (Elasticsearch, Kibana) for logging and Prometheus/Grafana for metrics and dashboards.

## Overview

The infrastructure consists of:

1.  **Logging Stack**: Elasticsearch + Kibana for storing and visualizing logs
2.  **Monitoring Stack**: Prometheus + Grafana for metrics collection and visualization
3.  **Python Utilities**:
    *   `logger_util.py`: JSON-formatted logging utility with dynamic level configuration, correlation IDs, and enhanced error reporting.
    *   `metrics.py`: Prometheus metrics utility
    *   `orchestrator.py`: Stub orchestrator demonstrating logging and metrics
    *   `test_agent.py`: Test agent demonstrating integration with the infrastructure

## Directory Structure

```
.
├── docker-compose.yml          # Docker Compose configuration
├── prometheus.yml              # Prometheus configuration
├── filebeat.yml                # Filebeat configuration for log shipping
├── grafana/                    # Grafana configuration
│   └── provisioning/
│       ├── dashboards/         # Dashboard configurations
│       └── datasources/        # Data source configurations
├── logger_util.py              # JSON logging utility
├── metrics.py                  # Prometheus metrics utility
├── orchestrator.py             # Stub orchestrator
├── test_agent.py               # Test agent example
├── create_new_agent.py         # Script to generate new agent templates
├── requirements.txt            # Python dependencies
├── memlog/                     # Changelogs and documentation
└── ...                         # Other scripts and config files
```

## Prerequisites

-   Python 3.8+ for running the Python components
-   Docker and Docker Compose for running the full infrastructure (Elasticsearch, Kibana, Prometheus, Grafana, PostgreSQL)

If you don't have Docker installed, see [DOCKER_SETUP.md](DOCKER_SETUP.md) for installation instructions.

## Setup and Running

### 1. Start the Infrastructure

Start the ELK stack and Prometheus/Grafana:

```bash
docker-compose up -d
```

This will start:
-   Elasticsearch on port 9200
-   Kibana on port 5601
-   Prometheus on port 9090
-   Grafana on port 3000
-   PostgreSQL on port 5432
-   Filebeat (collects logs from containers)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Logging (Optional)

The logging level can be configured via the `LOG_LEVEL` environment variable. Valid values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. If not set, it defaults to `INFO`.

```bash
export LOG_LEVEL=DEBUG # Example: Set log level to DEBUG
```

### 4. Run Agents (Orchestrator / Test Agent)

You can run the orchestrator or test agent either locally or in Docker containers:

#### Running Locally

```bash
# Example: Run test agent locally with DEBUG level
export LOG_LEVEL=DEBUG
python test_agent.py
```

When running locally, logs will be output to stdout. Filebeat (running in Docker) is configured to pick up logs from Docker containers, so local logs won't be automatically shipped unless you configure a local Filebeat instance or redirect output.

#### Running in Docker

Build and run the agent containers:

```bash
# Build images
docker build -t orchestrator -f Dockerfile.orchestrator .
docker build -t test_agent -f Dockerfile.test_agent .

# Run containers (example with test_agent)
# Set LOG_LEVEL environment variable for the container
docker run --name test_agent --network logging-network -p 8001:8001 -e LOG_LEVEL=DEBUG test_agent
```

When running in Docker, logs will automatically be collected by the Filebeat container and shipped to Elasticsearch.

### 5. Access the Dashboards

-   **Kibana**: http://localhost:5601
    -   Create index patterns (e.g., `filebeat-*`, `orchestrator-logs-*`, `test_agent-*`) to view logs.
    -   Use Discover to search and filter logs (e.g., `metadata.correlation_id:"some-task-id"`).
    -   Verify JSON fields (timestamp, agent_name, event_type, severity, message, metadata, metadata.exception, metadata.correlation_id) are correctly mapped and searchable.

-   **Prometheus**: http://localhost:9090
    -   Query metrics like `tasks_dispatched` and `errors_encountered`.

-   **Grafana**: http://localhost:3000
    -   Login: `admin` / `admin` (or check [GRAFANA_ANONYMOUS_ACCESS.md](GRAFANA_ANONYMOUS_ACCESS.md) if anonymous access is enabled).
    -   View pre-configured dashboards (Orchestrator, Test Agent).
    -   Remember to use `.keyword` suffix for string fields in Elasticsearch queries within Grafana panels (see `memlog/elasticsearch_field_mapping.md`).

## JSON Logging Schema

Each log entry follows this enhanced schema:

```json
{
  "timestamp": "2023-01-01T12:00:00.123Z", // ISO 8601 format with Z for UTC
  "agent_name": "test_agent_1",           // Name of the agent generating the log
  "event_type": "task_processing",        // Type of event being logged
  "severity": "INFO",                     // Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  "message": "Processing task abc123",    // Human-readable log message
  "metadata": {                           // Additional structured data
    "task_id": "abc123",                  // Example metadata field
    "priority": "high",                   // Example metadata field
    "correlation_id": "abc123",           // ID to correlate logs for a specific task/request
    "exception": {                        // Included for ERROR/CRITICAL logs if an exception occurred
      "type": "ValueError",
      "message": "Invalid input",
      "traceback": [ /* Array of traceback strings */ ]
    }
  }
}
```

## Key Log Events

Standard event types include:
-   `system_startup`, `system_shutdown`
-   `task_received`, `task_processing`, `task_completed`, `task_failed`
-   `agent_registered`, `agent_heartbeat`
-   `transient_error_retry`, `max_retries_exceeded`, `permanent_error`, `unexpected_error`
-   `test_task_created`, `test_tasks_batch_created`

## Metrics

The following metrics are exposed:
-   `tasks_dispatched`: Counter of tasks dispatched (labeled by `task_type`)
-   `errors_encountered`: Counter of errors by type (labeled by `error_type`)
-   `task_latency_seconds`: Histogram of task processing times (labeled by `task_type`)
-   `active_tasks`: Gauge of currently active tasks (labeled by `agent_type`)

## Database Integration

The infrastructure includes a PostgreSQL database (`orchestrator_db` on port 5432) for persistent state. See `init-db.sql` for schema details (tables: `task_states`, `agents`, `task_history`, `system_config`).

## Using in Your Agent Code

### Logging

```python
from logger_util import setup_logger, log
import uuid

# Set up logger (reads LOG_LEVEL from env var)
logger = setup_logger(name="my_agent_logger")

# Example: Log an event with correlation ID
task_id = str(uuid.uuid4())
log(
    logger,
    "INFO",
    "Processing task",
    "my_agent",
    "task_processing",
    metadata={"task_id": task_id, "details": "Additional information"},
    correlation_id=task_id # Pass correlation ID
)

# Example: Log an error (exception info captured automatically)
try:
    # some operation that might fail
    result = 1 / 0
except Exception as e:
    log(
        logger,
        "ERROR",
        f"Failed operation for task {task_id}",
        "my_agent",
        "operation_failed",
        metadata={"task_id": task_id},
        correlation_id=task_id
    ) # exc_info is automatically added by the log function
```

### Metrics

```python
from metrics import (
    increment_tasks_dispatched,
    increment_errors,
    increment_active_tasks,
    decrement_active_tasks,
    TaskTimer
)

# Increment a counter with labels
increment_tasks_dispatched(task_type="content_generation")

# Track errors by type
increment_errors(error_type="transient")

# Track active tasks
increment_active_tasks(agent_type="research_agent")
try:
    # ... do work ...
    pass
finally:
    decrement_active_tasks(agent_type="research_agent")

# Time a task with labels
with TaskTimer(task_type="content_generation"):
    # Your task code here
    process_task()
```

## Validation and Testing

Use the provided scripts (`validate_local.py`, `run_validation.sh`, `run_complete_test.sh`) to test the infrastructure components. See the script headers and output for details.

### Validation Checklist

-   [ ] All services (Elasticsearch, Kibana, Prometheus, Grafana, PostgreSQL) start and run correctly via `docker-compose up`.
-   [ ] Logs are correctly formatted in JSON and appear in Kibana with all expected fields (including `correlation_id` and `metadata.exception`).
-   [ ] Logs are searchable/filterable in Kibana by key fields (`agent_name`, `event_type`, `severity`, `metadata.correlation_id`).
-   [ ] Setting `LOG_LEVEL` environment variable correctly controls the log output verbosity.
-   [ ] Error logs automatically include stack traces.
-   [ ] Metrics are being scraped by Prometheus and displayed in Grafana.
-   [ ] Database operations (agent registration, task updates) are successful.

## Troubleshooting

-   **Elasticsearch fails to start**: Check Docker memory allocation.
-   **Metrics not showing**: Ensure the agent/orchestrator container is running and its metrics port is exposed and accessible on the Docker network. Check Prometheus target configuration (`prometheus.yml`).
-   **Logs not appearing in Kibana**:
    -   Verify Filebeat container is running (`docker ps`).
    -   Check Filebeat logs (`docker logs filebeat`).
    -   Ensure Filebeat configuration (`filebeat.yml`) is correct and points to the Elastic Cloud instance.
    -   Check Kibana index patterns match the indices created by Filebeat/agents (e.g., `filebeat-*`, `test_agent-*`).
    -   Verify network connectivity between Filebeat and Elasticsearch.
-   **Validation script fails**: Check the script output for specific errors. Ensure all services are running and accessible.

## Extending

-   Add more specific metrics in `metrics.py`.
-   Create additional Grafana dashboards or Kibana visualizations.
-   Implement real agent logic.
-   Consider packaging `logger_util.py` and `metrics.py` into a shared library.

## Agent Integration

For detailed instructions on how to integrate new agents with this infrastructure, see [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) and the new `CENTRAL_LOGGING_ONBOARDING.md` checklist (to be created).

### Test Agent

A `test_agent.py` is provided as a reference implementation. Run it via `./run_test_agent.sh` or Docker.

### Creating New Agents

Use `./create_new_agent.py <agent_name> --port <port_num> --skills <skill1> <skill2>` to generate a template for a new agent.
