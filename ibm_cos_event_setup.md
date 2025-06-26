# IBM Cloud Object Storage Event Notifications Setup

## Overview
IBM Cloud Object Storage (COS) uses the **IBM Cloud Event Notifications (EN) service** for event-driven triggers, not direct bucket notifications like AWS S3. This guide shows you how to properly configure COS event notifications.

## Prerequisites

1. **IBM Cloud Account** with access to:
   - Cloud Object Storage (COS)
   - Event Notifications (EN) service
   - Code Engine (for your application)

2. **Your COS Event Listener Application** deployed and accessible

## Step-by-Step Setup

### 1. Create Event Notifications Service Instance

1. Go to the **IBM Cloud Catalog**
2. Search for **"Event Notifications"**
3. Click on **"Event Notifications"** service
4. Click **"Create"**
5. Configure:
   - **Service name**: `cos-event-notifications`
   - **Region**: Same as your COS instance
   - **Resource group**: Your resource group
6. Click **"Create"**

### 2. Create Event Source (COS)

1. In your Event Notifications instance, go to **"Event sources"**
2. Click **"Create event source"**
3. Select **"Cloud Object Storage"**
4. Configure:
   - **Event source name**: `cos-event-source`
   - **COS instance**: Select your COS instance
   - **Bucket**: Select your bucket
   - **Event types**: Select the events you want to listen for:
     - `Object:Put`
     - `Object:Delete`
     - `Object:Copy`
     - `Object:CompleteMultipartUpload`
     - `Object:AbortMultipartUpload`
5. Click **"Create"**

### 3. Create Destination (Webhook)

1. Go to **"Destinations"**
2. Click **"Create destination"**
3. Select **"Webhook"**
4. Configure:
   - **Destination name**: `cos-event-listener-webhook`
   - **URL**: `https://your-app-url/cos/events`
   - **HTTP method**: `POST`
   - **Content type**: `application/json`
   - **Secret key**: (Optional) Set a secret for signature verification
5. Click **"Create"**

### 4. Create Subscription

1. Go to **"Subscriptions"**
2. Click **"Create subscription"**
3. Configure:
   - **Subscription name**: `cos-event-subscription`
   - **Event source**: Select your COS event source
   - **Destination**: Select your webhook destination
   - **Event types**: Select the events you want to receive
4. Click **"Create"**

## Configuration Details

### Event Source Configuration

```yaml
Event Source:
  Name: cos-event-source
  Type: Cloud Object Storage
  Instance: your-cos-instance
  Bucket: your-bucket-name
  Event Types:
    - Object:Put
    - Object:Delete
    - Object:Copy
    - Object:CompleteMultipartUpload
    - Object:AbortMultipartUpload
```

### Destination Configuration

```yaml
Destination:
  Name: cos-event-listener-webhook
  Type: Webhook
  URL: https://your-app-url/cos/events
  Method: POST
  Content-Type: application/json
  Secret Key: your-webhook-secret (optional)
```

### Subscription Configuration

```yaml
Subscription:
  Name: cos-event-subscription
  Event Source: cos-event-source
  Destination: cos-event-listener-webhook
  Event Types: All selected events
```

## Environment Variables for Your Application

Set these environment variables in your application:

```bash
# COS Configuration
export COS_ENDPOINT="https://s3.us-south.cloud-object-storage.appdomain.cloud"
export COS_BUCKET_NAME="your-bucket-name"

# Event Notifications Configuration
export COS_SECRET_KEY="your-webhook-secret"  # If you set one in the destination
export APP_URL="https://your-app-url"

# Optional: Disable signature verification for testing
export DISABLE_SIGNATURE_VERIFICATION=false
```

## IBM Code Engine Deployment

Deploy your application with the correct environment variables:

```bash
ibmcloud ce app create \
  --name cos-event-listener \
  --image us.icr.io/suppliq-dev/cos-event-listener:1.0.1 \
  --cpu 0.25 \
  --memory 0.5G \
  --port 5000 \
  --env COS_ENDPOINT="https://s3.us-south.cloud-object-storage.appdomain.cloud" \
  --env COS_BUCKET_NAME="your-bucket-name" \
  --env COS_SECRET_KEY="your-webhook-secret" \
  --env APP_URL="https://cos-event-listener.xyz.us-south.codeengine.appdomain.cloud"
```

## Testing the Setup

### 1. Test Your Application

```bash
# Check if your app is ready to receive events
curl "https://your-app-url/health"

# Check COS events endpoint
curl "https://your-app-url/cos/events"
```

### 2. Test Event Notifications

1. **Upload a file** to your COS bucket
2. **Check Event Notifications logs**:
   - Go to your Event Notifications instance
   - Check "Activity" or "Logs" section
3. **Check your application logs**:
   ```bash
   ibmcloud ce app logs --name cos-event-listener --follow
   ```

### 3. Monitor Event Delivery

In the Event Notifications service:
- Go to **"Subscriptions"**
- Click on your subscription
- Check **"Activity"** tab for delivery status
- Look for successful webhook deliveries

## Troubleshooting

### Common Issues

1. **Events not being delivered**:
   - Check if your app URL is accessible from IBM Cloud
   - Verify the webhook URL is correct
   - Check Event Notifications logs

2. **Signature verification fails**:
   - Ensure the secret key matches between Event Notifications and your app
   - Check if signature verification is enabled in your app

3. **Subscription not active**:
   - Verify the subscription is created and active
   - Check if the event source is properly configured

### Debug Steps

1. **Check Event Notifications status**:
   - Go to your Event Notifications instance
   - Check "Activity" for any errors

2. **Test webhook manually**:
   ```bash
   curl -X POST "https://your-app-url/cos/events" \
     -H "Content-Type: application/json" \
     -d '{"test": "event"}'
   ```

3. **Check application logs**:
   ```bash
   ibmcloud ce app logs --name cos-event-listener
   ```

## Cost Considerations

- **Event Notifications service**: Pay-per-use based on events processed
- **COS events**: No additional cost for generating events
- **Code Engine**: Pay-per-use for your application

## Best Practices

1. **Use specific event types** to avoid unnecessary events
2. **Set up monitoring** for event delivery failures
3. **Use secret keys** for webhook security in production
4. **Monitor costs** of Event Notifications service
5. **Set up alerts** for webhook delivery failures

## Alternative: Direct COS API (Advanced)

For advanced use cases, you can also use the COS API directly:

```bash
# List objects and check for changes
ibmcloud cos list-objects --bucket your-bucket-name

# Use COS API with event polling
# (More complex, requires custom implementation)
```

## Summary

The key difference from AWS S3 is that IBM COS requires:
1. **Event Notifications service** (separate from COS)
2. **Event sources** to define what to monitor
3. **Destinations** to define where to send events
4. **Subscriptions** to connect sources to destinations

This architecture provides more flexibility and better integration with other IBM Cloud services. 