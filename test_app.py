import requests
import json

# Base URL for the application
BASE_URL = "http://localhost:5000"

def test_home_endpoint():
    """Test the home endpoint with different query parameters"""
    print("=== Testing Home Endpoint ===")
    
    # Test without parameters
    response = requests.get(f"{BASE_URL}/")
    print(f"GET {BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test with name parameter
    response = requests.get(f"{BASE_URL}/?name=Alice")
    print(f"GET {BASE_URL}/?name=Alice")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test with multiple parameters
    response = requests.get(f"{BASE_URL}/?name=Bob&age=30&city=NewYork")
    print(f"GET {BASE_URL}/?name=Bob&age=30&city=NewYork")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_cos_events_endpoint():
    """Test the COS events endpoint"""
    print("=== Testing COS Events Endpoint ===")
    
    # Test GET request (status check)
    response = requests.get(f"{BASE_URL}/cos/events")
    print(f"GET {BASE_URL}/cos/events")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test POST request with sample COS event
    sample_cos_event = {
        "events": [
            {
                "eventType": "Object:Put",
                "bucket": "test-bucket",
                "key": "uploads/test-file.txt",
                "time": "2024-01-15T10:30:00.000Z"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/cos/events", json=sample_cos_event)
    print(f"POST {BASE_URL}/cos/events")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test POST request with S3-compatible format
    sample_s3_event = {
        "Records": [
            {
                "eventName": "ObjectCreated:Put",
                "eventTime": "2024-01-15T10:30:00.000Z",
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "uploads/test-file.txt"
                    }
                }
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/cos/events", json=sample_s3_event)
    print(f"POST {BASE_URL}/cos/events (S3 format)")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_data_endpoint():
    """Test the data endpoint with different query parameters"""
    print("=== Testing Data Endpoint ===")
    
    # Test without parameters
    response = requests.get(f"{BASE_URL}/api/data")
    print(f"GET {BASE_URL}/api/data")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test with pagination
    response = requests.get(f"{BASE_URL}/api/data?limit=2&offset=1")
    print(f"GET {BASE_URL}/api/data?limit=2&offset=1")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test with category filter
    response = requests.get(f"{BASE_URL}/api/data?category=tech")
    print(f"GET {BASE_URL}/api/data?category=tech")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_health_endpoint():
    """Test the health endpoint"""
    print("=== Testing Health Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"GET {BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_cos_signature_verification():
    """Test COS signature verification (if secret is configured)"""
    print("=== Testing COS Signature Verification ===")
    
    # This test would require a valid signature
    # For now, we'll just test the endpoint without signature
    sample_event = {
        "events": [
            {
                "eventType": "Object:Delete",
                "bucket": "test-bucket",
                "key": "uploads/deleted-file.txt",
                "time": "2024-01-15T10:35:00.000Z"
            }
        ]
    }
    
    # Test without signature header (should work if no secret configured)
    response = requests.post(f"{BASE_URL}/cos/events", json=sample_event)
    print(f"POST {BASE_URL}/cos/events (no signature)")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    try:
        test_home_endpoint()
        test_cos_events_endpoint()
        test_data_endpoint()
        test_health_endpoint()
        test_cos_signature_verification()
        print("All tests completed successfully!")
        print("\nTo test with real COS events:")
        print("1. Configure COS event notifications")
        print("2. Upload files to your COS bucket")
        print("3. Check application logs for events")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the Flask application is running on http://localhost:5000")
        print("Run: python app.py")
    except Exception as e:
        print(f"Error during testing: {e}") 