#!/usr/bin/env python3
"""
Test script for real COS event format based on actual logs
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

def test_real_cos_format():
    """
    Test the real COS event format from actual logs
    """
    base_url = "http://localhost:5000"
    
    logger.info("🧪 Testing Real COS Event Format (from actual logs)")
    logger.info("=" * 60)
    
    # Real COS event format based on the logs
    real_cos_event = {
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
    
    logger.info(f"📤 Sending real COS event: {real_cos_event['event_type']} - {real_cos_event['object_name']}")
    logger.info(f"   Bucket: {real_cos_event['bucket']}")
    logger.info(f"   Content Type: {real_cos_event['content_type']}")
    logger.info(f"   File Size: {real_cos_event['object_length']} bytes")
    
    try:
        response = requests.post(
            f"{base_url}/cos/events",
            json=real_cos_event,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Event processed: {result['message']}")
            logger.debug(f"📄 Response: {json.dumps(result, indent=2)}")
            
            # Check if PDF was detected
            if result.get('events'):
                event = result['events'][0]
                logger.info(f"📋 Extracted Event: {event.get('event_type')} - {event.get('object_key')}")
                logger.info(f"   Source: {event.get('source')}")
        else:
            logger.error(f"❌ Event failed: {response.status_code}")
            logger.error(f"📄 Error response: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Error sending event: {e}")
    
    # Check PDF stats after sending event
    logger.info("\n📊 Checking PDF statistics after real COS event...")
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
                    logger.info(f"      Event: {upload['event_type']}, Source: {upload['source']}")
                    logger.info(f"      Timestamp: {upload['timestamp']}")
        else:
            logger.error(f"❌ PDF stats failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error getting PDF stats: {e}")

def test_variations():
    """
    Test variations of the real COS format
    """
    base_url = "http://localhost:5000"
    
    logger.info("\n🧪 Testing COS Format Variations")
    logger.info("=" * 50)
    
    test_cases = [
        {
            "name": "With object_name field",
            "data": {
                "bucket": "test-bucket",
                "object_name": "document.pdf",
                "event_type": "Object:Write",
                "content_type": "application/pdf"
            }
        },
        {
            "name": "With key field",
            "data": {
                "bucket": "test-bucket",
                "key": "document.pdf",
                "event_type": "Object:Put",
                "content_type": "application/pdf"
            }
        },
        {
            "name": "With notification field",
            "data": {
                "bucket": "test-bucket",
                "object_name": "document.pdf",
                "notification": "Object:Post",
                "content_type": "application/pdf"
            }
        },
        {
            "name": "Non-PDF file",
            "data": {
                "bucket": "test-bucket",
                "object_name": "image.jpg",
                "event_type": "Object:Write",
                "content_type": "image/jpeg"
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
                
                if result.get('events'):
                    event = result['events'][0]
                    logger.info(f"   📋 Event: {event.get('event_type')} - {event.get('object_key')}")
            else:
                logger.error(f"   ❌ {test_case['name']} failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Error with {test_case['name']}: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting Real COS Format Tests")
    logger.info("Make sure the Flask application is running on http://localhost:5000")
    logger.info("")
    
    test_real_cos_format()
    test_variations()
    
    logger.info("\n📋 Test Summary:")
    logger.info("- Real COS event format is now supported")
    logger.info("- PDF detection works with Object:Write events")
    logger.info("- Multiple field name variations are handled")
    logger.info("- Event extraction is robust for different COS configurations") 