"""
Logging configuration for KubeGenie Backend
"""

import logging
import sys
from typing import Any, Dict
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
                
        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Setup logging configuration"""
    
    # Get log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set formatter
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("kubernetes").setLevel(logging.WARNING)
    
    logging.info("Logging configured", extra={"level": log_level, "format": log_format})