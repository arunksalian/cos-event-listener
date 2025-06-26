#!/usr/bin/env python3
"""
Logging configuration for the Cloud Object Storage Event Listener
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(log_level=None, log_file=None, max_bytes=10*1024*1024, backup_count=5):
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: app.log)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
    """
    
    # Default log level
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Default log file
    if log_file is None:
        log_file = os.environ.get('LOG_FILE', 'app.log')
    
    # Convert string to logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    
    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    
    # Create error file handler
    error_log_file = log_file.replace('.log', '_error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set to lowest level to capture all
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Create application logger
    app_logger = logging.getLogger(__name__)
    
    # Log configuration
    app_logger.info("🔧 Logging Configuration Applied")
    app_logger.info(f"   - Log Level: {log_level}")
    app_logger.info(f"   - Log File: {log_file}")
    app_logger.info(f"   - Error Log File: {error_log_file}")
    app_logger.info(f"   - Max File Size: {max_bytes} bytes")
    app_logger.info(f"   - Backup Count: {backup_count}")
    
    return app_logger

def get_logger(name):
    """
    Get a logger with the specified name
    """
    return logging.getLogger(name)

def log_request_info(logger, request, response=None):
    """
    Log detailed request information
    
    Args:
        logger: Logger instance
        request: Flask request object
        response: Flask response object (optional)
    """
    logger.info(f"📨 Request: {request.method} {request.path}")
    logger.info(f"   - IP: {request.remote_addr}")
    logger.info(f"   - User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    logger.info(f"   - Content Type: {request.headers.get('Content-Type', 'Unknown')}")
    logger.info(f"   - Content Length: {request.headers.get('Content-Length', 'Unknown')}")
    
    if request.args:
        logger.debug(f"   - Query Parameters: {dict(request.args)}")
    
    if response:
        logger.info(f"📤 Response: {response.status_code}")
        logger.debug(f"   - Response Headers: {dict(response.headers)}")

def log_cos_event(logger, event_data, event_type="COS"):
    """
    Log COS event information
    
    Args:
        logger: Logger instance
        event_data: Event data dictionary
        event_type: Type of event (COS, S3, etc.)
    """
    logger.info(f"📋 {event_type} Event Received")
    logger.debug(f"   - Event Structure: {list(event_data.keys())}")
    
    if 'events' in event_data:
        logger.info(f"   - Number of Events: {len(event_data['events'])}")
        for i, event in enumerate(event_data['events'], 1):
            logger.debug(f"   - Event {i}: {event.get('eventType', 'Unknown')} - {event.get('key', 'Unknown')}")
    
    elif 'Records' in event_data:
        logger.info(f"   - Number of Records: {len(event_data['Records'])}")
        for i, record in enumerate(event_data['Records'], 1):
            event_name = record.get('eventName', 'Unknown')
            bucket = record.get('s3', {}).get('bucket', {}).get('name', 'Unknown')
            key = record.get('s3', {}).get('object', {}).get('key', 'Unknown')
            logger.debug(f"   - Record {i}: {event_name} - {bucket}/{key}")

def log_pdf_detection(logger, file_name, bucket, event_type, is_pdf):
    """
    Log PDF detection results
    
    Args:
        logger: Logger instance
        file_name: Name of the file
        bucket: Bucket name
        event_type: Type of event
        is_pdf: Whether the file is a PDF
    """
    if is_pdf:
        logger.info(f"📄 PDF DETECTED: {file_name} in bucket {bucket}")
        logger.info(f"   - Event Type: {event_type}")
        logger.info(f"   - Timestamp: {datetime.now().isoformat()}")
    else:
        logger.debug(f"📝 Not PDF: {file_name} in bucket {bucket}")

def log_performance(logger, operation, start_time, end_time=None):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Name of the operation
        start_time: Start time (datetime)
        end_time: End time (datetime, optional)
    """
    if end_time is None:
        end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    logger.info(f"⏱️ Performance: {operation} completed in {duration:.3f} seconds")
    
    if duration > 1.0:
        logger.warning(f"⚠️ Slow operation: {operation} took {duration:.3f} seconds")

# Convenience functions for common logging patterns
def log_startup(logger, app_name, version="1.0.0"):
    """Log application startup information"""
    logger.info("🚀 " + "="*60)
    logger.info(f"🚀 Starting {app_name} v{version}")
    logger.info(f"🚀 Startup Time: {datetime.now().isoformat()}")
    logger.info("🚀 " + "="*60)

def log_shutdown(logger, app_name):
    """Log application shutdown information"""
    logger.info("🛑 " + "="*60)
    logger.info(f"🛑 Shutting down {app_name}")
    logger.info(f"🛑 Shutdown Time: {datetime.now().isoformat()}")
    logger.info("🛑 " + "="*60)

def log_error_with_context(logger, error, context=""):
    """Log error with additional context"""
    logger.error(f"❌ Error: {error}")
    if context:
        logger.error(f"❌ Context: {context}")
    logger.exception("🔍 Full exception details:") 