from prometheus_client import Counter, Histogram, start_http_server
import time

# Define metrics
tasks_dispatched = Counter(
    'tasks_dispatched', 
    'Number of tasks dispatched by the orchestrator'
)

errors_encountered = Counter(
    'errors_encountered', 
    'Number of errors encountered during task processing',
    ['error_type']  # Label for different error types
)

task_latency = Histogram(
    'task_latency_seconds', 
    'Time taken to process a task',
    buckets=(0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0)  # Define buckets in seconds
)

# Helper functions for common metric operations
def increment_tasks_dispatched():
    """Increment the tasks_dispatched counter."""
    tasks_dispatched.inc()

def increment_errors(error_type="general"):
    """
    Increment the errors_encountered counter.
    
    Args:
        error_type (str): Type of error (e.g., 'transient', 'critical')
    """
    errors_encountered.labels(error_type=error_type).inc()

def track_task_latency(func):
    """
    Decorator to track task latency.
    
    Args:
        func: The function to track
        
    Returns:
        Wrapped function that tracks execution time
    """
    def wrapper(*args, **kwargs):
        with task_latency.time():
            return func(*args, **kwargs)
    return wrapper

class TaskTimer:
    """Context manager for timing task execution."""
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        task_latency.observe(duration)

def start_metrics_server(port=8000):
    """
    Start the Prometheus metrics HTTP server.
    
    Args:
        port (int): Port to expose metrics on
    """
    start_http_server(port)
    print(f"Metrics server started on port {port}")
