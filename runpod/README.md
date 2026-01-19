# RunPod.io GPU Integration

This directory contains files for integrating GPU processing with RunPod.io.

## Overview

RunPod.io provides on-demand GPU instances that can be used for OCR processing, significantly reducing costs compared to running a dedicated GPU server.

## Architecture

```
DigitalOcean VPS          RunPod.io GPU
     (Flask App)    →     (OCR Processing)
         ↓                      ↓
    Upload PDF          Process with GPU
         ↓                      ↓
    Send to RunPod      Return OCR results
         ↓                      ↓
    Receive results     (Auto-shutdown)
         ↓
    Continue processing
```

## Files

- `handler.py` - RunPod serverless handler (for serverless endpoints)
- `api_server.py` - Simple Flask API server (for pod endpoints)
- `requirements.txt` - Python dependencies for RunPod
- `Dockerfile` - Docker image for custom RunPod deployment

## Setup Options

### Option 1: Serverless Endpoint (Recommended)

**Pros:**
- Auto-scaling
- Pay only for execution time
- No idle costs
- Automatic shutdown

**Cons:**
- Cold start latency (~5-10 seconds)
- More complex setup

**Setup:**
1. Create serverless endpoint in RunPod dashboard
2. Upload `handler.py` as the handler
3. Configure auto-scaling (1-5 workers)
4. Get endpoint ID and API key

### Option 2: Pod Endpoint (Simpler)

**Pros:**
- No cold start
- Simpler setup
- Faster response

**Cons:**
- Always running (costs ~$0.20-$0.40/hour)
- Manual scaling
- Need to manage pod lifecycle

**Setup:**
1. Deploy GPU pod
2. Install dependencies
3. Run `api_server.py`
4. Get pod URL

## Configuration

### Environment Variables (on DigitalOcean VPS)

```bash
# .env file
RUNPOD_API_KEY=your-api-key-here
RUNPOD_ENDPOINT_ID=your-endpoint-id-here
FORCE_RUNPOD=true  # Always use RunPod instead of local GPU
```

### Testing RunPod Connection

```bash
# Test API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.runpod.io/v1/user

# Test endpoint
curl -X POST https://api.runpod.io/v2/YOUR_ENDPOINT_ID/run \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"input": {"test": true}}'
```

## Cost Optimization

### Serverless Endpoint
- **Idle**: $0/hour
- **Processing**: $0.20-$0.40/hour (only when running)
- **Estimated**: $2-5/month for light usage

### Pod Endpoint
- **Always-on**: $0.20-$0.40/hour = $144-$288/month
- **Recommended**: Use serverless for production

## Integration Code

The main application automatically detects RunPod configuration and uses it when available.

**In `services/processing_service.py`:**

```python
import config

# Check if RunPod is configured
if config.RUNPOD_API_KEY and config.RUNPOD_ENDPOINT_ID:
    # Use RunPod for GPU processing
    result = runpod_ocr(image)
else:
    # Use local GPU/CPU
    result = local_ocr(image)
```

## Monitoring

### Check RunPod Usage

1. Go to RunPod dashboard
2. Navigate to "Usage" or "Billing"
3. View execution time and costs

### View Logs

**Serverless:**
- Check RunPod dashboard → Endpoints → Logs

**Pod:**
- SSH into pod: `ssh root@pod-ip -p port`
- View logs: `tail -f /var/log/api_server.log`

## Troubleshooting

### Connection Timeout

**Cause:** RunPod endpoint not responding

**Fix:**
```bash
# Check endpoint status
curl https://api.runpod.io/v2/YOUR_ENDPOINT_ID/health \
     -H "Authorization: Bearer YOUR_API_KEY"

# Restart pod (if using pod endpoint)
# Go to RunPod dashboard → Pods → Restart
```

### Cold Start Too Slow

**Cause:** Serverless endpoint takes time to start

**Solutions:**
1. Keep endpoint warm with periodic pings
2. Switch to pod endpoint for always-on
3. Increase worker count

### High Costs

**Cause:** Pod running 24/7

**Solutions:**
1. Switch to serverless endpoint
2. Auto-stop pod when not in use
3. Use cheaper GPU (RTX 3060 instead of A4000)

## Next Steps

1. Choose deployment option (serverless vs pod)
2. Follow setup instructions in `DEPLOYMENT_GUIDE.md`
3. Configure environment variables
4. Test integration
5. Monitor costs and performance

---

For detailed deployment instructions, see `../DEPLOYMENT_GUIDE.md`

