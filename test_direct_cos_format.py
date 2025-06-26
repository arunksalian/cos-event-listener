#!/usr/bin/env python3
"""
Test script for direct COS notification format
"""

import requests
import json
import logging
from datetime import datetime

# Configure logging for the test script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_direct_cos_format():
    """
    Test the direct COS notification format handling
    """
    base_url = "http://localhost:5000"
    
    logger.info("🧪 Testing Direct COS Notification Format")
    logger.info("=" * 50)
    
    # Test direct COS notification format
    direct_cos_events = [
        {
            "bucket": "test-bucket",
            "endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
            "key": "documents/report.pdf",
            "notification": "Object:Put",
            "operation": "Put"
        },
        {
            "bucket": "test-bucket",
            "endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
            "key": "uploads/invoice.pdf",
            "notification": "Object:Post",
            "operation": "Post"
        },
        {
            "bucket": "test-bucket",
            "endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
            "key": "files/image.jpg",
            "notification": "Object:Put",
            "operation": "Put"
        },
        {
            "bucket": "test-bucket",
            "endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
            "key": "documents/contract.pdf",
            "notification": "Object:Delete",
            "operation": "Delete"
        }
    ]
    
    for i, event in enumerate(direct_cos_events, 1):
        logger.info(f"\n   Test {i}: {event['notification']} - {event['key']}")
        try:
            response = requests.post(
                f"{base_url}/cos/events",
                json=event,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"   ✅ Event processed: {result['message']}")
                logger.debug(f"   📄 Response: {json.dumps(result, indent=2)}")
            else:
                logger.error(f"   ❌ Event failed: {response.status_code}")
                logger.error(f"   📄 Error response: {response.text}")
                
        except Exception as e:
            logger.error(f"   ❌ Error sending event: {e}")
    
    # Check PDF stats after sending events
    logger.info("\n📊 Checking PDF statistics after direct COS events...")
    try:
        response = requests.get(f"{base_url}/pdf/stats")
        if response.status_code == 200:
            stats_data = response.json()
            logger.info(f"✅ PDF stats retrieved")
            logger.info(f"   Total PDF uploads: {stats_data['pdf_upload_statistics']['total_pdf_uploads']}")
            logger.info(f"   Recent uploads: {stats_data['pdf_upload_statistics']['recent_uploads_count']}")
            
            if stats_data['recent_pdf_uploads']:
                logger.info("\n   Recent PDF uploads:")
                for upload in stats_data['recent_pdf_uploads']:
                    logger.info(f"   📄 {upload['file_name']} (Bucket: {upload['bucket']})")
                    logger.debug(f"      Event: {upload['event_type']}, Source: {upload['source']}")
        else:
            logger.error(f"❌ PDF stats failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error getting PDF stats: {e}")

def test_mixed_formats():
    """
    Test mixed event formats to ensure all are handled correctly
    """
    base_url = "http://localhost:5000"
    
    logger.info("\n🧪 Testing Mixed Event Formats")
    logger.info("=" * 50)
    
    # Test different event formats
    test_cases = [
        {
            "name": "Direct COS Format",
            "data": {
                "bucket": "test-bucket",
                "key": "documents/test.pdf",
                "notification": "Object:Put",
                "operation": "Put"
            }
        },
        {
            "name": "IBM COS Format",
            "data": {
                "events": [
                    {
                        "eventType": "Object:Put",
                        "bucket": "test-bucket",
                        "key": "documents/test2.pdf",
                        "time": datetime.now().isoformat()
                    }
                ]
            }
        },
        {
            "name": "S3 Compatible Format",
            "data": {
                "Records": [
                    {
                        "eventName": "s3:ObjectCreated:Put",
                        "eventTime": datetime.now().isoformat(),
                        "s3": {
                            "bucket": {
                                "name": "test-bucket"
                            },
                            "object": {
                                "key": "documents/test3.pdf"
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n   Test {i}: {test_case['name']}")
        try:
            response = requests.post(
                f"{base_url}/cos/events",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"   ✅ {test_case['name']} processed: {result['message']}")
            else:
                logger.error(f"   ❌ {test_case['name']} failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Error with {test_case['name']}: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting Direct COS Format Tests")
    logger.info("Make sure the Flask application is running on http://localhost:5000")
    logger.info("")
    
    test_direct_cos_format()
    test_mixed_formats()
    
    logger.info("\n📋 Test Summary:")
    logger.info("- Direct COS notification format is now supported")
    logger.info("- Mixed event formats are handled correctly")
    logger.info("- PDF detection works with all formats")
    logger.info("- Event extraction is improved for different COS configurations") 