# Central Logging Onboarding Checklist

This checklist outlines the steps required to integrate a new agent or microservice with the central logging infrastructure.

## Prerequisites

-   Ensure your agent's Python environment has access to the `logger_util.py` module (either by copying it or installing it as part of a shared library).
-   Familiarize yourself with the standard JSON log schema defined in the main `README.md`.

## Integration Steps

1.  **Import Utilities**:
    *   Import `setup_logger` and `log` from `logger_util`.
    ```python
    from logger_util import setup_logger, log
    import uuid # For generating correlation IDs if needed
    ```

2.  **Initialize Logger**:
    *   Set up a logger instance for your agent, typically near the start of your main script or class initialization.
    *   The logger name should be unique to your agent (e.g., `research_agent_logger`).
    *   The log level is automatically configured via the `LOG_LEVEL` environment variable (defaults to `INFO`).
    ```python
    AGENT_NAME = "my_new_agent" # Define your agent's name
    logger = setup_logger(name=f"{AGENT_NAME}_logger")
    ```

3.  **Implement Logging Calls**:
    *   Use the `log()` helper function throughout your agent's code to record events.
    *   **Required Parameters**:
        *   `logger`: The logger instance created in Step 2.
        *   `level`: Log severity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
        *   `message`: A human-readable description of the event.
        *   `agent_name`: The name of your agent (e.g., `AGENT_NAME`).
        *   `event_type`: A short, descriptive string identifying the event (use standard types from `README.md` where possible, or define agent-specific ones).
    *   **Optional Parameters**:
        *   `metadata` (dict): A dictionary for additional structured context (e.g., task details, input parameters, results).
        *   `correlation_id` (str): An identifier (like a `task_id` or `session_id`) to link related log entries across different agents or operations. Pass this ID consistently for all logs related to the same task or request.

    ```python
    # Example: Logging task start with correlation ID
    task_id = str(uuid.uuid4())
    log(
        logger,
        "INFO",
        f"Starting task {task_id}",
        AGENT_NAME,
        "task_processing",
        metadata={"task_type": "data_analysis", "input_size": 1024},
        correlation_id=task_id
    )
    ```

4.  **Handle Error Logging**:
    *   When logging errors (`ERROR` or `CRITICAL` level) within an `except` block, the `log()` function automatically captures and includes exception details (type, message, traceback) in the `metadata.exception` field.
    *   Use standardized `event_type` values for errors (e.g., `transient_error_retry`, `permanent_error`, `unexpected_error`).

    ```python
    try:
        # Risky operation
        if some_condition:
            raise ValueError("Invalid condition")
    except ValueError as e:
        log(
            logger,
            "ERROR",
            f"Validation failed for task {task_id}: {e}",
            AGENT_NAME,
            "validation_error", # Example specific error type
            metadata={"task_id": task_id},
            correlation_id=task_id
        ) # Exception info is added automatically
    except Exception as e:
        log(
            logger,
            "CRITICAL",
            f"Unexpected failure during task {task_id}: {e}",
            AGENT_NAME,
            "unexpected_error",
            metadata={"task_id": task_id},
            correlation_id=task_id
        ) # Exception info is added automatically
    ```

5.  **Configure Agent Environment (if running in Docker)**:
    *   When running your agent in a Docker container, ensure the `LOG_LEVEL` environment variable is set if you need a level other than the default (`INFO`).
    ```yaml
    # Example in docker-compose.yml
    services:
      my_new_agent:
        image: my_new_agent_image
        environment:
          - LOG_LEVEL=DEBUG # Set desired log level
        # ... other configurations ...
    ```

## Testing and Validation

1.  **Run the Agent**: Execute your agent locally or in Docker.
2.  **Generate Logs**: Trigger various code paths in your agent to generate different log events (info, warnings, errors with exceptions, different event types).
3.  **Check Log Output**:
    *   If running locally, check the console output for correctly formatted JSON logs.
    *   If running in Docker, check Kibana:
        *   Ensure logs appear in the appropriate index (e.g., `filebeat-*` or a custom index if configured).
        *   Verify all fields (`timestamp`, `agent_name`, `event_type`, `severity`, `message`, `metadata`, `metadata.correlation_id`) are present and correctly populated.
        *   Confirm error logs contain the `metadata.exception` field with traceback details.
        *   Test filtering in Kibana using `metadata.correlation_id` to trace a single task's logs.
4.  **Test Log Level Configuration**:
    *   Run the agent with different `LOG_LEVEL` settings (e.g., `DEBUG`, `WARNING`) and verify that only logs at or above the specified level are outputted/shipped.

## Final Checklist

-   [ ] Logger initialized with a unique agent name.
-   [ ] `log()` function used for all significant events.
-   [ ] Standard event types used where applicable.
-   [ ] Correlation ID passed for related operations (e.g., using `task_id`).
-   [ ] Error logging uses `ERROR` or `CRITICAL` level within `except` blocks.
-   [ ] Agent's `LOG_LEVEL` is configurable via environment variable.
-   [ ] Logs validated in Kibana (correct format, fields, correlation, exceptions).
-   [ ] Log level configuration tested.
