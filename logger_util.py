import logging
import json
from datetime import datetime
import traceback
import sys

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def format(self, record):
        """
        Format the log record as JSON.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_name": getattr(record, "agent_name", "unknown_agent"),
            "event_type": getattr(record, "event_type", "unknown_event"),
            "severity": record.levelname,
            "message": record.getMessage(),
            "metadata": getattr(record, "metadata", {})
        }
        
        # Add exception info if available
        if record.exc_info:
            log_entry["metadata"]["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry)

def setup_logger(name="json_logger", log_file=None, level=logging.INFO):
    """
    Set up a logger with JSON formatting.
    
    Args:
        name (str): Name of the logger
        log_file (str, optional): Path to log file. If None, logs to stdout.
        level (int, optional): Logging level. Defaults to INFO.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create handler (file or stdout)
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger

def log(logger, level, message, agent_name, event_type, metadata=None):
    """
    Helper function to log with the required fields.
    
    Args:
        logger (logging.Logger): Logger instance
        level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message (str): Log message
        agent_name (str): Name of the agent
        event_type (str): Type of event
        metadata (dict, optional): Additional metadata
    """
    if metadata is None:
        metadata = {}
    
    extra = {
        "agent_name": agent_name,
        "event_type": event_type,
        "metadata": metadata
    }
    
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    log_level = level_map.get(level.upper(), logging.INFO)
    logger.log(log_level, message, extra=extra)
