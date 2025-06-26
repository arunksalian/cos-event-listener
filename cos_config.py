"""
Cloud Object Storage Configuration
This file contains configuration settings for COS event handling
"""

import os

# COS Configuration
COS_CONFIG = {
    'endpoint': os.environ.get('COS_ENDPOINT', ''),
    'bucket_name': os.environ.get('COS_BUCKET_NAME', ''),
    'secret_key': os.environ.get('COS_SECRET_KEY', ''),
    'api_key': os.environ.get('COS_API_KEY', ''),
    'instance_id': os.environ.get('COS_INSTANCE_ID', ''),
    'region': os.environ.get('COS_REGION', 'us-south'),
}

# Event Types to listen for
COS_EVENT_TYPES = [
    'Object:Put',
    'Object:Post',
    'Object:Delete',
    'Object:Copy',
    'Object:CompleteMultipartUpload',
    'Object:AbortMultipartUpload'
]

# Webhook Configuration
WEBHOOK_CONFIG = {
    'endpoint': '/cos/events',
    'method': 'POST',
    'timeout': 30,  # seconds
    'retry_attempts': 3,
    'verify_ssl': True,
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': os.environ.get('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.environ.get('LOG_FILE', 'cos_events.log'),
}

# Event Processing Configuration
EVENT_PROCESSING = {
    'max_events_per_request': 100,
    'event_timeout': 60,  # seconds
    'enable_signature_verification': True,
    'store_events': False,  # Set to True if you want to store events
}

def get_cos_config():
    """Get COS configuration"""
    return COS_CONFIG

def is_cos_configured():
    """Check if COS is properly configured"""
    config = get_cos_config()
    return bool(config['endpoint'] and config['bucket_name'])

def get_webhook_url(base_url):
    """Get the full webhook URL"""
    return f"{base_url.rstrip('/')}{WEBHOOK_CONFIG['endpoint']}" 