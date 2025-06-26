#!/usr/bin/env python3
"""
COS Event Monitor
Real-time monitoring script to verify COS events are being captured
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
MONITOR_INTERVAL = 5  # seconds

def print_banner():
    """Print monitoring banner"""
    print("=" * 60)
    print("COS Event Monitor - Real-time Event Verification")
    print("=" * 60)
    print(f"Monitoring: {APP_URL}")
    print(f"Interval: {MONITOR_INTERVAL} seconds")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    print()

def check_app_health():
    """Check if the application is running"""
    try:
        response = requests.get(f"{APP_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ App Status: {data['status']}")
            print(f"✅ COS Configured: {data['cos_configured']}")
            print(f"✅ Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ App returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        return False

def check_cos_events_status():
    """Check COS events endpoint status"""
    try:
        response = requests.get(f"{APP_URL}/cos/events", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ COS Events Endpoint: {data['status']}")
            print(f"✅ Endpoint: {data['endpoint']}")
            print(f"✅ Method: {data['method']}")
            return True
        else:
            print(f"❌ COS events endpoint returned: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access COS events endpoint: {e}")
        return False

def send_test_event():
    """Send a test event to verify processing"""
    test_event = {
        "events": [
            {
                "eventType": "Object:Put",
                "bucket": "test-bucket",
                "key": f"test-files/test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test Event Sent Successfully!")
            print(f"✅ Processed Events: {data['message']}")
            print(f"✅ Event Details: {json.dumps(data['events'], indent=2)}")
            return True
        else:
            print(f"❌ Test event failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot send test event: {e}")
        return False

def monitor_continuously():
    """Continuously monitor for events"""
    print("Starting continuous monitoring...")
    print("Upload files to your COS bucket to see events here!")
    print()
    
    last_check = datetime.now()
    
    while True:
        try:
            current_time = datetime.now()
            print(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Checking for events...")
            
            # Check app health
            if not check_app_health():
                print("⚠️  Application appears to be down")
            
            # Check COS events status
            check_cos_events_status()
            
            # Wait for next check
            time.sleep(MONITOR_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            time.sleep(MONITOR_INTERVAL)

def main():
    """Main monitoring function"""
    print_banner()
    
    # Initial health check
    print("Initial Health Check:")
    if not check_app_health():
        print("❌ Application is not accessible. Please start the app first.")
        return
    
    print()
    
    # Check COS events endpoint
    print("COS Events Endpoint Check:")
    if not check_cos_events_status():
        print("❌ COS events endpoint is not accessible.")
        return
    
    print()
    
    # Send test event
    print("Sending Test Event:")
    send_test_event()
    
    print()
    
    # Ask user if they want continuous monitoring
    response = input("Start continuous monitoring? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        monitor_continuously()
    else:
        print("Monitoring complete. Use this script anytime to check events!")

if __name__ == "__main__":
    main() 