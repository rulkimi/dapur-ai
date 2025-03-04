import json
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time
from typing import Dict, Any
from .context import get_request_id

class RequestIDFilter(logging.Filter):
    """Filter that adds request_id to log records."""
    
    def filter(self, record):
        record.request_id = get_request_id()
        return True

class JsonFormatter(logging.Formatter):
    """Formatter that outputs JSON formatted logs."""
    
    def format(self, record) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", ""),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields from record dict
        for key, value in record.__dict__.items():
            if key not in ("args", "asctime", "created", "exc_info", "exc_text", 
                           "filename", "funcName", "id", "levelname", "levelno",
                           "lineno", "module", "msecs", "message", "msg", 
                           "name", "pathname", "process", "processName", 
                           "relativeCreated", "stack_info", "thread", "threadName",
                           "request_id"):
                log_data[key] = value
                
        return json.dumps(log_data)

def configure_logging(log_dir: Path = None):
    """Configure application logging with request ID."""
    if log_dir is None:
        log_dir = Path("logs")
    
    os.makedirs(log_dir, exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (for development)
    console = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "[%(asctime)s] [%(request_id)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console.setFormatter(console_formatter)
    console.addFilter(RequestIDFilter())
    root_logger.addHandler(console)
    
    # File handler with rotation (for production/debugging)
    file_handler = RotatingFileHandler(
        filename=log_dir / "application.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=10,       # Keep 10 backup files
    )
    file_handler.setFormatter(JsonFormatter())
    file_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(file_handler)
    
    # Error-specific log file
    error_handler = RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=10,       # Keep 10 backup files
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JsonFormatter())
    error_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(error_handler)
    
    # Return the configured logger
    return root_logger 