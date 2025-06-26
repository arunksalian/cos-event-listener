# Cloud Object Storage Event Listener

A Python Flask application that accepts HTTP GET requests with query parameters and listens to Cloud Object Storage (COS) events via webhooks.

## Features

- Accepts query parameters in GET requests
- Returns JSON responses
- Multiple endpoints for different use cases
- Health check endpoint
- **Cloud Object Storage event listening**
- **Webhook endpoint for COS notifications**
- **Event signature verification**
- **Comprehensive logging**
- **Real-time event monitoring**
- **Event verification tools**
- **PDF file detection and tracking**
- **PDF upload statistics and monitoring**
- **Enhanced logging with multiple levels and rotation**
- **Performance monitoring and metrics**
- **Detailed error tracking and debugging**
- Configurable port via environment variable
- Docker support for easy deployment

## Setup

### Option 1: Local Python Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables for COS:
```bash
export COS_ENDPOINT="your-cos-endpoint"
export COS_BUCKET_NAME="your-bucket-name"
export COS_SECRET_KEY="your-webhook-secret"  # Optional
export APP_URL="http://localhost:5000"  # Your app URL
```

3. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

### Option 2: Docker Setup

#### Using Docker Compose (Recommended)
```bash
# Build and run with docker-compose
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the application
docker-compose down
```

#### Using Docker directly
```bash
# Build the Docker image
docker build -t flask-app .

# Run the container with COS environment variables
docker run -p 5000:5000 \
  -e COS_ENDPOINT="your-cos-endpoint" \
  -e COS_BUCKET_NAME="your-bucket-name" \
  -e COS_SECRET_KEY="your-webhook-secret" \
  flask-app
```

## Cloud Object Storage Event Setup

### 1. Run the Setup Script
```bash
python setup_cos_events.py
```

This script will:
- Check your environment configuration
- Generate a configuration file
- Test your webhook endpoint
- Provide setup instructions

### 2. Configure IBM Cloud Event Notifications (EN) Service

**Important**: IBM Cloud Object Storage uses the **Event Notifications (EN) service** for event-driven triggers, not direct bucket notifications like AWS S3.

#### Step 1: Create Event Notifications Service
1. Go to **IBM Cloud Catalog**
2. Search for **"Event Notifications"**
3. Create a new Event Notifications service instance

#### Step 2: Create Event Source
1. In your Event Notifications instance, go to **"Event sources"**
2. Click **"Create event source"**
3. Select **"Cloud Object Storage"**
4. Configure:
   - **Event source name**: `cos-event-source`
   - **COS instance**: Select your COS instance
   - **Bucket**: Select your bucket
   - **Event types**: Select events you want to listen for

#### Step 3: Create Destination (Webhook)
1. Go to **"Destinations"**
2. Click **"Create destination"**
3. Select **"Webhook"**
4. Configure:
   - **URL**: `https://your-app-url/cos/events`
   - **HTTP method**: `POST`
   - **Content type**: `application/json`
   - **Secret key**: (Optional) For signature verification

#### Step 4: Create Subscription
1. Go to **"Subscriptions"**
2. Click **"Create subscription"**
3. Connect your event source to your webhook destination

### 3. Deploy to IBM Code Engine

```bash
# Build and push your image
docker build -t us.icr.io/suppliq-dev/cos-event-listener:1.0.1 .
docker push us.icr.io/suppliq-dev/cos-event-listener:1.0.1

# Deploy with environment variables
ibmcloud ce app create \
  --name cos-event-listener \
  --image us.icr.io/suppliq-dev/cos-event-listener:1.0.1 \
  --cpu 0.25 \
  --memory 0.5G \
  --port 5000 \
  --env COS_ENDPOINT="your-cos-endpoint" \
  --env COS_BUCKET_NAME="your-bucket-name" \
  --env COS_SECRET_KEY="your-webhook-secret"
```

**For detailed setup instructions, see: [IBM COS Event Notifications Setup Guide](ibm_cos_event_setup.md)**

## Verifying Events Are Captured

### 🔍 **Method 1: Real-time Monitoring**

Use the monitoring script to watch for events in real-time:

```bash
# Set your app URL
export APP_URL="https://your-app-url"

# Run the monitor
python monitor_events.py
```

This will:
- ✅ Check application health
- ✅ Verify COS events endpoint
- ✅ Send test events
- ✅ Monitor continuously for real events

### 🔍 **Method 2: Event Analysis**

Use the event viewer to analyze captured events:

```bash
# Set your app URL
export APP_URL="https://your-app-url"

# Run the viewer
python view_events.py
```

This will:
- 📊 Display application status
- 📊 Show COS configuration
- 📊 Send test events
- 📊 Provide troubleshooting steps

### 🔍 **Method 3: Application Logs**

Check the application logs for event processing:

```bash
# Local development
tail -f app.log

# Docker
docker logs -f flask-container

# IBM Code Engine
ibmcloud ce app logs --name cos-event-listener --follow
```

Look for these log entries:
```
INFO:__main__:Received COS event at 2024-01-15 10:30:00
INFO:__main__:Processed 1 events
```

### 🔍 **Method 4: Manual Testing**

Test the webhook endpoint directly:

```bash
# Test GET request (status check)
curl "https://your-app-url/cos/events"

# Test POST request with sample event
curl -X POST "https://your-app-url/cos/events" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "eventType": "Object:Put",
        "bucket": "test-bucket",
        "key": "uploads/test-file.txt",
        "time": "2024-01-15T10:30:00.000Z"
      }
    ]
  }'
```

### 🔍 **Method 5: Real COS Operations**

Perform actual operations on your COS bucket:

1. **Upload a file** to your COS bucket
2. **Delete a file** from your COS bucket
3. **Copy a file** within your COS bucket
4. **Check application logs** for event processing

### 🔍 **Method 6: IBM Cloud Monitoring**

Check IBM Cloud services for event delivery:

1. **Code Engine Logs**:
   ```bash
   ibmcloud ce app logs --name cos-event-listener
   ```

2. **COS Notification Status**:
   - Go to your COS bucket
   - Check 'Configuration' > 'Event Notifications'
   - View delivery status and history

3. **Activity Tracker** (if enabled):
   - Check for COS API calls
   - Monitor webhook delivery attempts

## Usage Examples

### Home Endpoint (`/`)
Accepts query parameters and returns a greeting message.

```bash
# Basic request
curl "http://localhost:5000/"

# With query parameters
curl "http://localhost:5000/?name=John&age=25"
```

Response:
```json
{
  "message": "Hello, John!",
  "query_parameters": {
    "name": "John",
    "age": "25"
  },
  "specific_params": {
    "name": "John",
    "age": "25"
  },
  "cos_config": {
    "endpoint": "your-cos-endpoint",
    "bucket": "your-bucket-name",
    "has_secret": true
  }
}
```

### COS Events Endpoint (`/cos/events`)
Receives Cloud Object Storage event notifications.

```bash
# Check COS events status
curl "http://localhost:5000/cos/events"

# The endpoint also accepts POST requests from COS
# This is automatically called when files are uploaded/deleted
```

### Data API Endpoint (`/api/data`)
Demonstrates pagination and filtering with query parameters.

```bash
# Basic request
curl "http://localhost:5000/api/data"

# With pagination
curl "http://localhost:5000/api/data?limit=2&offset=1"

# With category filter
curl "http://localhost:5000/api/data?category=tech"

# Combined parameters
curl "http://localhost:5000/api/data?limit=1&offset=0&category=tech"
```

### Health Check Endpoint (`/health`)
Simple health check endpoint with COS status.

```bash
curl "http://localhost:5000/health"
```

Response:
```json
{
  "status": "healthy",
  "message": "Server is running",
  "cos_configured": true,
  "pdf_detection": {
    "enabled": true,
    "total_pdf_uploads": 5
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### PDF Statistics Endpoint (`/pdf/stats`)
Get PDF upload statistics and recent uploads.

```bash
# Get basic PDF stats
curl "http://localhost:5000/pdf/stats"

# Get PDF stats with pagination
curl "http://localhost:5000/pdf/stats?limit=5&offset=0"
```

Response:
```json
{
  "pdf_upload_statistics": {
    "total_pdf_uploads": 5,
    "recent_uploads_count": 3,
    "uploads_tracked": 5
  },
  "recent_pdf_uploads": [
    {
      "file_name": "documents/report.pdf",
      "bucket": "my-bucket",
      "event_type": "Object:Put",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "source": "ibm_cos"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 5
  },
  "detection_config": {
    "upload_events": [
      "Object:Put",
      "Object:Post",
      "s3:ObjectCreated:Put",
      "s3:ObjectCreated:Post",
      "s3:ObjectCreated:CompleteMultipartUpload"
    ],
    "pdf_extensions": [".pdf"],
    "filename_patterns": ["pdf"]
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Environment Variables

- `PORT`: Set the port number (default: 5000)
- `FLASK_ENV`: Set Flask environment (development/production)
- `COS_ENDPOINT`: Your COS endpoint URL
- `COS_BUCKET_NAME`: Your COS bucket name
- `COS_SECRET_KEY`: Secret key for webhook signature verification
- `COS_API_KEY`: Your IBM Cloud API key
- `COS_INSTANCE_ID`: Your COS instance ID
- `COS_REGION`: Your COS region (default: us-south)
- `APP_URL`: Your application URL for webhook configuration
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Log file path (default: app.log)
- `DISABLE_SIGNATURE_VERIFICATION`: Disable signature verification for testing (default: false)

Example:
```bash
export COS_ENDPOINT="https://s3.us-south.cloud-object-storage.appdomain.cloud"
export COS_BUCKET_NAME="my-bucket"
export COS_SECRET_KEY="my-webhook-secret"
export APP_URL="https://cos-event-listener.xyz.us-south.codeengine.appdomain.cloud"
export LOG_LEVEL="DEBUG"
export LOG_FILE="app.log"
```

## COS Event Types

The application listens for the following COS events:
- `Object:Put` - File upload
- `Object:Post` - File upload via POST
- `Object:Delete` - File deletion
- `Object:Copy` - File copy
- `Object:CompleteMultipartUpload` - Multipart upload completion
- `Object:AbortMultipartUpload` - Multipart upload abortion

## PDF Detection and Tracking

The application automatically detects and tracks PDF file uploads with the following features:

### PDF Detection Logic
- **File Extension**: Detects files with `.pdf` extension
- **Filename Pattern**: Detects files with "pdf" in the filename
- **Upload Events**: Monitors upload events (`Object:Put`, `Object:Post`, etc.)
- **Real-time Logging**: Logs PDF uploads with detailed information

### Detection Events
The following upload events trigger PDF detection:
- `Object:Put` - Standard file upload
- `Object:Post` - File upload via POST
- `s3:ObjectCreated:Put` - S3-compatible upload
- `s3:ObjectCreated:Post` - S3-compatible POST upload
- `s3:ObjectCreated:CompleteMultipartUpload` - Multipart upload completion

### PDF Upload Logging
When a PDF upload is detected, the application logs:
```
📄 PDF UPLOAD DETECTED: File 'documents/report.pdf' uploaded to bucket 'my-bucket' at 2024-01-15T10:30:00.000Z
📄 PDF Details: Event Type: Object:Put, Source: ibm_cos
```

### Statistics Tracking
- **Total PDF Uploads**: Count of all PDF uploads since application start
- **Recent Uploads**: List of recent PDF uploads (last 100)
- **Upload Details**: File name, bucket, event type, timestamp, and source

### Extensibility
The PDF detection system is designed for easy extension:
- Add custom file type detection
- Integrate with external services
- Trigger PDF processing workflows
- Send notifications
- Update databases

## Enhanced Logging System

The application includes a comprehensive logging system with multiple features:

### Logging Features
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Dual Output**: Console and file logging
- **Log Rotation**: Automatic log file rotation with size limits
- **Separate Error Logs**: Dedicated error log files
- **Structured Format**: Detailed timestamps and context information
- **Performance Tracking**: Request timing and performance metrics
- **Request/Response Logging**: Complete HTTP request/response details

### Log Configuration
```bash
# Set log level
export LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Set log file path
export LOG_FILE="app.log"

# Default configuration
LOG_LEVEL=INFO
LOG_FILE=app.log
MAX_LOG_SIZE=10MB
BACKUP_COUNT=5
```

### Log Output Examples

#### Application Startup
```
2024-01-15 10:30:00 - __main__ - INFO - 🚀 Starting Cloud Object Storage Event Listener
2024-01-15 10:30:00 - __main__ - INFO - 📋 Application Configuration:
2024-01-15 10:30:00 - __main__ - INFO -    - COS Endpoint: Configured
2024-01-15 10:30:00 - __main__ - INFO -    - COS Bucket: Configured
2024-01-15 10:30:00 - __main__ - INFO - 📊 PDF Detection System Initialized
```

#### COS Event Processing
```
2024-01-15 10:30:05 - __main__ - INFO - 📨 COS Event received from IP: 192.168.1.100
2024-01-15 10:30:05 - __main__ - INFO - 🔐 Attempting signature verification...
2024-01-15 10:30:05 - __main__ - INFO - ✅ Signature verification successful
2024-01-15 10:30:05 - __main__ - INFO - 🔄 Processing COS events...
2024-01-15 10:30:05 - __main__ - INFO - 📋 Processing IBM COS format with 1 events
2024-01-15 10:30:05 - __main__ - INFO - ✅ Successfully processed 1 events
2024-01-15 10:30:05 - __main__ - INFO -    Event 1: Object:Put - documents/report.pdf
```

#### PDF Detection
```
2024-01-15 10:30:05 - __main__ - INFO - 📄 PDF UPLOAD DETECTED: File 'documents/report.pdf' uploaded to bucket 'my-bucket' at 2024-01-15T10:30:05.000Z
2024-01-15 10:30:05 - __main__ - INFO - 📄 PDF Details: Event Type: Object:Put, Source: ibm_cos
2024-01-15 10:30:05 - __main__ - INFO - 📊 PDF Upload Statistics Updated: Total count = 1, Recent uploads = 1
```

#### Performance Metrics
```
2024-01-15 10:30:05 - __main__ - INFO - ⏱️ Performance: COS event processing completed in 0.045 seconds
2024-01-15 10:30:05 - __main__ - INFO - 📤 Sending response with 1 processed events
```

### Log Files
- `app.log`: Main application log with all levels
- `app_error.log`: Error-only log file
- Console output: Real-time logging to terminal

### Debugging with Logs
The enhanced logging system provides comprehensive debugging information:

1. **Request Tracking**: Every HTTP request is logged with details
2. **Event Processing**: Step-by-step COS event processing logs
3. **PDF Detection**: Detailed PDF file detection and tracking
4. **Performance**: Timing information for all operations
5. **Error Context**: Full exception details with stack traces
6. **Configuration**: Application startup and configuration logs

### Log Analysis
```bash
# View recent logs
tail -f app.log

# Search for PDF uploads
grep "PDF UPLOAD DETECTED" app.log

# Search for errors
grep "ERROR" app_error.log

# Monitor performance
grep "Performance:" app.log

# Track specific events
grep "Object:Put" app.log
```

## Event Processing

When a COS event is received:

1. **Signature Verification**: If `COS_SECRET_KEY` is set, the webhook signature is verified
2. **Event Parsing**: The JSON payload is parsed and validated
3. **Event Extraction**: Relevant information is extracted (bucket, object key, event type)
4. **Logging**: All events are logged for monitoring
5. **Response**: A success response is returned to COS

### Supported Event Formats

The application supports multiple COS event formats:

#### 1. IBM COS Format (Standard)
```json
{
  "events": [
    {
      "eventType": "Object:Put",
      "bucket": "my-bucket",
      "key": "uploads/document.pdf",
      "time": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

#### 2. S3-Compatible Format
```json
{
  "Records": [
    {
      "eventName": "s3:ObjectCreated:Put",
      "eventTime": "2024-01-15T10:30:00.000Z",
      "s3": {
        "bucket": {
          "name": "my-bucket"
        },
        "object": {
          "key": "uploads/document.pdf"
        }
      }
    }
  ]
}
```

#### 3. Direct COS Notification Format
```json
{
  "bucket": "my-bucket",
  "endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
  "key": "uploads/document.pdf",
  "notification": "Object:Put",
  "operation": "Put"
}
```

#### 4. Real COS Event Format (Enhanced)
```json
{
  "bucket": "bucket-redact-test",
  "endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
  "key": "MyTheron - Architecture.pdf",
  "notification": "Object:Write",
  "operation": "Write",
  "event_type": "Object:Write",
  "object_name": "MyTheron - Architecture.pdf",
  "content_type": "application/pdf",
  "object_length": "387865",
  "object_etag": "e7a674fd5d11958e378721dca5dafbfc",
  "request_id": "1e367faf-700c-4cc0-99ec-eb30d109d9fe",
  "request_time": "2025-06-26T07:07:13.192Z",
  "format": "2.0"
}
```

**Note**: The application now supports multiple field name variations:
- Object key: `key` or `object_name`
- Event type: `event_type`, `notification`, or `operation`

### Sample Event Response
```json
{
  "status": "success",
  "message": "Processed 1 events",
  "events": [
    {
      "event_type": "Object:Put",
      "bucket": "my-bucket",
      "object_key": "uploads/document.pdf",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "source": "ibm_cos"
    }
  ],
  "timestamp": "2024-01-15T10:30:01.000Z"
}
```

## Docker Configuration

### Dockerfile Features
- Uses Python 3.11 slim image for smaller size
- Multi-stage build for optimization
- Non-root user for security
- Health check endpoint
- Proper layer caching

### Docker Compose Features
- Easy development setup
- Volume mounting for live code changes
- Health checks and restart policies
- Optional nginx reverse proxy (commented)
- Environment variable configuration

### Production Deployment
For production deployment, consider:
1. Using a production WSGI server like Gunicorn
2. Adding nginx as a reverse proxy
3. Setting up proper logging
4. Using environment-specific configurations
5. Configuring COS event notifications

Example production docker-compose:
```yaml
version: '3.8'
services:
  flask-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - PORT=5000
      - COS_ENDPOINT=${COS_ENDPOINT}
      - COS_BUCKET_NAME=${COS_BUCKET_NAME}
      - COS_SECRET_KEY=${COS_SECRET_KEY}
    restart: unless-stopped
    # Remove volume mount for production
```

## Query Parameter Handling

The application demonstrates several ways to handle query parameters:

1. **Getting all parameters**: `dict(request.args)`
2. **Getting specific parameters with defaults**: `request.args.get('name', 'World')`
3. **Type conversion**: `request.args.get('limit', 10, type=int)`
4. **Optional parameters**: `request.args.get('age')` (returns None if not provided)

## Development

The application runs in debug mode by default, which enables:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar (if installed)

## Testing

### Local Testing
```bash
python test_app.py
```

### Docker Testing
```bash
# Test the running container
curl "http://localhost:5000/health"
curl "http://localhost:5000/?name=Test"
curl "http://localhost:5000/cos/events"
```

### COS Event Testing
1. Upload a file to your COS bucket
2. Check the application logs for the event
3. Verify the event was processed correctly

### PDF Detection Testing
```bash
# Run comprehensive PDF detection tests
python test_pdf_detection.py
```

This test script will:
- ✅ Check application health and PDF detection status
- ✅ Verify PDF statistics endpoint
- ✅ Send test PDF upload events
- ✅ Test both IBM COS and S3-compatible formats
- ✅ Verify PDF detection and logging
- ✅ Check updated statistics

### Direct COS Format Testing
```bash
# Test direct COS notification format
python test_direct_cos_format.py
```

This test script will:
- ✅ Test direct COS notification format handling
- ✅ Verify mixed event format support
- ✅ Test PDF detection with direct COS format
- ✅ Validate event extraction for different configurations

### Real COS Format Testing
```bash
# Test real COS event format (from actual logs)
python test_real_cos_format.py
```

This test script will:
- ✅ Test real COS event format based on actual production logs
- ✅ Verify PDF detection with Object:Write events
- ✅ Test multiple field name variations (key, object_name, event_type, notification)
- ✅ Validate robust event extraction for different COS configurations

### Event Verification Testing
```bash
# Run comprehensive tests
python test_app.py

# Monitor events in real-time
python monitor_events.py

# Analyze event processing
python view_events.py
```

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**:
   - Check if your app URL is accessible
   - Verify COS notification configuration
   - Check application logs

2. **Signature verification failing**:
   - Ensure `COS_SECRET_KEY` matches the one in COS settings
   - Check if the secret key is properly set

3. **Events not being processed**:
   - Check application logs for errors
   - Verify event format compatibility
   - Ensure all required environment variables are set

4. **Events not being captured**:
   - Run `python monitor_events.py` to check connectivity
   - Verify COS notification is properly configured
   - Check if your app is accessible from the internet
   - Review IBM Cloud logs for delivery status

5. **Events showing as "Unknown" in logs**:
   - This indicates the event format is not recognized
   - Check the event structure in logs: `data structure: ['bucket', 'endpoint', 'key', 'notification', 'operation']`
   - The application now supports direct COS notification format
   - Run `python test_direct_cos_format.py` to verify format handling

6. **PDF detection not working**:
   - Verify the event is an upload event (Object:Put, Object:Post, etc.)
   - Check if the file has a .pdf extension or contains "pdf" in the filename
   - Review logs for PDF detection messages
   - Test with `python test_pdf_detection.py`

### Event Format Troubleshooting

If you see logs like:
```
📋 Processing single event or unknown format
✅ Event processing completed - 1 events processed
   Event 1: Unknown - Unknown
```

This means the event format is not being recognized. The application now supports:

1. **IBM COS Format**: `{"events": [...]}`
2. **S3-Compatible Format**: `{"Records": [...]}`
3. **Direct COS Format**: `{"bucket": "...", "key": "...", "notification": "...", "operation": "..."}`

To debug event format issues:
```bash
# Check the event structure in logs
grep "data structure:" app.log

# Test with different formats
python test_direct_cos_format.py

# Enable debug logging
export LOG_LEVEL="DEBUG"
```

### Logs
The application logs all COS events and errors. Check the logs for:
- Incoming webhook requests
- Event processing results
- Signature verification status
- Error messages

### Verification Checklist

Use this checklist to verify events are being captured:

- [ ] Application is running and accessible
- [ ] COS environment variables are set
- [ ] COS notification is configured
- [ ] Webhook URL is correct and accessible
- [ ] Event types are selected in COS
- [ ] Application logs show incoming requests
- [ ] Test events are processed successfully
- [ ] Real COS operations trigger events
- [ ] No errors in application logs
- [ ] IBM Cloud logs show successful delivery 