#!/usr/bin/env python3
"""
Debug Signature Verification
This script helps troubleshoot signature verification issues
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
    """Generate HMAC signature for the payload"""
    if isinstance(payload, str):
        payload_bytes = payload.encode('utf-8')
    else:
        payload_bytes = payload
    
    signature = hmac.new(
        secret_key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).digest()
    
    return base64.b64encode(signature).decode('utf-8')

def check_app_configuration():
    """Check application signature configuration"""
    print("🔍 Checking Application Configuration")
    print("=" * 50)
    
    try:
        response = requests.get(f"{APP_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            sig_config = data.get('signature_verification', {})
            
            print(f"✅ App Status: {data['status']}")
            print(f"✅ COS Configured: {data['cos_configured']}")
            print(f"✅ Signature Enabled: {sig_config.get('enabled', False)}")
            print(f"✅ Secret Configured: {sig_config.get('secret_configured', False)}")
            print(f"✅ Disabled for Testing: {sig_config.get('disabled_for_testing', False)}")
            
            return sig_config
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        return None

def test_signature_generation():
    """Test signature generation and verification"""
    print("\n🔐 Testing Signature Generation")
    print("=" * 50)
    
    # Test payload
    test_event = {
        "events": [
            {
                "eventType": "Object:Put",
                "bucket": "test-bucket",
                "key": "uploads/debug-test.txt",
                "time": datetime.now().isoformat()
            }
        ]
    }
    
    payload = json.dumps(test_event)
    expected_signature = generate_signature(payload, COS_SECRET_KEY)
    
    print(f"📦 Payload: {payload}")
    print(f"🔑 Secret Key: {COS_SECRET_KEY[:10]}..." if len(COS_SECRET_KEY) > 10 else f"🔑 Secret Key: {COS_SECRET_KEY}")
    print(f"🔐 Expected Signature: {expected_signature}")
    
    return payload, expected_signature

def test_with_correct_signature(payload, signature):
    """Test with the correct signature"""
    print("\n✅ Testing with Correct Signature")
    print("=" * 50)
    
    headers = {
        'Content-Type': 'application/json',
        'X-Cos-Signature': signature
    }
    
    try:
        response = requests.post(
            f"{APP_URL}/cos/events",
            data=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Signature verification passed")
            return True
        else:
            print("❌ FAILED! Even with correct signature")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def show_postman_debug_info(payload, signature):
    """Show debug information for Postman"""
    print("\n📋 Postman Debug Information")
    print("=" * 50)
    
    print("🔧 Environment Variables to set in Postman:")
    print(f"   app_url: {APP_URL}")
    print(f"   cos_secret_key: {COS_SECRET_KEY}")
    
    print("\n🔧 Pre-request Script for Postman:")
    print("```javascript")
    print("const requestBody = pm.request.body.raw;")
    print("const secretKey = pm.environment.get('cos_secret_key');")
    print("")
    print("if (requestBody && secretKey) {")
    print("    const signature = CryptoJS.HmacSHA256(requestBody, secretKey);")
    print("    const base64Signature = signature.toString(CryptoJS.enc.Base64);")
    print("    ")
    print("    pm.request.headers.remove('X-Cos-Signature');")
    print("    pm.request.headers.add({")
    print("        key: 'X-Cos-Signature',")
    print("        value: base64Signature")
    print("    });")
    print("    ")
    print("    console.log('Generated signature:', base64Signature);")
    print("    console.log('Expected signature:', '" + signature + "');")
    print("}")
    print("```")
    
    print("\n🔧 Request Configuration:")
    print(f"   Method: POST")
    print(f"   URL: {APP_URL}/cos/events")
    print(f"   Headers: Content-Type: application/json")
    print(f"   Body: {payload}")

def main():
    """Main debug function"""
    print("🐛 COS Event Signature Debug Tool")
    print("=" * 60)
    print(f"App URL: {APP_URL}")
    print(f"Secret Key: {COS_SECRET_KEY[:10]}..." if len(COS_SECRET_KEY) > 10 else f"Secret Key: {COS_SECRET_KEY}")
    print()
    
    # Check app configuration
    sig_config = check_app_configuration()
    if not sig_config:
        print("❌ Cannot connect to application")
        return
    
    # Test signature generation
    payload, expected_signature = test_signature_generation()
    
    # Test with correct signature
    correct_test = test_with_correct_signature(payload, expected_signature)
    
    # Show Postman debug info
    show_postman_debug_info(payload, expected_signature)
    
    print("\n" + "=" * 60)
    print("🎯 Debug Results:")
    print(f"✅ Correct Signature: {'PASS' if correct_test else 'FAIL'}")
    
    if correct_test:
        print("\n🎉 Signature verification is working correctly.")
        print("💡 If Postman is still failing, check the debug information above.")
    else:
        print("\n⚠️  Signature verification failed.")
    
    print("\n🔧 Quick Fix Options:")
    print("1. Set DISABLE_SIGNATURE_VERIFICATION=true for testing")
    print("2. Use the exact signature shown above in Postman")
    print("3. Check that your secret key matches the one in COS")

if __name__ == "__main__":
    main() 