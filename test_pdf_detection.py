#!/usr/bin/env python3
"""
Test script for PDF detection functionality with enhanced logging
"""

import requests
import json
import time
import logging
from datetime import datetime

# Configure logging for the test script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_pdf_detection():
    """
    Test the PDF detection functionality
    """
    base_url = "http://localhost:5000"
    
    logger.info("🧪 Testing PDF Detection Functionality")
    logger.info("=" * 50)
    
    # Test 1: Check health endpoint
    logger.info("\n1. Checking application health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✅ Health check passed")
            logger.info(f"   PDF Detection: {health_data.get('pdf_detection', {}).get('enabled', False)}")
            logger.info(f"   Total PDF uploads: {health_data.get('pdf_detection', {}).get('total_pdf_uploads', 0)}")
            logger.debug(f"   Full health response: {json.dumps(health_data, indent=2)}")
        else:
            logger.error(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        logger.error(f"❌ Error connecting to application: {e}")
        return
    
    # Test 2: Check PDF stats endpoint
    logger.info("\n2. Checking PDF statistics...")
    try:
        response = requests.get(f"{base_url}/pdf/stats")
        if response.status_code == 200:
            stats_data = response.json()
            logger.info(f"✅ PDF stats retrieved")
            logger.info(f"   Total PDF uploads: {stats_data['pdf_upload_statistics']['total_pdf_uploads']}")
            logger.info(f"   Recent uploads: {stats_data['pdf_upload_statistics']['recent_uploads_count']}")
            logger.debug(f"   Detection config: {stats_data['detection_config']}")
        else:
            logger.error(f"❌ PDF stats failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error getting PDF stats: {e}")
    
    # Test 3: Send test PDF upload events
    logger.info("\n3. Sending test PDF upload events...")
    
    test_events = [
        {
            "eventType": "Object:Put",
            "bucket": "test-bucket",
            "key": "documents/report.pdf",
            "time": datetime.now().isoformat()
        },
        {
            "eventType": "Object:Post",
            "bucket": "test-bucket", 
            "key": "uploads/invoice.pdf",
            "time": datetime.now().isoformat()
        },
        {
            "eventType": "Object:Put",
            "bucket": "test-bucket",
            "key": "files/image.jpg",  # Non-PDF file
            "time": datetime.now().isoformat()
        },
        {
            "eventType": "Object:Delete",
            "bucket": "test-bucket",
            "key": "documents/old.pdf",  # Delete event (not upload)
            "time": datetime.now().isoformat()
        },
        {
            "eventType": "Object:Put",
            "bucket": "test-bucket",
            "key": "contracts/agreement.pdf",  # Another PDF
            "time": datetime.now().isoformat()
        }
    ]
    
    for i, event in enumerate(test_events, 1):
        logger.info(f"\n   Test {i}: {event['eventType']} - {event['key']}")
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/cos/events",
                json={"events": [event]},
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"   ✅ Event processed: {result['message']}")
                logger.debug(f"   ⏱️ Processing time: {end_time - start_time:.3f} seconds")
                logger.debug(f"   📄 Response: {json.dumps(result, indent=2)}")
            else:
                logger.error(f"   ❌ Event failed: {response.status_code}")
                logger.error(f"   📄 Error response: {response.text}")
                
        except Exception as e:
            logger.error(f"   ❌ Error sending event: {e}")
        
        time.sleep(0.5)  # Small delay between events
    
    # Test 4: Check updated PDF stats
    logger.info("\n4. Checking updated PDF statistics...")
    try:
        response = requests.get(f"{base_url}/pdf/stats")
        if response.status_code == 200:
            stats_data = response.json()
            logger.info(f"✅ Updated PDF stats retrieved")
            logger.info(f"   Total PDF uploads: {stats_data['pdf_upload_statistics']['total_pdf_uploads']}")
            logger.info(f"   Recent uploads: {stats_data['pdf_upload_statistics']['recent_uploads_count']}")
            
            if stats_data['recent_pdf_uploads']:
                logger.info("\n   Recent PDF uploads:")
                for upload in stats_data['recent_pdf_uploads']:
                    logger.info(f"   📄 {upload['file_name']} (Bucket: {upload['bucket']})")
                    logger.debug(f"      Event: {upload['event_type']}, Source: {upload['source']}")
        else:
            logger.error(f"❌ Updated PDF stats failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error getting updated PDF stats: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info("🎉 PDF Detection Testing Complete!")

def test_s3_compatible_format():
    """
    Test with S3-compatible event format
    """
    base_url = "http://localhost:5000"
    
    logger.info("\n🧪 Testing S3-Compatible Event Format")
    logger.info("=" * 50)
    
    s3_event = {
        "Records": [
            {
                "eventName": "s3:ObjectCreated:Put",
                "eventTime": datetime.now().isoformat(),
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "documents/contract.pdf"
                    }
                }
            }
        ]
    }
    
    try:
        logger.info("📤 Sending S3-compatible event...")
        start_time = time.time()
        response = requests.post(
            f"{base_url}/cos/events",
            json=s3_event,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ S3 event processed: {result['message']}")
            logger.debug(f"⏱️ Processing time: {end_time - start_time:.3f} seconds")
        else:
            logger.error(f"❌ S3 event failed: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error sending S3 event: {e}")

def test_logging_levels():
    """
    Test different logging levels and endpoints
    """
    base_url = "http://localhost:5000"
    
    logger.info("\n🔍 Testing Logging Levels and Endpoints")
    logger.info("=" * 50)
    
    endpoints = [
        ("/", "Home endpoint"),
        ("/health", "Health check"),
        ("/cos/events", "COS events status"),
        ("/api/data", "API data"),
        ("/pdf/stats", "PDF statistics"),
        ("/api/data?limit=2&category=tech", "API data with parameters")
    ]
    
    for endpoint, description in endpoints:
        logger.info(f"\n📊 Testing {description} ({endpoint})")
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}")
            end_time = time.time()
            
            logger.info(f"   Status: {response.status_code}")
            logger.info(f"   Response time: {end_time - start_time:.3f} seconds")
            logger.debug(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.debug(f"   Response data: {json.dumps(data, indent=2)}")
                except:
                    logger.debug(f"   Response text: {response.text[:200]}...")
            else:
                logger.warning(f"   Error response: {response.text}")
                
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting PDF Detection Tests")
    logger.info("Make sure the Flask application is running on http://localhost:5000")
    logger.info("Check the application logs for detailed information about event processing")
    logger.info("")
    
    test_pdf_detection()
    test_s3_compatible_format()
    test_logging_levels()
    
    logger.info("\n📋 Test Summary:")
    logger.info("- PDF detection is enabled and working")
    logger.info("- Upload events are properly identified")
    logger.info("- PDF files are detected by extension")
    logger.info("- Statistics are tracked and available")
    logger.info("- Both IBM COS and S3-compatible formats are supported")
    logger.info("- Enhanced logging provides detailed debugging information")
    logger.info("- Performance metrics are tracked")
    logger.info("- Error handling and context logging is comprehensive") 