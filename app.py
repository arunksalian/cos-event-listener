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

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Log application startup
logger.info("🚀 Starting Cloud Object Storage Event Listener")
logger.info("📋 Application Configuration:")
logger.info(f"   - COS Endpoint: {'Configured' if os.environ.get('COS_ENDPOINT') else 'Not configured'}")
logger.info(f"   - COS Bucket: {'Configured' if os.environ.get('COS_BUCKET_NAME') else 'Not configured'}")
logger.info(f"   - Secret Key: {'Configured' if os.environ.get('COS_SECRET_KEY') else 'Not configured'}")
logger.info(f"   - Signature Verification: {'Disabled' if os.environ.get('DISABLE_SIGNATURE_VERIFICATION', 'false').lower() == 'true' else 'Enabled'}")

# Configuration for COS event processing
COS_SECRET_KEY = os.environ.get('COS_SECRET_KEY', '')
COS_ENDPOINT = os.environ.get('COS_ENDPOINT', '')
COS_BUCKET_NAME = os.environ.get('COS_BUCKET_NAME', '')
# Allow disabling signature verification for testing
DISABLE_SIGNATURE_VERIFICATION = os.environ.get('DISABLE_SIGNATURE_VERIFICATION', 'false').lower() == 'true'

# Global variable to track PDF uploads (in production, use a database)
pdf_upload_count = 0
pdf_uploads = []

logger.info("📊 PDF Detection System Initialized")
logger.info(f"   - Upload Events Tracked: Object:Put, Object:Post, s3:ObjectCreated:Put, s3:ObjectCreated:Post, s3:ObjectCreated:CompleteMultipartUpload")
logger.info(f"   - PDF Extensions: .pdf")
logger.info(f"   - Filename Patterns: pdf")

def is_pdf_file(object_key):
    """
    Check if the uploaded file is a PDF based on its extension and MIME type
    """
    if not object_key:
        logger.info(f"🔍 PDF Check: Object key is empty or None")
        return False
    
    # Check file extension
    file_extension = os.path.splitext(object_key.lower())[1]
    logger.info(f"🔍 PDF Check: File '{object_key}' has extension '{file_extension}'")
    
    if file_extension == '.pdf':
        logger.info(f"✅ PDF Detected: File '{object_key}' has .pdf extension")
        return True
    
    # Additional check: if the object key contains 'pdf' in the filename
    filename = os.path.basename(object_key.lower())
    if 'pdf' in filename:
        logger.info(f"✅ PDF Detected: File '{object_key}' contains 'pdf' in filename")
        return True
    
    logger.info(f"❌ Not PDF: File '{object_key}' does not match PDF criteria")
    logger.info(f"🔍 File extension: '{file_extension}', filename: '{filename}'")
    return False

def is_upload_event(event_type):
    """
    Check if the event is an upload event
    """
    upload_events = [
        'Object:Put',
        'Object:Post',
        'Object:Write',
        's3:ObjectCreated:Put',
        's3:ObjectCreated:Post',
        's3:ObjectCreated:CompleteMultipartUpload',
        'Put',
        'Post',
        'Create',
        'Upload',
        'Write'
    ]
    
    is_upload = event_type in upload_events
    logger.info(f"🔍 Upload Event Check: '{event_type}' -> {'✅ Upload Event' if is_upload else '❌ Not Upload Event'}")
    logger.info(f"🔍 Available upload events: {upload_events}")
    return is_upload

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint that accepts query parameters
    """
    logger.info(f"🏠 Home endpoint accessed - IP: {request.remote_addr}")
    logger.debug(f"📝 Query parameters received: {dict(request.args)}")
    
    # Get all query parameters
    query_params = dict(request.args)
    
    # Get a specific query parameter (example: 'name')
    name = request.args.get('name', 'World')
    
    # Get another query parameter (example: 'age')
    age = request.args.get('age')
    
    logger.debug(f"📝 Processed parameters - name: '{name}', age: '{age}'")
    
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
    
    logger.info(f"✅ Home endpoint response sent successfully")
    return jsonify(response)

@app.route('/cos/events', methods=['POST'])
def handle_cos_events():
    """
    Handle Cloud Object Storage events
    This endpoint receives webhook notifications from COS
    """
    logger.info(f"📨 COS Event received from IP: {request.remote_addr}")
    logger.info(f"📋 Request Headers: {dict(request.headers)}")
    
    try:
        # Log the incoming request
        logger.info(f"🕐 Processing COS event at {datetime.now()}")
        
        # Get the raw body for signature verification
        raw_body = request.get_data()
        logger.debug(f"📦 Raw request body length: {len(raw_body)} bytes")
        
        # Verify signature if secret key is configured and not disabled
        if COS_SECRET_KEY and not DISABLE_SIGNATURE_VERIFICATION:
            logger.info("🔐 Attempting signature verification...")
            if not verify_cos_signature(request.headers, raw_body):
                logger.warning("❌ Invalid signature received - rejecting request")
                return jsonify({'error': 'Invalid signature'}), 401
            logger.info("✅ Signature verification successful")
        else:
            if not COS_SECRET_KEY:
                logger.warning("⚠️ No secret key configured - skipping signature verification")
            if DISABLE_SIGNATURE_VERIFICATION:
                logger.warning("⚠️ Signature verification disabled for testing")
        
        # Parse the JSON payload
        try:
            event_data = json.loads(raw_body)
            logger.debug(f"📄 JSON payload parsed successfully - Event structure: {list(event_data.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON payload: {e}")
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Process the COS event
        logger.info("🔄 Processing COS events...")
        processed_events = process_cos_events(event_data)
        
        # Log the processed events
        logger.info(f"✅ Successfully processed {len(processed_events)} events")
        for i, event in enumerate(processed_events, 1):
            logger.info(f"   Event {i}: {event.get('event_type', 'Unknown')} - {event.get('object_key', 'Unknown')}")
        
        response_data = {
            'status': 'success',
            'message': f'Processed {len(processed_events)} events',
            'events': processed_events,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"📤 Sending response with {len(processed_events)} processed events")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error processing COS event: {e}")
        logger.exception("🔍 Full exception details:")
        return jsonify({'error': str(e)}), 500

@app.route('/cos/events', methods=['GET'])
def get_cos_events():
    """
    Get recent COS events (for debugging/monitoring)
    """
    logger.info(f"📊 COS Events status requested from IP: {request.remote_addr}")
    
    response_data = {
        'status': 'active',
        'endpoint': '/cos/events',
        'method': 'POST',
        'description': 'COS event webhook endpoint',
        'config': {
            'endpoint': COS_ENDPOINT,
            'bucket': COS_BUCKET_NAME,
            'has_secret': bool(COS_SECRET_KEY)
        }
    }
    
    logger.info(f"✅ COS Events status sent successfully")
    return jsonify(response_data)

def verify_cos_signature(headers, body):
    """
    Verify the signature of the COS webhook
    """
    logger.debug("🔐 Starting signature verification process")
    
    try:
        # Get the signature from headers
        signature = headers.get('X-Cos-Signature')
        if not signature:
            logger.warning("❌ No signature found in headers")
            return False
        
        logger.debug(f"🔐 Found signature in headers: {signature[:20]}...")
        
        # Calculate expected signature
        expected_signature = base64.b64encode(
            hmac.new(
                COS_SECRET_KEY.encode('utf-8'),
                body,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        logger.debug(f"🔐 Calculated expected signature: {expected_signature[:20]}...")
        
        # Compare signatures
        is_valid = hmac.compare_digest(signature, expected_signature)
        logger.info(f"🔐 Signature verification result: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"❌ Error verifying signature: {e}")
        logger.exception("🔍 Signature verification exception details:")
        return False

def process_cos_events(event_data):
    """
    Process COS events and extract relevant information
    """
    logger.info(f"🔄 Starting event processing for data structure: {list(event_data.keys())}")
    logger.info(f"🔍 Full event data: {event_data}")
    processed_events = []
    
    try:
        # Handle different event formats
        if 'Records' in event_data:
            logger.info(f"📋 Processing S3-compatible format with {len(event_data['Records'])} records")
            for i, record in enumerate(event_data['Records'], 1):
                logger.debug(f"🔄 Processing record {i}/{len(event_data['Records'])}")
                event = extract_event_info(record)
                if event:
                    processed_events.append(event)
                    logger.debug(f"✅ Record {i} processed successfully")
                    # Check for PDF upload
                    check_pdf_upload(event)
                else:
                    logger.warning(f"⚠️ Record {i} could not be processed")
                    
        elif 'events' in event_data:
            logger.info(f"📋 Processing IBM COS format with {len(event_data['events'])} events")
            for i, event in enumerate(event_data['events'], 1):
                logger.debug(f"🔄 Processing event {i}/{len(event_data['events'])}")
                processed_event = extract_ibm_cos_event_info(event)
                if processed_event:
                    processed_events.append(processed_event)
                    logger.debug(f"✅ Event {i} processed successfully")
                    # Check for PDF upload
                    check_pdf_upload(processed_event)
                else:
                    logger.warning(f"⚠️ Event {i} could not be processed")
        elif 'bucket' in event_data and ('key' in event_data or 'object_name' in event_data):
            logger.info("📋 Processing direct COS notification format")
            event = extract_direct_cos_event_info(event_data)
            if event:
                processed_events.append(event)
                logger.info("✅ Direct COS event processed successfully")
                logger.info(f"🔍 Extracted event for PDF check: {event}")
                # Check for PDF upload
                logger.info("🔍 Calling check_pdf_upload function...")
                check_pdf_upload(event)
                logger.info("🔍 check_pdf_upload function completed")
            else:
                logger.warning("⚠️ Direct COS event could not be processed")
        elif 'bucket' in event_data and 'notification' in event_data:
            logger.info("📋 Processing direct COS notification format (with nested notification)")
            event = extract_direct_cos_event_info(event_data)
            if event:
                processed_events.append(event)
                logger.info("✅ Direct COS event processed successfully")
                logger.info(f"🔍 Extracted event for PDF check: {event}")
                # Check for PDF upload
                logger.info("🔍 Calling check_pdf_upload function...")
                check_pdf_upload(event)
                logger.info("🔍 check_pdf_upload function completed")
            else:
                logger.warning("⚠️ Direct COS event could not be processed")
        elif 'bucket_name' in event_data and 'object_name' in event_data:
            logger.info("📋 Processing direct COS notification format (bucket_name/object_name)")
            event = extract_direct_cos_event_info(event_data)
            if event:
                processed_events.append(event)
                logger.info("✅ Direct COS event processed successfully")
                logger.info(f"🔍 Extracted event for PDF check: {event}")
                # Check for PDF upload
                logger.info("🔍 Calling check_pdf_upload function...")
                check_pdf_upload(event)
                logger.info("🔍 check_pdf_upload function completed")
            else:
                logger.warning("⚠️ Direct COS event could not be processed")
        else:
            logger.info("📋 Processing single event or unknown format")
            logger.info(f"🔍 Event keys: {list(event_data.keys())}")
            event = extract_event_info(event_data)
            if event:
                processed_events.append(event)
                logger.debug("✅ Single event processed successfully")
                # Check for PDF upload
                check_pdf_upload(event)
            else:
                logger.warning("⚠️ Single event could not be processed")
                
    except Exception as e:
        logger.error(f"❌ Error processing events: {e}")
        logger.exception("🔍 Event processing exception details:")
    
    logger.info(f"✅ Event processing completed - {len(processed_events)} events processed")
    return processed_events

def check_pdf_upload(event):
    """
    Check if the event is a PDF upload and log it
    """
    global pdf_upload_count, pdf_uploads
    
    logger.info("🔍 Starting PDF upload check...")
    
    try:
        event_type = event.get('event_type', '')
        object_key = event.get('object_key', '')
        bucket = event.get('bucket', '')
        
        logger.info(f"🔍 PDF Upload Check: Event '{event_type}' for file '{object_key}' in bucket '{bucket}'")
        logger.info(f"🔍 Full event data: {event}")
        
        # Check if it's an upload event and the file is a PDF
        is_upload = is_upload_event(event_type)
        is_pdf = is_pdf_file(object_key)
        
        logger.info(f"🔍 Upload check result: {is_upload}")
        logger.info(f"🔍 PDF check result: {is_pdf}")
        
        if is_upload and is_pdf:
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
            
            logger.info(f"📊 PDF Upload Statistics Updated: Total count = {pdf_upload_count}, Recent uploads = {len(pdf_uploads)}")
            
            # Keep only the last 100 PDF uploads to prevent memory issues
            if len(pdf_uploads) > 100:
                removed_upload = pdf_uploads.pop(0)
                logger.debug(f"🗑️ Removed old PDF upload from tracking: {removed_upload['file_name']}")
            
            # You can add additional processing here, such as:
            # - Sending notifications
            # - Triggering PDF processing workflows
            # - Updating databases
            # - Calling external services
            
        else:
            if not is_upload:
                logger.info(f"📝 Not an upload event: {event_type}")
            if not is_pdf:
                logger.info(f"📝 Not a PDF file: {object_key}")
            
    except Exception as e:
        logger.error(f"❌ Error checking PDF upload: {e}")
        logger.exception("🔍 PDF upload check exception details:")

def extract_event_info(record):
    """
    Extract event information from S3-compatible format
    """
    logger.debug(f"🔄 Extracting S3 event info from record")
    
    try:
        event_name = record.get('eventName', 'Unknown')
        bucket_name = record.get('s3', {}).get('bucket', {}).get('name', 'Unknown')
        object_key = record.get('s3', {}).get('object', {}).get('key', 'Unknown')
        
        logger.debug(f"📋 S3 Event extracted: {event_name} - {bucket_name}/{object_key}")
        
        return {
            'event_type': event_name,
            'bucket': bucket_name,
            'object_key': object_key,
            'timestamp': record.get('eventTime', datetime.now().isoformat()),
            'source': 's3_compatible'
        }
    except Exception as e:
        logger.error(f"❌ Error extracting S3 event info: {e}")
        logger.exception("🔍 S3 event extraction exception details:")
        return None

def extract_ibm_cos_event_info(event):
    """
    Extract event information from IBM COS format
    """
    logger.debug(f"🔄 Extracting IBM COS event info")
    
    try:
        event_type = event.get('eventType', 'Unknown')
        bucket = event.get('bucket', 'Unknown')
        object_key = event.get('key', 'Unknown')
        
        logger.debug(f"📋 IBM COS Event extracted: {event_type} - {bucket}/{object_key}")
        
        return {
            'event_type': event_type,
            'bucket': bucket,
            'object_key': object_key,
            'timestamp': event.get('time', datetime.now().isoformat()),
            'source': 'ibm_cos'
        }
    except Exception as e:
        logger.error(f"❌ Error extracting IBM COS event info: {e}")
        logger.exception("🔍 IBM COS event extraction exception details:")
        return None

def extract_direct_cos_event_info(event_data):
    """
    Extract event information from direct COS notification format
    """
    logger.info(f"🔄 Extracting direct COS event info")
    logger.info(f"🔍 Raw event data: {event_data}")
    
    try:
        # Check if we have a nested notification structure
        if 'notification' in event_data and isinstance(event_data['notification'], dict):
            logger.info("📋 Detected nested notification structure")
            notification_data = event_data['notification']
            
            # Extract from notification object
            bucket = notification_data.get('bucket_name', event_data.get('bucket', 'Unknown'))
            object_key = notification_data.get('object_name', event_data.get('key', 'Unknown'))
            event_type = notification_data.get('event_type', event_data.get('operation', 'Unknown'))
            
            logger.info(f"📋 Nested notification extracted: bucket={bucket}, object_key={object_key}, event_type={event_type}")
            
        else:
            # Handle different possible field names for bucket
            bucket = event_data.get('bucket', event_data.get('bucket_name', 'Unknown'))
            
            # Handle different possible field names for object key
            object_key = event_data.get('key', event_data.get('object_name', 'Unknown'))
            notification = event_data.get('notification', 'Unknown')
            operation = event_data.get('operation', 'Unknown')
            
            # Handle different possible field names for event type
            event_type = event_data.get('event_type', notification if notification != 'Unknown' else operation)
            
            logger.info(f"📋 Direct COS Event extracted: bucket={bucket}, object_key={object_key}, event_type={event_type}")
        
        extracted_event = {
            'event_type': event_type,
            'bucket': bucket,
            'object_key': object_key,
            'timestamp': datetime.now().isoformat(),
            'source': 'direct_cos'
        }
        
        logger.info(f"📋 Extracted event object: {extracted_event}")
        return extracted_event
        
    except Exception as e:
        logger.error(f"❌ Error extracting direct COS event info: {e}")
        logger.exception("🔍 Direct COS event extraction exception details:")
        return None

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Another endpoint that demonstrates different query parameter handling
    """
    logger.info(f"📊 API Data endpoint accessed from IP: {request.remote_addr}")
    
    # Get query parameters with defaults
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    category = request.args.get('category', 'all')
    
    logger.debug(f"📝 API Data parameters: limit={limit}, offset={offset}, category='{category}'")
    
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
        original_count = len(data['items'])
        data['items'] = [item for item in data['items'] if item['category'] == category]
        logger.debug(f"🔍 Category filter applied: {original_count} -> {len(data['items'])} items")
    
    # Apply pagination
    total_items = len(data['items'])
    data['items'] = data['items'][offset:offset + limit]
    logger.debug(f"📄 Pagination applied: showing {len(data['items'])} of {total_items} items")
    
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
    
    logger.info(f"✅ API Data response sent successfully")
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    logger.info(f"🏥 Health check requested from IP: {request.remote_addr}")
    
    health_status = {
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
    }
    
    logger.info(f"✅ Health check completed - Status: {health_status['status']}")
    logger.debug(f"📊 Health details: COS configured={health_status['cos_configured']}, PDF uploads={health_status['pdf_detection']['total_pdf_uploads']}")
    
    return jsonify(health_status)

@app.route('/pdf/stats', methods=['GET'])
def pdf_stats():
    """
    Get PDF upload statistics
    """
    logger.info(f"📊 PDF Stats requested from IP: {request.remote_addr}")
    
    # Get query parameters for filtering
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    logger.debug(f"📝 PDF Stats parameters: limit={limit}, offset={offset}")
    
    # Get recent PDF uploads with pagination
    recent_uploads = pdf_uploads[offset:offset + limit] if pdf_uploads else []
    
    logger.debug(f"📄 PDF Stats: {len(recent_uploads)} recent uploads retrieved from {len(pdf_uploads)} total tracked")
    
    response_data = {
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
                'Object:Write',
                's3:ObjectCreated:Put',
                's3:ObjectCreated:Post',
                's3:ObjectCreated:CompleteMultipartUpload',
                'Put',
                'Post',
                'Create',
                'Upload',
                'Write'
            ],
            'pdf_extensions': ['.pdf'],
            'filename_patterns': ['pdf']
        },
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"✅ PDF Stats response sent successfully")
    logger.debug(f"📊 PDF Stats summary: {pdf_upload_count} total uploads, {len(recent_uploads)} in current page")
    
    return jsonify(response_data)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"🌐 Starting Flask application on port {port}")
    logger.info(f"🔧 Environment: {'Development' if app.debug else 'Production'}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    
    # Run the app in debug mode for development
    app.run(host='0.0.0.0', port=port, debug=True) 