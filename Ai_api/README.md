# Support Ticket Classifier

This API processes support tickets to classify their category and urgency.

## Testing the API

To test the API locally, make sure to set `LLM_STUB=1` in your environment variables to enable Stub Mode and use a running instance of the FastAPI application (e.g., at port 8000).

### Valid Request
Here is a valid cURL command testing the `/api/v1/triage` endpoint with a valid JSON payload:

```bash
curl -X POST http://localhost:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{"text": "I was charged twice for my subscription this month."}'
```

### Invalid Request
Here is an invalid cURL command testing the endpoint with a missing text field to trigger a schema validation error:

```bash
curl -X POST http://localhost:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{}'
```
