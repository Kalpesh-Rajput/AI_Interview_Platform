#!/usr/bin/env python3
"""
Test script for AWS Bedrock integration.

This script validates the Bedrock client configuration and basic functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings
from app.services.bedrock import BedrockClient, parse_json_response, BedrockError


async def test_bedrock_client():
    """Test Bedrock client initialization and basic functionality."""
    
    print("=" * 70)
    print("AWS Bedrock Integration Test Suite")
    print("=" * 70)
    
    # Test 1: Configuration Loading
    print("\n[TEST 1] Configuration Loading")
    print("-" * 70)
    try:
        settings = get_settings()
        print(f"✓ Settings loaded successfully")
        print(f"  - AWS Region: {settings.aws_region}")
        print(f"  - Bearer Token: {'***' + settings.aws_bearer_token_bedrock[-4:] if settings.aws_bearer_token_bedrock else 'NOT SET'}")
        print(f"  - Model Parsing: {settings.model_parsing}")
        print(f"  - Model Context: {settings.model_context}")
        print(f"  - Model Questions: {settings.model_questions}")
        print(f"  - Model Explanation: {settings.model_explanation}")
        print(f"  - Model Supervisor: {settings.model_supervisor}")
    except Exception as exc:
        print(f"✗ Failed to load settings: {exc}")
        return False
    
    # Test 2: Bedrock Client Initialization
    print("\n[TEST 2] Bedrock Client Initialization")
    print("-" * 70)
    try:
        client = BedrockClient()
        print(f"✓ BedrockClient initialized successfully")
        print(f"  - Client type: {type(client.client).__name__}")
        print(f"  - Region: {settings.aws_region}")
    except BedrockError as exc:
        if "not configured" in str(exc):
            print(f"⚠ BedrockClient initialization skipped: {exc}")
            print(f"  → Set AWS_BEARER_TOKEN_BEDROCK environment variable to enable")
        else:
            print(f"✗ BedrockClient initialization failed: {exc}")
            return False
    except Exception as exc:
        print(f"✗ Unexpected error: {exc}")
        return False
    
    # Test 3: JSON Parsing
    print("\n[TEST 3] JSON Response Parsing")
    print("-" * 70)
    test_cases = [
        ('{"test": "value"}', "Plain JSON"),
        ('```json\n{"test": "value"}\n```', "JSON with markdown"),
        ('```\n{"test": "value"}\n```', "JSON with markdown (no lang)"),
        ('  {"test": "value"}  ', "JSON with whitespace"),
    ]
    
    for test_json, description in test_cases:
        try:
            result = parse_json_response(test_json)
            print(f"✓ {description}: {result}")
        except Exception as exc:
            print(f"✗ {description}: {exc}")
            return False
    
    # Test 4: Model Availability
    print("\n[TEST 4] Model Configuration Validation")
    print("-" * 70)
    required_models = [
        settings.model_parsing,
        settings.model_context,
        settings.model_questions,
        settings.model_explanation,
        settings.model_supervisor,
    ]
    
    for model in set(required_models):
        if model:
            print(f"✓ Model configured: {model}")
        else:
            print(f"⚠ Model not configured (empty string)")
    
    if not all(required_models):
        print(f"⚠ Some models are not configured")
    
    # Test 5: Error Handling
    print("\n[TEST 5] Error Handling")
    print("-" * 70)
    
    # Test missing bearer token
    try:
        if not settings.aws_bearer_token_bedrock:
            raise BedrockError("AWS_BEARER_TOKEN_BEDROCK is not configured.")
        print("✓ Bearer token is configured")
    except BedrockError as exc:
        print(f"⚠ {exc}")
    
    # Test JSON parsing error handling
    try:
        parse_json_response("invalid json {]")
        print("✗ Should have raised error for invalid JSON")
        return False
    except BedrockError as exc:
        print(f"✓ Invalid JSON error handling: {type(exc).__name__}")
    
    print("\n" + "=" * 70)
    print("Test Suite Summary")
    print("=" * 70)
    print("""
Configuration Status:
- AWS Region: REQUIRED (default: ap-south-1)
- AWS Bearer Token: REQUIRED
- Models: CONFIGURED

To complete setup:
1. Set AWS_BEARER_TOKEN_BEDROCK in .env or environment
2. Verify AWS_REGION matches your deployment
3. Ensure Bedrock models are available in your AWS account

See BEDROCK_SETUP.md for detailed instructions.
    """)
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_bedrock_client())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as exc:
        print(f"\n\n✗ Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
