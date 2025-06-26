#!/usr/bin/env python3
"""
Quick Test for COS Events
This script provides multiple ways to test COS events
"""

import requests
import json
import os
from datetime import datetime

# Configuration
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')

def test_without_signature():
    """Test without signature verification (for testing)"""
    print("🔓 Testing WITHOUT signature verification")
    print("=" * 50)
    
    test_event = {
        "events": [
            {
                "eventType": "Object:Put",
                "bucket": "test-bucket",
                "key": f"uploads/test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
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
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Event processed without signature")
            return True
        elif response.status_code == 401:
            print("❌ FAILED! Signature verification is enabled")
            print("💡 Solution: Set DISABLE_SIGNATURE_VERIFICATION=true")
            return False
        else:
            print(f"❌ FAILED! Unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def check_app_status():
    """Check application status and signature configuration"""
    print("📊 Checking Application Status")
    print("=" * 50)
    
    try:
        response = requests.get(f"{APP_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ App Status: {data['status']}")
            print(f"✅ COS Configured: {data['cos_configured']}")
            
            sig_config = data.get('signature_verification', {})
            print(f"✅ Signature Enabled: {sig_config.get('enabled', False)}")
            print(f"✅ Secret Configured: {sig_config.get('secret_configured', False)}")
            print(f"✅ Disabled for Testing: {sig_config.get('disabled_for_testing', False)}")
            
            return data
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 Quick COS Event Test")
    print("=" * 60)
    print(f"App URL: {APP_URL}")
    print()
    
    # Check app status first
    status = check_app_status()
    if not status:
        print("❌ Cannot connect to application")
        return
    
    print()
    
    # Test without signature
    success = test_without_signature()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Your COS event listener is working!")
        print("\n💡 Next steps:")
        print("1. Upload files to your COS bucket")
        print("2. Check application logs for events")
        print("3. Use python monitor_events.py for real-time monitoring")
    else:
        print("❌ TEST FAILED!")
        print("\n🔧 Solutions:")
        print("1. Set environment variable: export DISABLE_SIGNATURE_VERIFICATION=true")
        print("2. Or use the proper signature test: python test_with_signature.py")
        print("3. Or unset COS_SECRET_KEY to disable signature verification")

if __name__ == "__main__":
    main() 