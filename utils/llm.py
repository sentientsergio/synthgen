"""
LLM API integration module for SynthGen.

This module provides utilities for interacting with OpenAI Language Model APIs,
handling common operations like preparing prompts, making API calls, and processing responses.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import OpenAI package
import openai

# Import dotenv for environment variable management
from dotenv import load_dotenv, find_dotenv, set_key


class APIKeyError(Exception):
    """Exception raised for API key issues."""
    pass


class LLMProvider:
    """Base class for all LLM API providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM provider.
        
        Args:
            api_key: API key for the provider. If not provided, will try to read from
                    environment variables.
        """
        self.api_key = api_key or self._get_api_key_from_env()
    
    def _get_api_key_from_env(self) -> str:
        """Get API key from environment variables."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        seed: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Control randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in the response
            seed: Seed for reproducibility (if supported)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Text response from the LLM
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def generate_json(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        temperature: float = 0.0,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a JSON response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            json_schema: JSON schema for the expected response
            temperature: Control randomness (0.0 = deterministic, 1.0 = creative)
            seed: Seed for reproducibility (if supported)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            JSON response from the LLM
        """
        raise NotImplementedError("Subclasses must implement this method")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    # Regular expression for validating OpenAI API keys - more flexible pattern
    API_KEY_PATTERN = r'^sk-[a-zA-Z0-9]+'
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to read from
                    environment variables.
        """
        super().__init__(api_key)
        self._validate_api_key()
        # Important: Pass the API key directly to the client rather than relying on env vars
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def _get_api_key_from_env(self) -> str:
        """Get OpenAI API key from .env file, ignoring environment variables.
        
        This method prioritizes the .env file over system environment variables
        to avoid conflicts with incorrectly set environment variables.
        
        Returns:
            API key from .env file
            
        Raises:
            APIKeyError: If API key is not found in .env file
        """
        # First, check for .env file
        dotenv_path = find_dotenv(usecwd=True)
        if not dotenv_path:
            # If not found in current directory, look in project root
            dotenv_path = Path(__file__).resolve().parent.parent / '.env'
            if not dotenv_path.exists():
                raise APIKeyError(
                    "No .env file found. Please create a .env file with OPENAI_API_KEY=your-key-here"
                )
        
        # Load the .env file
        load_dotenv(dotenv_path)
        
        # Read directly from file rather than environment to avoid any system env vars
        from dotenv import dotenv_values
        env_vars = dotenv_values(dotenv_path)
        api_key = env_vars.get("OPENAI_API_KEY")
        
        if not api_key:
            raise APIKeyError(
                "OPENAI_API_KEY not found in .env file. "
                "Please add it to your .env file with format: OPENAI_API_KEY=your-key-here"
            )
        
        return api_key
    
    def _validate_api_key(self) -> None:
        """Validate the OpenAI API key format."""
        if not re.match(self.API_KEY_PATTERN, self.api_key):
            raise APIKeyError(
                "Invalid API key format. OpenAI API keys should start with 'sk-' "
                "followed by alphanumeric characters."
            )
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        seed: Optional[int] = None,
        model: str = "gpt-4o",
        **kwargs
    ) -> str:
        """Generate a response using OpenAI's API.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Control randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in the response
            seed: Seed for reproducibility
            model: OpenAI model to use
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Text response from the LLM
        """
        # Create the messages with system and user content
        messages = [
            {"role": "system", "content": "You are a helpful assistant specialized in parsing SQL and generating structured data."},
            {"role": "user", "content": prompt}
        ]
        
        # Make the actual API call
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            **kwargs
        )
        
        # Extract and return the text content
        return response.choices[0].message.content
    
    def generate_json(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        temperature: float = 0.0,
        seed: Optional[int] = None,
        model: str = "gpt-4o",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a JSON response using OpenAI's API.
        
        Args:
            prompt: The prompt to send to the LLM
            json_schema: JSON schema for the expected response
            temperature: Control randomness (0.0 = deterministic, 1.0 = creative)
            seed: Seed for reproducibility
            model: OpenAI model to use
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            JSON response from the LLM
        """
        # Create the messages with system and user content
        messages = [
            {
                "role": "system", 
                "content": "You are a helpful assistant specialized in parsing SQL and generating structured data. Always respond with valid JSON."
            },
            {"role": "user", "content": prompt}
        ]
        
        # Define the response format to force JSON output
        response_format = {"type": "json_object"}
        
        # Make the API call with JSON response format
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            seed=seed,
            response_format=response_format,
            **kwargs
        )
        
        # Extract and parse the JSON content
        json_response = json.loads(response.choices[0].message.content)
        return json_response


def get_provider(provider_name: str = "openai", api_key: Optional[str] = None) -> LLMProvider:
    """Factory function to get an LLM provider instance.
    
    Args:
        provider_name: Name of the provider to use (currently only "openai" is supported)
        api_key: Optional API key to override environment variables
        
    Returns:
        An instance of the requested LLM provider
        
    Raises:
        ValueError: If provider_name is not supported
    """
    providers = {
        "openai": OpenAIProvider,
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unsupported provider: {provider_name}. Must be one of: {', '.join(providers.keys())}")
    
    return providers[provider_name](api_key=api_key) 