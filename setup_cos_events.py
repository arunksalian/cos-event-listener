#!/usr/bin/env python3
"""
Setup script for Cloud Object Storage Event Notifications
This script helps configure COS event notifications for your application
"""

import os
import sys
import json
import requests
from cos_config import get_cos_config, get_webhook_url, COS_EVENT_TYPES

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("Cloud Object Storage Event Listener Setup")
    print("=" * 60)
    print()

def check_environment():
    """Check if required environment variables are set"""
    print("Checking environment configuration...")
    
    config = get_cos_config()
    missing_vars = []
    
    required_vars = ['COS_ENDPOINT', 'COS_BUCKET_NAME']
    for var in required_vars:
        if not config.get(var.lower().replace('cos_', '')):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=your_value")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def get_webhook_endpoint():
    """Get the webhook endpoint URL"""
    print("\nWebhook Configuration:")
    print("Your application will receive COS events at:")
    
    # Try to get the application URL
    app_url = os.environ.get('APP_URL', 'http://localhost:5000')
    webhook_url = get_webhook_url(app_url)
    
    print(f"  Webhook URL: {webhook_url}")
    print(f"  Method: POST")
    print(f"  Content-Type: application/json")
    
    return webhook_url

def generate_cos_config():
    """Generate COS configuration for event notifications"""
    print("\nCOS Event Notification Configuration:")
    
    config = {
        "event_types": COS_EVENT_TYPES,
        "webhook_url": get_webhook_endpoint(),
        "cos_config": get_cos_config()
    }
    
    print("Event types to listen for:")
    for event_type in COS_EVENT_TYPES:
        print(f"  - {event_type}")
    
    return config

def create_notification_config():
    """Create notification configuration file"""
    config = generate_cos_config()
    
    config_file = "cos_notification_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {config_file}")
    return config_file

def test_webhook_endpoint():
    """Test if the webhook endpoint is accessible"""
    print("\nTesting webhook endpoint...")
    
    webhook_url = get_webhook_endpoint()
    
    try:
        response = requests.get(webhook_url, timeout=10)
        if response.status_code == 200:
            print("✅ Webhook endpoint is accessible")
            return True
        else:
            print(f"⚠️  Webhook endpoint returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access webhook endpoint: {e}")
        print("Make sure your application is running and accessible")
        return False

def print_setup_instructions():
    """Print setup instructions for COS event notifications"""
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. IBM Cloud Object Storage Setup:")
    print("   - Go to your IBM Cloud COS instance")
    print("   - Navigate to your bucket")
    print("   - Go to 'Configuration' > 'Event Notifications'")
    print("   - Click 'Create notification'")
    
    print("\n2. Configure the notification:")
    print("   - Name: cos-event-listener")
    print("   - Event types: Select the events you want to listen for")
    print("   - Destination: Webhook")
    print(f"   - URL: {get_webhook_endpoint()}")
    print("   - HTTP method: POST")
    
    print("\n3. Optional: Configure authentication:")
    print("   - If you want to verify webhook signatures:")
    print("   - Set a secret key in COS notification settings")
    print("   - Set the same key as COS_SECRET_KEY environment variable")
    
    print("\n4. Test the setup:")
    print("   - Upload a file to your COS bucket")
    print("   - Check your application logs for the event")
    print("   - Or use: curl -X GET <your-app-url>/cos/events")

def main():
    """Main setup function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Generate configuration
    config_file = create_notification_config()
    
    # Test webhook endpoint
    test_webhook_endpoint()
    
    # Print instructions
    print_setup_instructions()
    
    print(f"\n✅ Setup complete! Configuration saved to: {config_file}")
    print("\nNext steps:")
    print("1. Configure COS event notifications using the instructions above")
    print("2. Deploy your application to IBM Code Engine")
    print("3. Test by uploading files to your COS bucket")

if __name__ == "__main__":
    main() 