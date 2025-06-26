#!/usr/bin/env python3
"""
COS Event Viewer
View and analyze captured COS events
"""

import requests
import json
import os
from datetime import datetime

# Configuration
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')

def print_banner():
    """Print viewer banner"""
    print("=" * 60)
    print("COS Event Viewer - Event Analysis")
    print("=" * 60)
    print(f"Application: {APP_URL}")
    print("=" * 60)
    print()

def get_app_status():
    """Get application status and COS configuration"""
    try:
        response = requests.get(f"{APP_URL}/health", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        return None

def get_cos_events_info():
    """Get COS events endpoint information"""
    try:
        response = requests.get(f"{APP_URL}/cos/events", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ COS events info failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot get COS events info: {e}")
        return None

def send_test_events():
    """Send multiple test events to verify processing"""
    test_events = [
        {
            "events": [
                {
                    "eventType": "Object:Put",
                    "bucket": "test-bucket",
                    "key": "uploads/document.pdf",
                    "time": datetime.now().isoformat()
                }
            ]
        },
        {
            "events": [
                {
                    "eventType": "Object:Delete",
                    "bucket": "test-bucket",
                    "key": "uploads/old-file.txt",
                    "time": datetime.now().isoformat()
                }
            ]
        },
        {
            "events": [
                {
                    "eventType": "Object:Copy",
                    "bucket": "test-bucket",
                    "key": "backups/document.pdf",
                    "time": datetime.now().isoformat()
                }
            ]
        }
    ]
    
    print("Sending test events...")
    for i, event in enumerate(test_events, 1):
        try:
            response = requests.post(
                f"{APP_URL}/cos/events",
                json=event,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test Event {i}: {data['message']}")
                for evt in data['events']:
                    print(f"   - {evt['event_type']}: {evt['object_key']}")
            else:
                print(f"❌ Test Event {i} failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Test Event {i} error: {e}")
    
    print()

def display_app_info():
    """Display application information"""
    print("📊 Application Information:")
    print("-" * 40)
    
    # Health check
    health = get_app_status()
    if health:
        print(f"Status: {health['status']}")
        print(f"COS Configured: {health['cos_configured']}")
        print(f"Last Check: {health['timestamp']}")
    else:
        print("❌ Cannot get application status")
    
    print()
    
    # COS events info
    cos_info = get_cos_events_info()
    if cos_info:
        print(f"Events Endpoint: {cos_info['endpoint']}")
        print(f"Method: {cos_info['method']}")
        print(f"Status: {cos_info['status']}")
        if 'config' in cos_info:
            config = cos_info['config']
            print(f"COS Endpoint: {config.get('endpoint', 'Not set')}")
            print(f"COS Bucket: {config.get('bucket', 'Not set')}")
            print(f"Has Secret: {config.get('has_secret', False)}")
    else:
        print("❌ Cannot get COS events information")
    
    print()

def show_verification_steps():
    """Show steps to verify events are captured"""
    print("🔍 How to Verify Events Are Captured:")
    print("-" * 40)
    
    print("1. 📝 Check Application Logs:")
    print("   - Look for log entries when files are uploaded/deleted")
    print("   - Search for 'Received COS event' messages")
    print("   - Check for 'Processed X events' confirmations")
    
    print("\n2. 🌐 Monitor Webhook Endpoint:")
    print("   - Use the monitoring script: python monitor_events.py")
    print("   - Watch for real-time event processing")
    print("   - Verify events are being received")
    
    print("\n3. 📤 Test with Real COS Operations:")
    print("   - Upload a file to your COS bucket")
    print("   - Delete a file from your COS bucket")
    print("   - Copy a file within your COS bucket")
    print("   - Check if events are triggered")
    
    print("\n4. 🔧 Manual Testing:")
    print("   - Send test events using this script")
    print("   - Use curl to test the webhook endpoint")
    print("   - Verify response format and content")
    
    print("\n5. 📊 Check IBM Cloud Logs:")
    print("   - Review Code Engine application logs")
    print("   - Check COS notification delivery status")
    print("   - Monitor webhook delivery attempts")
    
    print()

def show_troubleshooting():
    """Show troubleshooting steps"""
    print("🔧 Troubleshooting:")
    print("-" * 40)
    
    print("❌ If events are NOT being captured:")
    print("1. Check if your app is accessible from the internet")
    print("2. Verify COS notification configuration")
    print("3. Check webhook URL is correct")
    print("4. Ensure event types are selected in COS")
    print("5. Check application logs for errors")
    
    print("\n❌ If signature verification fails:")
    print("1. Ensure COS_SECRET_KEY matches COS settings")
    print("2. Check if signature header is present")
    print("3. Verify HMAC calculation")
    
    print("\n❌ If events are malformed:")
    print("1. Check event format compatibility")
    print("2. Verify JSON payload structure")
    print("3. Test with different event types")
    
    print()

def main():
    """Main viewer function"""
    print_banner()
    
    # Display app information
    display_app_info()
    
    # Show verification steps
    show_verification_steps()
    
    # Show troubleshooting
    show_troubleshooting()
    
    # Ask if user wants to send test events
    response = input("Send test events to verify processing? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        send_test_events()
    
    print("✅ Event verification complete!")
    print("\nNext steps:")
    print("1. Upload files to your COS bucket")
    print("2. Run: python monitor_events.py")
    print("3. Check application logs")
    print("4. Verify events are being processed")

if __name__ == "__main__":
    main() 