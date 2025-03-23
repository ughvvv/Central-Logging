# Central Logging, Monitoring, and Error Handling Infrastructure

This repository contains the central logging, monitoring, and error-handling infrastructure for a multi-agent system. It uses the ELK stack (Elasticsearch, Kibana) for logging and Prometheus/Grafana for metrics and dashboards.

## Overview

The infrastructure consists of:

1. **Logging Stack**: Elasticsearch + Kibana for storing and visualizing logs
2. **Monitoring Stack**: Prometheus + Grafana for metrics collection and visualization
3. **Python Utilities**: 
   - `logger_util.py`: JSON-formatted logging utility
   - `metrics.py`: Prometheus metrics utility
   - `orchestrator.py`: Stub orchestrator demonstrating logging and metrics

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
└── requirements.txt            # Python dependencies
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+

## Setup and Running

### 1. Start the Infrastructure

Start the ELK stack and Prometheus/Grafana:

```bash
docker-compose up -d
```

This will start:
- Elasticsearch on port 9200
- Kibana on port 5601
- Prometheus on port 9090
- Grafana on port 3000

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Orchestrator Stub

```bash
python orchestrator.py
```

The orchestrator will:
- Start a metrics server on port 8000
- Generate and process sample tasks
- Log events in JSON format
- Expose metrics for Prometheus

### 4. Access the Dashboards

- **Kibana**: http://localhost:5601
  - Create an index pattern for `filebeat-*` to view logs
  - Use Discover to search and filter logs

- **Prometheus**: http://localhost:9090
  - Query metrics like `tasks_dispatched` and `errors_encountered`

- **Grafana**: http://localhost:3000
  - Login with admin/admin
  - A sample dashboard is pre-configured

## JSON Logging Schema

Each log entry follows this schema:

```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "agent_name": "orchestrator",
  "event_type": "task_dispatch",
  "severity": "INFO",
  "message": "Dispatching task abc123",
  "metadata": {
    "task_id": "abc123",
    "priority": "high"
  }
}
```

## Key Log Events

The orchestrator logs these event types:
- `system_startup`: When the orchestrator starts
- `system_shutdown`: When the orchestrator shuts down
- `task_dispatch`: When a task is dispatched to an agent
- `transient_error_retry`: When a transient error occurs and is retried
- `max_retries_exceeded`: When max retries are exceeded for a transient error
- `permanent_error`: When a permanent error occurs
- `error`: When an unexpected error occurs

## Metrics

The following metrics are exposed:
- `tasks_dispatched`: Counter of tasks dispatched
- `errors_encountered`: Counter of errors by type
- `task_latency_seconds`: Histogram of task processing times

## Using in Your Agent Code

### Logging

```python
from logger_util import setup_logger, log

# Set up logger
logger = setup_logger(name="my_agent_logger")

# Log an event
log(
    logger,
    "INFO",
    "Processing task",
    "my_agent",
    "task_processing",
    {
        "task_id": "abc123",
        "details": "Additional information"
    }
)
```

### Metrics

```python
from metrics import increment_tasks_dispatched, TaskTimer

# Increment a counter
increment_tasks_dispatched()

# Time a task
with TaskTimer():
    # Your task code here
    process_task()
```

## Troubleshooting

- **Elasticsearch fails to start**: Check if you have enough memory allocated to Docker
- **Metrics not showing in Prometheus**: Ensure the orchestrator is running and accessible from the Docker network
- **Logs not appearing in Kibana**: Check Filebeat configuration and ensure it can access Docker logs

## Extending

- Add more metrics in `metrics.py`
- Create additional Grafana dashboards
- Implement real agent logic in place of the stub orchestrator
