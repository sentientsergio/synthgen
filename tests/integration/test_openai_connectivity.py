#!/usr/bin/env python3
"""
Test script to verify OpenAI API connectivity.

This script attempts to make a simple API call to OpenAI to verify that
credentials are properly configured and connectivity is working.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.llm import get_provider, APIKeyError
from dotenv import load_dotenv, find_dotenv, dotenv_values


def print_env_info():
    """Print information about environment variables for debugging."""
    print("\n==== Environment Debug Info ====")
    
    # Check for .env file
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        print(f".env file found at: {dotenv_path}")
        # Read values directly from file
        env_vars = dotenv_values(dotenv_path)
        if "OPENAI_API_KEY" in env_vars:
            key = env_vars["OPENAI_API_KEY"]
            print(f"OPENAI_API_KEY in .env file: {key[:4]}...{key[-4:]}")
        else:
            print("OPENAI_API_KEY not found in .env file")
    else:
        print(".env file not found")
    
    # Check environment variable (but we now ignore this)
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        print(f"OPENAI_API_KEY in system environment: {env_key[:4]}...{env_key[-4:]}")
        print("Note: This system environment variable will be IGNORED with our new approach")
    else:
        print("OPENAI_API_KEY not found in system environment")
    
    print("==== End Debug Info ====\n")


def setup_instructions():
    """Print instructions for setting up API keys."""
    print("\n==== API Key Setup Instructions ====")
    print("1. Get an OpenAI API key from: https://platform.openai.com/api-keys")
    print("2. Set up your environment by creating a .env file in the project root with:")
    print("   OPENAI_API_KEY=your-key-here")
    print("3. Run this test again to verify connectivity")
    print("=======================================\n")


def main():
    """Run a simple connectivity test for the OpenAI API."""
    print("Testing OpenAI API connectivity...")
    
    # Print detailed environment information
    print_env_info()
    
    try:
        # Get the OpenAI provider - this will validate the API key
        provider = get_provider("openai")
        
        # If we get here, the API key format is valid
        print("✅ API key format is valid")
        
        # Make a simple API call to verify connectivity
        print("Making test API call...")
        response = provider.generate(
            "Hello, this is a test message. Please respond with a short greeting.",
            max_tokens=100,
            model="gpt-3.5-turbo"  # Using a smaller/cheaper model for the test
        )
        
        print("\nAPI Response:")
        print(f"{response}")
        
        print("\n✅ OpenAI API connectivity test passed successfully!")
        return 0
    
    except APIKeyError as e:
        print(f"\n❌ API Key Error: {str(e)}")
        setup_instructions()
        return 1
    
    except Exception as e:
        print(f"\n❌ OpenAI API connectivity test failed: {str(e)}")
        
        # Check if this might be a network issue
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            print("\nThis appears to be a network connectivity issue.")
            print("Please check your internet connection and try again.")
        else:
            # For other errors, show setup instructions
            setup_instructions()
        
        return 1


if __name__ == "__main__":
    sys.exit(main()) 