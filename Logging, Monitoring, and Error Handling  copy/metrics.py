from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
tasks_dispatched = Counter(
    'tasks_dispatched', 
    'Number of tasks dispatched by the orchestrator',
    ['task_type']  # Label for different task types
)

errors_encountered = Counter(
    'errors_encountered', 
    'Number of errors encountered during task processing',
    ['error_type']  # Label for different error types
)

task_latency = Histogram(
    'task_latency_seconds', 
    'Time taken to process a task',
    ['task_type'],  # Label for different task types
    buckets=(0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0)  # Define buckets in seconds
)

active_tasks = Gauge(
    'active_tasks',
    'Number of tasks currently being processed',
    ['agent_type']  # Label for different agent types
)

# Helper functions for common metric operations
def increment_tasks_dispatched(task_type="unknown"):
    """
    Increment the tasks_dispatched counter.
    
    Args:
        task_type (str): Type of task being dispatched
    """
    tasks_dispatched.labels(task_type=task_type).inc()

def increment_errors(error_type="general"):
    """
    Increment the errors_encountered counter.
    
    Args:
        error_type (str): Type of error (e.g., 'transient', 'critical')
    """
    errors_encountered.labels(error_type=error_type).inc()

def track_task_latency(task_type="unknown"):
    """
    Decorator to track task latency.
    
    Args:
        task_type (str): Type of task being tracked
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with task_latency.labels(task_type=task_type).time():
                return func(*args, **kwargs)
        return wrapper
    return decorator

class TaskTimer:
    """Context manager for timing task execution."""
    
    def __init__(self, task_type="unknown"):
        self.task_type = task_type
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        task_latency.labels(task_type=self.task_type).observe(duration)

def increment_active_tasks(agent_type="unknown"):
    """
    Increment the active_tasks gauge.
    
    Args:
        agent_type (str): Type of agent processing the task
    """
    active_tasks.labels(agent_type=agent_type).inc()

def decrement_active_tasks(agent_type="unknown"):
    """
    Decrement the active_tasks gauge.
    
    Args:
        agent_type (str): Type of agent processing the task
    """
    active_tasks.labels(agent_type=agent_type).dec()

def start_metrics_server(port=8000):
    """
    Start the Prometheus metrics HTTP server.
    
    Args:
        port (int): Port to expose metrics on
    """
    start_http_server(port)
    print(f"Metrics server started on port {port}")
