"""
Base Agent class that defines the interface and common functionality for all agents.

All specialized agents will inherit from this class and implement their specific behavior.
"""

import json
import os
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


class Agent(ABC):
    """Base class for all agents in the SynthGen pipeline.
    
    Provides common functionality for LLM interaction, logging, artifact generation,
    and error handling that all agents need.
    """
    
    def __init__(
        self,
        name: str,
        run_id: Optional[str] = None,
        artifacts_dir: str = "artifacts",
        seed: Optional[int] = None,
    ):
        """Initialize the base agent.
        
        Args:
            name: Name of the agent (used for logging and artifact directories)
            run_id: Unique identifier for the current run, used for reproducibility
                   and artifact organization. If not provided, a timestamp-based ID is generated.
            artifacts_dir: Root directory for storing artifacts
            seed: Seed value for LLM calls to ensure reproducibility
        """
        self.name = name
        self.run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.artifacts_dir = artifacts_dir
        self.seed = seed
        
        # Create agent-specific artifact directory
        self.agent_artifacts_dir = Path(self.artifacts_dir) / self.run_id / self.name
        os.makedirs(self.agent_artifacts_dir, exist_ok=True)
        
        # Initialize logger
        self._setup_logging()
        
        self.logger.info(f"Initialized {self.name} agent with run_id: {self.run_id}")
    
    def _setup_logging(self) -> None:
        """Set up logging for the agent."""
        # Placeholder for logging setup
        # In a real implementation, this would configure a proper logger
        self.logger = type('SimpleLogger', (), {
            'info': lambda self, msg: print(f"[INFO] {self.name}: {msg}"),
            'error': lambda self, msg: print(f"[ERROR] {self.name}: {msg}"),
            'warning': lambda self, msg: print(f"[WARNING] {self.name}: {msg}"),
        })()
        
        # Bind the agent name to the logger methods for convenience
        name = self.name
        self.logger.info = lambda msg: print(f"[INFO] {name}: {msg}")
        self.logger.error = lambda msg: print(f"[ERROR] {name}: {msg}")
        self.logger.warning = lambda msg: print(f"[WARNING] {name}: {msg}")
    
    def save_artifact(self, name: str, content: Union[str, Dict[str, Any]], is_json: bool = False) -> Path:
        """Save an artifact to the agent's artifact directory.
        
        Args:
            name: Name of the artifact file (without extension)
            content: Content to save (string or dict for JSON)
            is_json: Whether to save as JSON (adds .json extension and pretty-prints)
            
        Returns:
            Path to the saved artifact
        """
        if is_json:
            file_path = self.agent_artifacts_dir / f"{name}.json"
            # Convert to string if it's a dict
            if isinstance(content, dict):
                content = json.dumps(content, indent=2, sort_keys=True)
        else:
            file_path = self.agent_artifacts_dir / f"{name}.md"
        
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Saved artifact: {file_path}")
        return file_path
    
    def save_prompt(self, prompt: str) -> Path:
        """Save the prompt used for LLM call to an artifact.
        
        Args:
            prompt: The prompt content
            
        Returns:
            Path to the saved prompt file
        """
        return self.save_artifact("prompt", prompt)
    
    def save_error(self, error_message: str, error_details: Optional[Dict[str, Any]] = None) -> Path:
        """Save error information to an artifact.
        
        Args:
            error_message: Main error message
            error_details: Additional error details as a dictionary
            
        Returns:
            Path to the saved error file
        """
        content = f"# Error in {self.name}\n\n{error_message}\n\n"
        
        if error_details:
            content += "## Details\n\n```json\n"
            content += json.dumps(error_details, indent=2, sort_keys=True)
            content += "\n```\n"
        
        return self.save_artifact("error", content)
    
    def handle_llm_error(self, error: Exception, retry_count: int = 3, backoff_factor: float = 2.0) -> Optional[Any]:
        """Handle errors in LLM API calls with retry logic.
        
        Args:
            error: The exception that occurred
            retry_count: Number of retries to attempt
            backoff_factor: Multiplier for exponential backoff between retries
            
        Returns:
            Result from successful retry or None if all retries failed
        """
        self.logger.error(f"LLM API error: {str(error)}")
        
        if retry_count <= 0:
            self.save_error(
                "Maximum retries exceeded for LLM API call",
                {"error_type": type(error).__name__, "error_message": str(error)}
            )
            return None
        
        # Exponential backoff
        wait_time = backoff_factor ** (3 - retry_count)
        self.logger.info(f"Retrying in {wait_time:.2f} seconds... ({retry_count} retries left)")
        time.sleep(wait_time)
        
        try:
            # This would be implemented in subclasses
            return self.retry_llm_call()
        except Exception as e:
            return self.handle_llm_error(e, retry_count - 1, backoff_factor)
    
    @abstractmethod
    def retry_llm_call(self) -> Any:
        """Retry the last LLM API call.
        
        To be implemented by subclasses with their specific LLM call logic.
        
        Returns:
            Result from the LLM API call
        """
        pass
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute the agent's main functionality.
        
        To be implemented by subclasses with their specific behavior.
        
        Args:
            args: Positional arguments specific to the agent
            kwargs: Keyword arguments specific to the agent
            
        Returns:
            Output of the agent's execution
        """
        pass 