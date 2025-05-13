#!/usr/bin/env python3
"""
Simple test script for the LLM utilities.

This script demonstrates the basic functionality of the LLM utilities
to ensure the provider setup works correctly before proceeding with
more complex components.
"""

import os
import sys
from typing import Dict, Any
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.llm import get_provider, OpenAIProvider


def test_provider_factory():
    """Test the provider factory function."""
    print("\n=== Testing provider factory ===")
    
    # Get default provider (should be OpenAI)
    provider = get_provider()
    print(f"Default provider: {provider.__class__.__name__}")
    assert isinstance(provider, OpenAIProvider), "Default provider should be OpenAIProvider"
    print("✅ Default provider is OpenAIProvider")
    
    # Get OpenAI provider explicitly
    provider = get_provider("openai")
    print(f"Explicit provider: {provider.__class__.__name__}")
    assert isinstance(provider, OpenAIProvider), "Explicit provider should be OpenAIProvider"
    print("✅ Explicit provider is OpenAIProvider")
    
    # Test invalid provider
    try:
        provider = get_provider("invalid")
        print("❌ Invalid provider should have raised an error")
        assert False, "Invalid provider should have raised an error"
    except ValueError as e:
        print(f"Expected error for invalid provider: {e}")
        print("✅ Invalid provider correctly raises ValueError")


def test_mock_generation():
    """Test mock text generation."""
    print("\n=== Testing mock text generation ===")
    
    # Skip API key check for mock test
    os.environ["OPENAI_API_KEY"] = "mock_key_for_testing"
    
    provider = get_provider("openai")
    
    # Test text generation
    response = provider.generate("Test prompt", model="gpt-4o")
    print(f"Generated text: {response}")
    assert "mock response" in response.lower(), "Response should contain 'mock response'"
    print("✅ Mock text generation works")
    
    # Test JSON generation
    json_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "response": {"type": "string"},
            "schema": {"type": "string"}
        }
    }
    json_response = provider.generate_json("Test JSON prompt", json_schema, model="gpt-4o")
    print(f"Generated JSON: {json_response}")
    assert "response" in json_response, "JSON response should contain 'response' key"
    print("✅ Mock JSON generation works")


def main():
    """Run all tests."""
    print("Testing LLM utilities...")
    
    test_provider_factory()
    test_mock_generation()
    
    print("\n✅ All tests passed!")
    
    # Clean up environment variable
    if "OPENAI_API_KEY" in os.environ and os.environ["OPENAI_API_KEY"] == "mock_key_for_testing":
        del os.environ["OPENAI_API_KEY"]


if __name__ == "__main__":
    main() 