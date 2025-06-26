# Testing COS Events with Signatures in Postman

## Overview
This guide shows you how to test your COS event listener with proper signature verification in Postman.

## Setup

### 1. Environment Variables in Postman

Create a new environment in Postman with these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `app_url` | `https://your-app-url` | Your application URL |
| `cos_secret_key` | `your-secret-key` | Your COS webhook secret key |
| `cos_endpoint` | `https://s3.us-south.cloud-object-storage.appdomain.cloud` | Your COS endpoint |
| `cos_bucket` | `your-bucket-name` | Your COS bucket name |

### 2. Pre-request Script for Signature Generation (FIXED)

Add this **corrected** script to your request's "Pre-request Script" tab:

```javascript
// Get the request body
const requestBody = pm.request.body.raw;

// Get the secret key from environment
const secretKey = pm.environment.get('cos_secret_key');

if (!secretKey) {
    console.error('cos_secret_key environment variable is not set');
    return;
}

if (!requestBody) {
    console.error('Request body is empty');
    return;
}

// Generate HMAC signature using Postman's CryptoJS
const signature = CryptoJS.HmacSHA256(requestBody, secretKey);
const base64Signature = signature.toString(CryptoJS.enc.Base64);

// Remove existing signature header if present
pm.request.headers.remove('X-Cos-Signature');

// Add the signature header
pm.request.headers.add({
    key: 'X-Cos-Signature',
    value: base64Signature
});

console.log('Request body:', requestBody);
console.log('Secret key:', secretKey.substring(0, 10) + '...');
console.log('Generated signature:', base64Signature);
```

### 3. Alternative Pre-request Script (Simpler Version)

If the above still doesn't work, try this simpler version:

```javascript
// Get the request body
const requestBody = pm.request.body.raw;
const secretKey = pm.environment.get('cos_secret_key');

if (requestBody && secretKey) {
    // Generate signature
    const signature = CryptoJS.HmacSHA256(requestBody, secretKey);
    const base64Signature = signature.toString(CryptoJS.enc.Base64);
    
    // Set header
    pm.request.headers.add({
        key: 'X-Cos-Signature',
        value: base64Signature
    });
    
    console.log('Signature generated:', base64Signature);
} else {
    console.error('Missing request body or secret key');
}
```

## Request Configuration

### Method: POST
### URL: `{{app_url}}/cos/events`

### Headers:
```
Content-Type: application/json
X-Cos-Signature: {{signature}}  // This will be set by the pre-request script
```

### Body (raw JSON):

#### Example 1: Object Put Event
```json
{
  "events": [
    {
      "eventType": "Object:Put",
      "bucket": "{{cos_bucket}}",
      "key": "uploads/test-file.txt",
      "time": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

#### Example 2: Object Delete Event
```json
{
  "events": [
    {
      "eventType": "Object:Delete",
      "bucket": "{{cos_bucket}}",
      "key": "uploads/deleted-file.txt",
      "time": "2024-01-15T10:35:00.000Z"
    }
  ]
}
```

#### Example 3: S3 Compatible Format
```json
{
  "Records": [
    {
      "eventName": "ObjectCreated:Put",
      "eventTime": "2024-01-15T10:30:00.000Z",
      "s3": {
        "bucket": {
          "name": "{{cos_bucket}}"
        },
        "object": {
          "key": "uploads/s3-compatible-test.txt"
        }
      }
    }
  ]
}
```

## Testing Steps

### 1. Test Health Check (No Signature Required)
- **Method**: GET
- **URL**: `{{app_url}}/health`
- **Headers**: None required

### 2. Test COS Events Status (No Signature Required)
- **Method**: GET
- **URL**: `{{app_url}}/cos/events`
- **Headers**: None required

### 3. Test COS Events with Signature
- **Method**: POST
- **URL**: `{{app_url}}/cos/events`
- **Headers**: Set by pre-request script
- **Body**: Use one of the JSON examples above

## Expected Responses

### Success Response (200):
```json
{
  "status": "success",
  "message": "Processed 1 events",
  "events": [
    {
      "event_type": "Object:Put",
      "bucket": "your-bucket",
      "object_key": "uploads/test-file.txt",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "source": "ibm_cos"
    }
  ],
  "timestamp": "2024-01-15T10:30:01.000Z"
}
```

### Invalid Signature Response (401):
```json
{
  "error": "Invalid signature"
}
```

## Troubleshooting

### 1. CryptoJS Error Fixes

If you get CryptoJS errors, try these solutions:

**Solution 1: Use the corrected script above**

**Solution 2: Manual signature calculation**
```javascript
// Alternative manual approach
const requestBody = pm.request.body.raw;
const secretKey = pm.environment.get('cos_secret_key');

if (requestBody && secretKey) {
    // Use a different approach
    const encoder = new TextEncoder();
    const keyData = encoder.encode(secretKey);
    const messageData = encoder.encode(requestBody);
    
    // Note: This is a simplified approach - you might need to implement HMAC-SHA256 manually
    // or use a different method
    
    console.log('Manual signature calculation needed');
}
```

**Solution 3: Test without signature**
- Set `DISABLE_SIGNATURE_VERIFICATION=true` in your app
- Remove the pre-request script
- Test without signature verification

### 2. Common Issues

- **"Cannot read properties of undefined"**: Make sure request body exists
- **"sigBytes error"**: Use the corrected script above
- **"Secret key not found"**: Check environment variables
- **"Invalid signature"**: Verify secret key matches COS configuration

### 3. Debug Steps

1. Check console logs in Postman
2. Verify environment variables are set
3. Ensure request body is not empty
4. Test without signature first

## Quick Test Without Signature

For immediate testing without signature verification:

1. **Set environment variable** in your app:
   ```bash
   export DISABLE_SIGNATURE_VERIFICATION=true
   ```

2. **In Postman**: 
   - Remove the pre-request script
   - Remove the `X-Cos-Signature` header
   - Just send the JSON body

3. **Request**:
   - Method: POST
   - URL: `{{app_url}}/cos/events`
   - Headers: `Content-Type: application/json`
   - Body: Your JSON payload

## Postman Collection Structure

```json
{
  "info": {
    "name": "COS Event Listener Tests",
    "description": "Test collection for COS event listener"
  },
  "variable": [
    {
      "key": "app_url",
      "value": "https://your-app-url"
    },
    {
      "key": "cos_secret_key",
      "value": "your-secret-key"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{app_url}}/health"
      }
    },
    {
      "name": "Test COS Event with Signature",
      "event": [
        {
          "listen": "prerequest",
          "script": {
            "exec": [
              "const requestBody = pm.request.body.raw;",
              "const secretKey = pm.environment.get('cos_secret_key');",
              "if (requestBody && secretKey) {",
              "    const signature = CryptoJS.HmacSHA256(requestBody, secretKey);",
              "    const base64Signature = signature.toString(CryptoJS.enc.Base64);",
              "    pm.request.headers.add({",
              "        key: 'X-Cos-Signature',",
              "        value: base64Signature",
              "    });",
              "    console.log('Signature generated:', base64Signature);",
              "}"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"events\": [\n    {\n      \"eventType\": \"Object:Put\",\n      \"bucket\": \"test-bucket\",\n      \"key\": \"uploads/test-file.txt\",\n      \"time\": \"2024-01-15T10:30:00.000Z\"\n    }\n  ]\n}"
        },
        "url": "{{app_url}}/cos/events"
      }
    }
  ]
}
```

## Testing Checklist

- [ ] Environment variables set in Postman
- [ ] Pre-request script added (if using signatures)
- [ ] Correct URL and method
- [ ] Valid JSON body
- [ ] Content-Type header set
- [ ] Console logs show signature generation
- [ ] No CryptoJS errors in console

## Advanced Testing

### Dynamic Timestamps
Use this in the request body for dynamic timestamps:

```json
{
  "events": [
    {
      "eventType": "Object:Put",
      "bucket": "{{cos_bucket}}",
      "key": "uploads/test-{{$timestamp}}.txt",
      "time": "{{$isoTimestamp}}"
    }
  ]
}
```

### Multiple Events
Test with multiple events in a single request:

```json
{
  "events": [
    {
      "eventType": "Object:Put",
      "bucket": "{{cos_bucket}}",
      "key": "uploads/file1.txt",
      "time": "{{$isoTimestamp}}"
    },
    {
      "eventType": "Object:Delete",
      "bucket": "{{cos_bucket}}",
      "key": "uploads/file2.txt",
      "time": "{{$isoTimestamp}}"
    }
  ]
}
```

## Postman Collection

You can import this collection structure:

```json
{
  "info": {
    "name": "COS Event Listener Tests",
    "description": "Test collection for COS event listener with signature verification"
  },
  "variable": [
    {
      "key": "app_url",
      "value": "https://your-app-url"
    },
    {
      "key": "cos_secret_key",
      "value": "your-secret-key"
    },
    {
      "key": "cos_endpoint",
      "value": "https://s3.us-south.cloud-object-storage.appdomain.cloud"
    },
    {
      "key": "cos_bucket",
      "value": "your-bucket-name"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{app_url}}/health",
          "host": ["{{app_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "COS Events Status",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{app_url}}/cos/events",
          "host": ["{{app_url}}"],
          "path": ["cos", "events"]
        }
      }
    },
    {
      "name": "Test Object Put Event",
      "event": [
        {
          "listen": "prerequest",
          "script": {
            "exec": [
              "const requestBody = pm.request.body.raw;",
              "const secretKey = pm.environment.get('cos_secret_key');",
              "if (requestBody && secretKey) {",
              "    const signature = CryptoJS.HmacSHA256(requestBody, secretKey);",
              "    const base64Signature = signature.toString(CryptoJS.enc.Base64);",
              "    pm.request.headers.add({",
              "        key: 'X-Cos-Signature',",
              "        value: base64Signature",
              "    });",
              "    console.log('Signature generated:', base64Signature);",
              "}"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"events\": [\n    {\n      \"eventType\": \"Object:Put\",\n      \"bucket\": \"{{cos_bucket}}\",\n      \"key\": \"uploads/test-file.txt\",\n      \"time\": \"2024-01-15T10:30:00.000Z\"\n    }\n  ]\n}"
        },
        "url": {
          "raw": "{{app_url}}/cos/events",
          "host": ["{{app_url}}"],
          "path": ["cos", "events"]
        }
      }
    }
  ]
}
``` 