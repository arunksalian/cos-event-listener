#!/usr/bin/env python3
"""
Test script to verify PDF detection logic with real COS event format
"""

import json
from datetime import datetime

# Simulate the real COS event format from the logs
real_cos_event = {
    "bucket_name": "bucket-redact-test",
    "content_type": "application/pdf",
    "event_type": "Object:Write",
    "format": "2.0",
    "object_etag": "e7a674fd5d11958e378721dca5dafbfc",
    "object_length": "387865",
    "object_name": "MyTheron - Architecture.pdf",
    "request_id": "963af45e-3018-4984-bc8c-4160f50365fc",
    "request_time": "2025-06-26T08:45:28.305Z"
}

def is_pdf_file(object_key):
    """Check if the uploaded file is a PDF"""
    if not object_key:
        print(f"🔍 PDF Check: Object key is empty or None")
        return False
    
    # Check file extension
    import os
    file_extension = os.path.splitext(object_key.lower())[1]
    print(f"🔍 PDF Check: File '{object_key}' has extension '{file_extension}'")
    
    if file_extension == '.pdf':
        print(f"✅ PDF Detected: File '{object_key}' has .pdf extension")
        return True
    
    # Additional check: if the object key contains 'pdf' in the filename
    filename = os.path.basename(object_key.lower())
    if 'pdf' in filename:
        print(f"✅ PDF Detected: File '{object_key}' contains 'pdf' in filename")
        return True
    
    print(f"❌ Not PDF: File '{object_key}' does not match PDF criteria")
    print(f"🔍 File extension: '{file_extension}', filename: '{filename}'")
    return False

def is_upload_event(event_type):
    """Check if the event is an upload event"""
    upload_events = [
        'Object:Put',
        'Object:Post',
        'Object:Write',
        's3:ObjectCreated:Put',
        's3:ObjectCreated:Post',
        's3:ObjectCreated:CompleteMultipartUpload',
        'Put',
        'Post',
        'Create',
        'Upload',
        'Write'
    ]
    
    is_upload = event_type in upload_events
    print(f"🔍 Upload Event Check: '{event_type}' -> {'✅ Upload Event' if is_upload else '❌ Not Upload Event'}")
    print(f"🔍 Available upload events: {upload_events}")
    return is_upload

def extract_direct_cos_event_info(event_data):
    """Extract event information from direct COS notification format"""
    print(f"🔄 Extracting direct COS event info")
    print(f"🔍 Raw event data: {event_data}")
    
    try:
        # Handle different possible field names for bucket
        bucket = event_data.get('bucket', event_data.get('bucket_name', 'Unknown'))
        
        # Handle different possible field names for object key
        object_key = event_data.get('key', event_data.get('object_name', 'Unknown'))
        notification = event_data.get('notification', 'Unknown')
        operation = event_data.get('operation', 'Unknown')
        
        # Handle different possible field names for event type
        event_type = event_data.get('event_type', notification if notification != 'Unknown' else operation)
        
        print(f"📋 Direct COS Event extracted: bucket={bucket}, object_key={object_key}, event_type={event_type}")
        
        extracted_event = {
            'event_type': event_type,
            'bucket': bucket,
            'object_key': object_key,
            'timestamp': datetime.now().isoformat(),
            'source': 'direct_cos'
        }
        
        print(f"📋 Extracted event object: {extracted_event}")
        return extracted_event
        
    except Exception as e:
        print(f"❌ Error extracting direct COS event info: {e}")
        return None

def check_pdf_upload(event):
    """Check if the event is a PDF upload and log it"""
    print("🔍 Starting PDF upload check...")
    
    try:
        event_type = event.get('event_type', '')
        object_key = event.get('object_key', '')
        bucket = event.get('bucket', '')
        
        print(f"🔍 PDF Upload Check: Event '{event_type}' for file '{object_key}' in bucket '{bucket}'")
        print(f"🔍 Full event data: {event}")
        
        # Check if it's an upload event and the file is a PDF
        is_upload = is_upload_event(event_type)
        is_pdf = is_pdf_file(object_key)
        
        print(f"🔍 Upload check result: {is_upload}")
        print(f"🔍 PDF check result: {is_pdf}")
        
        if is_upload and is_pdf:
            print(f"📄 PDF UPLOAD DETECTED: File '{object_key}' uploaded to bucket '{bucket}' at {event.get('timestamp', 'unknown time')}")
            print(f"📄 PDF Details: Event Type: {event_type}, Source: {event.get('source', 'unknown')}")
            return True
        else:
            if not is_upload:
                print(f"📝 Not an upload event: {event_type}")
            if not is_pdf:
                print(f"📝 Not a PDF file: {object_key}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking PDF upload: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing PDF Detection Logic with Real COS Event Format")
    print("=" * 60)
    
    # Test the real COS event format
    print(f"📋 Testing real COS event format:")
    print(f"🔍 Event keys: {list(real_cos_event.keys())}")
    
    # Check which condition would be matched
    if 'Records' in real_cos_event:
        print("📋 Would process as S3-compatible format")
    elif 'events' in real_cos_event:
        print("📋 Would process as IBM COS format")
    elif 'bucket' in real_cos_event and ('key' in real_cos_event or 'object_name' in real_cos_event):
        print("📋 Would process as direct COS notification format")
    elif 'bucket_name' in real_cos_event and 'object_name' in real_cos_event:
        print("📋 Would process as direct COS notification format (bucket_name/object_name)")
    else:
        print("📋 Would process as single event or unknown format")
    
    # Extract event info
    print("\n🔄 Extracting event information...")
    extracted_event = extract_direct_cos_event_info(real_cos_event)
    
    if extracted_event:
        print(f"✅ Event extraction successful: {extracted_event}")
        
        # Check for PDF upload
        print("\n🔍 Checking for PDF upload...")
        is_pdf_upload = check_pdf_upload(extracted_event)
        
        if is_pdf_upload:
            print("🎉 SUCCESS: PDF upload detected correctly!")
        else:
            print("❌ FAILED: PDF upload not detected")
    else:
        print("❌ FAILED: Event extraction failed")

if __name__ == "__main__":
    main() 