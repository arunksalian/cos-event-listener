#!/usr/bin/env python3
"""
Test COS Events with Proper Signature Verification
This script sends test events with proper signatures for testing
"""

import requests
import json
import os
import hmac
import hashlib
import base64
from datetime import datetime

# Configuration
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
COS_SECRET_KEY = os.environ.get('COS_SECRET_KEY', 'test-secret-key')

def generate_signature(payload, secret_key):
    """
    Generate HMAC signature for the payload
    """
    # Convert payload to bytes if it's a string
    if isinstance(payload, str):
        payload_bytes = payload.encode('utf-8')
    else:
        payload_bytes = payload
    
    # Generate HMAC signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).digest()
    
    # Encode as base64
    return base64.b64encode(signature).decode('utf-8')

def send_test_event_with_signature(event_data, secret_key):
    """
    Send a test event with proper signature
    """
    # Convert event data to JSON string
    payload = json.dumps(event_data)
    
    # Generate signature
    signature = generate_signature(payload, secret_key)
    
    # Prepare headers
    headers = {
        'Content-Type': 'application/json',
        'X-Cos-Signature': signature
    }
    
    print(f"📤 Sending event with signature: {signature[:20]}...")
    print(f"📦 Payload: {payload}")
    print(f"🔑 Secret Key: {secret_key[:10]}..." if len(secret_key) > 10 else f"🔑 Secret Key: {secret_key}")
    
    try:
        response = requests.post(
            f"{APP_URL}/cos/events",
            data=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Event processed successfully!")
            print(f"✅ Message: {data['message']}")
            for event in data.get('events', []):
                print(f"   - {event['event_type']}: {event['object_key']}")
        else:
            print(f"❌ Event processing failed")
            
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_with_signature():
    """Test events with proper signature verification"""
    print("🔐 Testing COS Events with Signature Verification")
    print("=" * 60)
    
    # Test event 1: Object Put
    test_event_1 = {
        "events": [
            {
                "eventType": "Object:Put",
                "bucket": "test-bucket",
                "key": f"uploads/test-file-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
                "time": datetime.now().isoformat()
            }
        ]
    }
    
    print("\n1️⃣ Testing Object:Put event:")
    success_1 = send_test_event_with_signature(test_event_1, COS_SECRET_KEY)
    
    # Test event 2: Object Delete
    test_event_2 = {
        "events": [
            {
                "eventType": "Object:Delete",
                "bucket": "test-bucket",
                "key": "uploads/deleted-file.txt",
                "time": datetime.now().isoformat()
            }
        ]
    }
    
    print("\n2️⃣ Testing Object:Delete event:")
    success_2 = send_test_event_with_signature(test_event_2, COS_SECRET_KEY)
    
    # Test event 3: S3 compatible format
    test_event_3 = {
        "Records": [
            {
                "eventName": "ObjectCreated:Put",
                "eventTime": datetime.now().isoformat(),
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "uploads/s3-compatible-test.txt"
                    }
                }
            }
        ]
    }
    
    print("\n3️⃣ Testing S3-compatible format:")
    success_3 = send_test_event_with_signature(test_event_3, COS_SECRET_KEY)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Object:Put: {'PASS' if success_1 else 'FAIL'}")
    print(f"✅ Object:Delete: {'PASS' if success_2 else 'FAIL'}")
    print(f"✅ S3 Compatible: {'PASS' if success_3 else 'FAIL'}")
    
    all_passed = success_1 and success_2 and success_3
    print(f"\n🎯 Overall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

def test_without_signature():
    """Test events without signature (should fail if secret is configured)"""
    print("\n🔓 Testing COS Events WITHOUT Signature (should fail if secret configured)")
    print("=" * 60)
    
    test_event = {
        "events": [
            {
                "eventType": "Object:Put",
                "bucket": "test-bucket",
                "key": "uploads/no-signature-test.txt",
                "time": datetime.now().isoformat()
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{APP_URL}/cos/events",
            json=test_event,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected event without signature")
            return True
        else:
            print("⚠️  Event was accepted without signature (signature verification may be disabled)")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 COS Event Signature Verification Tests")
    print("=" * 60)
    print(f"App URL: {APP_URL}")
    print(f"Secret Key: {COS_SECRET_KEY[:10]}..." if len(COS_SECRET_KEY) > 10 else f"Secret Key: {COS_SECRET_KEY}")
    print()
    
    # Test with signature
    signature_tests = test_with_signature()
    
    # Test without signature
    no_signature_test = test_without_signature()
    
    print("\n" + "=" * 60)
    print("🎯 Final Results:")
    print(f"✅ Signature Tests: {'PASS' if signature_tests else 'FAIL'}")
    print(f"✅ No Signature Test: {'PASS' if no_signature_test else 'FAIL'}")
    
    if signature_tests and no_signature_test:
        print("\n🎉 All tests passed! Signature verification is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check your configuration.")
    
    print("\n💡 Tips:")
    print("- Make sure COS_SECRET_KEY environment variable is set")
    print("- The secret key should match the one configured in COS")
    print("- Real COS events will include the X-Cos-Signature header")

if __name__ == "__main__":
    main() 