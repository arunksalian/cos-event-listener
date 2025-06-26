from flask import Flask, request, jsonify
import os
import json
import logging
from datetime import datetime
import hmac
import hashlib
import base64
import mimetypes

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for COS event processing
COS_SECRET_KEY = os.environ.get('COS_SECRET_KEY', '')
COS_ENDPOINT = os.environ.get('COS_ENDPOINT', '')
COS_BUCKET_NAME = os.environ.get('COS_BUCKET_NAME', '')
# Allow disabling signature verification for testing
DISABLE_SIGNATURE_VERIFICATION = os.environ.get('DISABLE_SIGNATURE_VERIFICATION', 'false').lower() == 'true'

# Global variable to track PDF uploads (in production, use a database)
pdf_upload_count = 0
pdf_uploads = []

def is_pdf_file(object_key):
    """
    Check if the uploaded file is a PDF based on its extension and MIME type
    """
    if not object_key:
        return False
    
    # Check file extension
    file_extension = os.path.splitext(object_key.lower())[1]
    if file_extension == '.pdf':
        return True
    
    # Additional check: if the object key contains 'pdf' in the filename
    filename = os.path.basename(object_key.lower())
    if 'pdf' in filename:
        return True
    
    return False

def is_upload_event(event_type):
    """
    Check if the event is an upload event
    """
    upload_events = [
        'Object:Put',
        'Object:Post',
        's3:ObjectCreated:Put',
        's3:ObjectCreated:Post',
        's3:ObjectCreated:CompleteMultipartUpload'
    ]
    return event_type in upload_events

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint that accepts query parameters
    """
    # Get all query parameters
    query_params = dict(request.args)
    
    # Get a specific query parameter (example: 'name')
    name = request.args.get('name', 'World')
    
    # Get another query parameter (example: 'age')
    age = request.args.get('age')
    
    response = {
        'message': f'Hello, {name}!',
        'query_parameters': query_params,
        'specific_params': {
            'name': name,
            'age': age
        },
        'cos_config': {
            'endpoint': COS_ENDPOINT,
            'bucket': COS_BUCKET_NAME,
            'has_secret': bool(COS_SECRET_KEY)
        }
    }
    
    return jsonify(response)

@app.route('/cos/events', methods=['POST'])
def handle_cos_events():
    """
    Handle Cloud Object Storage events
    This endpoint receives webhook notifications from COS
    """
    try:
        # Log the incoming request
        logger.info(f"Received COS event at {datetime.now()}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Get the raw body for signature verification
        raw_body = request.get_data()
        
        # Verify signature if secret key is configured and not disabled
        if COS_SECRET_KEY and not DISABLE_SIGNATURE_VERIFICATION and not verify_cos_signature(request.headers, raw_body):
            logger.warning("Invalid signature received")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse the JSON payload
        try:
            event_data = json.loads(raw_body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Process the COS event
        processed_events = process_cos_events(event_data)
        
        # Log the processed events
        logger.info(f"Processed {len(processed_events)} events")
        
        return jsonify({
            'status': 'success',
            'message': f'Processed {len(processed_events)} events',
            'events': processed_events,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing COS event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cos/events', methods=['GET'])
def get_cos_events():
    """
    Get recent COS events (for debugging/monitoring)
    """
    # In a real application, you'd store events in a database
    # For now, we'll return a simple status
    return jsonify({
        'status': 'active',
        'endpoint': '/cos/events',
        'method': 'POST',
        'description': 'COS event webhook endpoint',
        'config': {
            'endpoint': COS_ENDPOINT,
            'bucket': COS_BUCKET_NAME,
            'has_secret': bool(COS_SECRET_KEY)
        }
    })

def verify_cos_signature(headers, body):
    """
    Verify the signature of the COS webhook
    """
    try:
        # Get the signature from headers
        signature = headers.get('X-Cos-Signature')
        if not signature:
            logger.warning("No signature found in headers")
            return False
        
        # Calculate expected signature
        expected_signature = base64.b64encode(
            hmac.new(
                COS_SECRET_KEY.encode('utf-8'),
                body,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False

def process_cos_events(event_data):
    """
    Process COS events and extract relevant information
    """
    processed_events = []
    
    try:
        # Handle different event formats
        if 'Records' in event_data:
            # AWS S3 compatible format
            for record in event_data['Records']:
                event = extract_event_info(record)
                if event:
                    processed_events.append(event)
                    # Check for PDF upload
                    check_pdf_upload(event)
        elif 'events' in event_data:
            # IBM COS format
            for event in event_data['events']:
                processed_event = extract_ibm_cos_event_info(event)
                if processed_event:
                    processed_events.append(processed_event)
                    # Check for PDF upload
                    check_pdf_upload(processed_event)
        else:
            # Single event or unknown format
            event = extract_event_info(event_data)
            if event:
                processed_events.append(event)
                # Check for PDF upload
                check_pdf_upload(event)
                
    except Exception as e:
        logger.error(f"Error processing events: {e}")
    
    return processed_events

def check_pdf_upload(event):
    """
    Check if the event is a PDF upload and log it
    """
    global pdf_upload_count, pdf_uploads
    
    try:
        event_type = event.get('event_type', '')
        object_key = event.get('object_key', '')
        bucket = event.get('bucket', '')
        
        # Check if it's an upload event and the file is a PDF
        if is_upload_event(event_type) and is_pdf_file(object_key):
            logger.info(f"📄 PDF UPLOAD DETECTED: File '{object_key}' uploaded to bucket '{bucket}' at {event.get('timestamp', 'unknown time')}")
            logger.info(f"📄 PDF Details: Event Type: {event_type}, Source: {event.get('source', 'unknown')}")
            
            # Track PDF upload
            pdf_upload_count += 1
            pdf_upload_info = {
                'file_name': object_key,
                'bucket': bucket,
                'event_type': event_type,
                'timestamp': event.get('timestamp', datetime.now().isoformat()),
                'source': event.get('source', 'unknown')
            }
            pdf_uploads.append(pdf_upload_info)
            
            # Keep only the last 100 PDF uploads to prevent memory issues
            if len(pdf_uploads) > 100:
                pdf_uploads.pop(0)
            
            # You can add additional processing here, such as:
            # - Sending notifications
            # - Triggering PDF processing workflows
            # - Updating databases
            # - Calling external services
            
    except Exception as e:
        logger.error(f"Error checking PDF upload: {e}")

def extract_event_info(record):
    """
    Extract event information from S3-compatible format
    """
    try:
        event_name = record.get('eventName', 'Unknown')
        bucket_name = record.get('s3', {}).get('bucket', {}).get('name', 'Unknown')
        object_key = record.get('s3', {}).get('object', {}).get('key', 'Unknown')
        
        return {
            'event_type': event_name,
            'bucket': bucket_name,
            'object_key': object_key,
            'timestamp': record.get('eventTime', datetime.now().isoformat()),
            'source': 's3_compatible'
        }
    except Exception as e:
        logger.error(f"Error extracting S3 event info: {e}")
        return None

def extract_ibm_cos_event_info(event):
    """
    Extract event information from IBM COS format
    """
    try:
        return {
            'event_type': event.get('eventType', 'Unknown'),
            'bucket': event.get('bucket', 'Unknown'),
            'object_key': event.get('key', 'Unknown'),
            'timestamp': event.get('time', datetime.now().isoformat()),
            'source': 'ibm_cos'
        }
    except Exception as e:
        logger.error(f"Error extracting IBM COS event info: {e}")
        return None

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Another endpoint that demonstrates different query parameter handling
    """
    # Get query parameters with defaults
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    category = request.args.get('category', 'all')
    
    # Simulate some data based on parameters
    data = {
        'items': [
            {'id': 1, 'name': 'Item 1', 'category': 'tech'},
            {'id': 2, 'name': 'Item 2', 'category': 'books'},
            {'id': 3, 'name': 'Item 3', 'category': 'tech'},
        ]
    }
    
    # Filter by category if specified
    if category != 'all':
        data['items'] = [item for item in data['items'] if item['category'] == category]
    
    # Apply pagination
    data['items'] = data['items'][offset:offset + limit]
    
    response = {
        'data': data,
        'pagination': {
            'limit': limit,
            'offset': offset,
            'total': len(data['items'])
        },
        'filters': {
            'category': category
        }
    }
    
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Server is running',
        'cos_configured': bool(COS_ENDPOINT and COS_BUCKET_NAME),
        'signature_verification': {
            'enabled': bool(COS_SECRET_KEY and not DISABLE_SIGNATURE_VERIFICATION),
            'secret_configured': bool(COS_SECRET_KEY),
            'disabled_for_testing': DISABLE_SIGNATURE_VERIFICATION
        },
        'pdf_detection': {
            'enabled': True,
            'total_pdf_uploads': pdf_upload_count
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/pdf/stats', methods=['GET'])
def pdf_stats():
    """
    Get PDF upload statistics
    """
    # Get query parameters for filtering
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get recent PDF uploads with pagination
    recent_uploads = pdf_uploads[offset:offset + limit] if pdf_uploads else []
    
    return jsonify({
        'pdf_upload_statistics': {
            'total_pdf_uploads': pdf_upload_count,
            'recent_uploads_count': len(recent_uploads),
            'uploads_tracked': len(pdf_uploads)
        },
        'recent_pdf_uploads': recent_uploads,
        'pagination': {
            'limit': limit,
            'offset': offset,
            'total': len(pdf_uploads)
        },
        'detection_config': {
            'upload_events': [
                'Object:Put',
                'Object:Post',
                's3:ObjectCreated:Put',
                's3:ObjectCreated:Post',
                's3:ObjectCreated:CompleteMultipartUpload'
            ],
            'pdf_extensions': ['.pdf'],
            'filename_patterns': ['pdf']
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app in debug mode for development
    app.run(host='0.0.0.0', port=port, debug=True) 