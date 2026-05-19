# AWS Bedrock Integration Guide

This document provides comprehensive setup and usage instructions for the AWS Bedrock integration with boto3.

## Overview

The AI Interview Platform now supports **AWS Bedrock** as the primary LLM provider using the official boto3 SDK with bearer token authentication. This replaces the previous OpenRouter implementation while maintaining the same LangGraph multi-agent workflow.

## Architecture

- **Service Layer**: `app/services/bedrock.py` - Core Bedrock client implementation
- **Configuration**: `app/core/config.py` - Environment variable management
- **Agent Nodes**: Updated to use BedrockClient instead of OpenRouterClient
  - `parsing_agent` - Document parsing
  - `context_extraction_agent` - Context analysis
  - `question_generation_agent` - Interview question generation
  - `explanation_agent` - Question explanation generation
  - `supervisor_agent` - Quality validation

## Prerequisites

1. **AWS Account** with access to Bedrock service
2. **AWS Bearer Token** for authentication
3. **AWS Region** (default: ap-south-1)
4. **Python 3.8+**

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This includes:
- `boto3>=1.28.0` - AWS SDK for Python
- All existing dependencies

### 2. Configure Environment Variables

Create or update `.env` file in the backend directory:

```env
# AWS Bedrock Configuration (Required)
AWS_BEARER_TOKEN_BEDROCK=your_bearer_token_here
AWS_REGION=ap-south-1

# Model Configuration
MODEL_PARSING=google.gemma-3-27b-it
MODEL_CONTEXT=google.gemma-3-27b-it
MODEL_QUESTIONS=google.gemma-3-27b-it
MODEL_EXPLANATION=google.gemma-3-27b-it
MODEL_SUPERVISOR=google.gemma-3-27b-it

# Optional Fallback Models
FALLBACK_MODELS=

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# LangSmith Integration (Optional)
LANGSMITH_API_KEY=
LANGSMITH_API_URL=
LANGSMITH_PROJECT=Interview Intelligence

# Quality Settings
MAX_SUPERVISOR_RETRIES=3
QUALITY_THRESHOLD=0.75
```

### 3. Verify Boto3 Configuration

Ensure boto3 is properly configured:

```bash
# Test boto3 installation
python -c "import boto3; print(boto3.__version__)"

# Verify Bedrock availability
python -c "import boto3; client = boto3.client('bedrock-runtime', region_name='ap-south-1'); print('Bedrock client created successfully')"
```

## Configuration Details

### AWS Credentials

#### Bearer Token Authentication

The Bedrock client uses bearer token authentication configured via:

1. **Environment Variable**: `AWS_BEARER_TOKEN_BEDROCK`
   - Set in `.env` file or system environment
   - Automatically loaded by the configuration system

2. **AWS Region**: `AWS_REGION`
   - Default: `ap-south-1`
   - Available regions: Check AWS Bedrock documentation for supported regions

#### How Bearer Token Auth Works

The `BedrockClient` class:

```python
# Automatically added to all Bedrock API requests
Authorization: Bearer {AWS_BEARER_TOKEN_BEDROCK}
```

This token is injected via boto3's event system:
- Intercepts all API calls
- Adds bearer token to request headers
- Retries with exponential backoff on authentication failures

### Model Configuration

All models use the **Google Gemma 3 27B** variant on Bedrock:

```env
MODEL_PARSING=google.gemma-3-27b-it
MODEL_CONTEXT=google.gemma-3-27b-it
MODEL_QUESTIONS=google.gemma-3-27b-it
MODEL_EXPLANATION=google.gemma-3-27b-it
MODEL_SUPERVISOR=google.gemma-3-27b-it
```

**Note**: These model IDs are specific to AWS Bedrock. Ensure you have access to these models in your AWS account.

## BedrockClient Features

### 1. Retry Logic

- **Automatic retries**: 3 attempts per request
- **Exponential backoff**: Built into boto3
- **Fallback models**: Configurable via `FALLBACK_MODELS`

### 2. Timeout Handling

- **Request timeout**: 120 seconds (configurable)
- **Async timeout**: Managed via `asyncio.wait_for()`
- **Graceful degradation**: Clear error messages

### 3. JSON Response Parsing

```python
# Handles various JSON formats
- Standard JSON
- JSON wrapped in markdown code blocks (```json ... ```)
- Malformed JSON with cleanup
```

### 4. Error Handling

Comprehensive error handling for:
- Authentication failures (`UnauthorizedException`)
- Rate limiting (`ThrottlingException`)
- Server errors (`ServiceUnavailableException`)
- Network errors and timeouts
- JSON parsing errors

### 5. Async-Compatible Architecture

```python
# All methods are async-first
async def chat_completion(...) -> str
async def stream_completion(...) -> AsyncIterator[str]
```

- Compatible with LangGraph's async workflow
- Non-blocking I/O via ThreadPoolExecutor
- Proper event loop handling

## Usage Examples

### Basic Chat Completion

```python
from app.services.bedrock import BedrockClient

client = BedrockClient()

messages = [
    {"role": "user", "content": "What is Python?"}
]

response = await client.chat_completion(
    model="google.gemma-3-27b-it",
    messages=messages,
    temperature=0.5,
    max_tokens=2048,
    json_mode=False,
    operation="example"
)

print(response)
```

### JSON Mode

```python
messages = [
    {"role": "user", "content": "Generate 3 interview questions in JSON format"}
]

response = await client.chat_completion(
    model="google.gemma-3-27b-it",
    messages=messages,
    temperature=0.7,
    max_tokens=4096,
    json_mode=True,
    operation="json_generation"
)

import json
data = json.loads(response)
```

### Streaming Responses

```python
async for chunk in client.stream_completion(
    model="google.gemma-3-27b-it",
    messages=messages,
    temperature=0.5,
    max_tokens=2048
):
    print(chunk, end="", flush=True)
```

## Running the Application

### Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

The server will:
1. Initialize BedrockClient on first request
2. Use bearer token for authentication
3. Route all LLM calls through Bedrock

### Environment Verification

On startup, the application logs:
```
Bedrock client initialized successfully with region=ap-south-1
```

If you see this message, Bedrock integration is working.

## Testing

### 1. Unit Testing

Run existing tests with Bedrock:
```bash
pytest backend/
```

### 2. Manual Testing

```bash
# Test parsing
python -c "
from app.agents.nodes.parsing import parsing_agent
from app.agents.state import InterviewState
import asyncio

state = InterviewState(
    jd_text='Python developer needed',
    resume_text='5 years Python experience',
    retry_count=0,
    supervisor_feedback=''
)

result = asyncio.run(parsing_agent(state))
print(result)
"
```

### 3. Full Pipeline Test

```bash
cd backend
python test.py
```

## Troubleshooting

### Error: "AWS_BEARER_TOKEN_BEDROCK is not configured"

**Solution**: Set the environment variable in `.env`:
```env
AWS_BEARER_TOKEN_BEDROCK=your_token_here
```

### Error: "Authentication failed" / UnauthorizedException

**Causes**:
- Invalid bearer token
- Expired token
- Incorrect AWS region

**Solution**:
1. Verify token is correct
2. Check token hasn't expired
3. Confirm region supports Bedrock: `ap-south-1`

### Error: "Model not available" / ModelNotFound

**Cause**: Model `google.gemma-3-27b-it` not available in your region

**Solution**:
- Check available models in your region
- Update `MODEL_*` environment variables
- Verify Bedrock service access in AWS console

### Error: "Rate limited by Bedrock"

**Cause**: Too many concurrent requests

**Solution**:
- Implemented automatic retry logic (3 attempts)
- Check AWS Bedrock quotas and limits
- Contact AWS support to increase limits

### Timeout Errors

**Cause**: Request exceeds 120-second limit

**Solution**:
- Reduce `max_tokens` parameter
- Check network connectivity
- Increase timeout in `BedrockClient._invoke_bedrock()`

## Production Checklist

- [ ] Set `AWS_BEARER_TOKEN_BEDROCK` in production environment
- [ ] Verify `AWS_REGION` matches your deployment region
- [ ] Configure LangSmith (optional) for monitoring
- [ ] Set appropriate `MAX_SUPERVISOR_RETRIES` (default: 3)
- [ ] Configure `CORS_ORIGINS` for frontend
- [ ] Test full pipeline with sample data
- [ ] Monitor CloudWatch logs for errors
- [ ] Set up alerts for authentication failures
- [ ] Review and adjust `QUALITY_THRESHOLD` if needed

## Migration from OpenRouter

If migrating from OpenRouter:

### What Changed

1. **Service Module**: `openrouter.py` → `bedrock.py`
2. **Client Class**: `OpenRouterClient` → `BedrockClient`
3. **Environment Variables**: 
   - Removed: `OPENROUTER_API_KEY`
   - Added: `AWS_BEARER_TOKEN_BEDROCK`, `AWS_REGION`
4. **Model IDs**: 
   - Changed from OpenRouter format to Bedrock format
   - Now using Bedrock Gemma models

### What Stayed the Same

- LangGraph multi-agent workflow
- Agent architecture and state management
- JSON mode and response parsing
- Error handling patterns
- Async/await patterns
- Configuration management

### Migration Steps

1. Update `.env` with AWS credentials
2. Update model names to Bedrock format
3. No code changes needed (already refactored)
4. Test with sample data
5. Monitor logs for any issues

## Performance Considerations

### Latency

- **Cold start**: ~2-3 seconds (Bedrock model loading)
- **Subsequent calls**: ~1-2 seconds per request
- **Streaming**: Real-time token generation

### Throughput

- **Concurrent requests**: Limited by AWS Bedrock quotas
- **Batch processing**: Sequential pipeline execution
- **Async operations**: Non-blocking per agent

### Cost Optimization

- Use appropriate `temperature` values (lower = less tokens)
- Set reasonable `max_tokens` limits
- Monitor token usage in CloudWatch

## Support and Documentation

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [boto3 Bedrock Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## License

This integration maintains the same license as the main project.
