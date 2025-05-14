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
import re

from utils.prompt_template import load_prompt


class Agent(ABC):
    """Base class for all agents in the SynthGen pipeline.
    
    Provides common functionality for LLM interaction, logging, artifact generation,
    and error handling that all agents need.
    """
    
    def __init__(
        self,
        name: str,
        run_id: Optional[str] = None,
        artifacts_dir: str = "runs",
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
        
        # Create standardized run directories
        self.run_dir = Path(self.artifacts_dir) / self.run_id
        self._create_run_directories()
        
        # Initialize logger
        self._setup_logging()
        
        self.logger.info(f"Initialized {self.name} agent with run_id: {self.run_id}")
    
    def _create_run_directories(self) -> None:
        """Create the standardized directory structure for a run."""
        # Create main run directory
        os.makedirs(self.run_dir, exist_ok=True)
        
        # Create subdirectories
        for subdir in ["inputs", "ir", "outputs", "traces", "logs"]:
            os.makedirs(self.run_dir / subdir, exist_ok=True)
    
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
    
    def get_inputs_dir(self) -> Path:
        """Get the inputs directory for this run."""
        return self.run_dir / "inputs"
    
    def get_ir_dir(self) -> Path:
        """Get the IR directory for this run."""
        return self.run_dir / "ir"
    
    def get_outputs_dir(self) -> Path:
        """Get the outputs directory for this run."""
        return self.run_dir / "outputs"
    
    def get_traces_dir(self) -> Path:
        """Get the traces directory for this run."""
        return self.run_dir / "traces"
    
    def get_logs_dir(self) -> Path:
        """Get the logs directory for this run."""
        return self.run_dir / "logs"
    
    def save_artifact(self, name: str, content: Union[str, Dict[str, Any]], artifact_type: str = "traces", is_json: bool = False) -> Path:
        """Save an artifact to the agent's artifact directory.
        
        Args:
            name: Name of the artifact file (without extension)
            content: Content to save (string or dict for JSON)
            artifact_type: Type of artifact (inputs, ir, outputs, traces, logs)
            is_json: Whether to save as JSON (adds .json extension and pretty-prints)
            
        Returns:
            Path to the saved artifact
        """
        artifact_dir = self.run_dir / artifact_type
        
        if is_json:
            file_path = artifact_dir / f"{name}.json"
            # Convert to string if it's a dict
            if isinstance(content, dict):
                content = json.dumps(content, indent=2, sort_keys=True)
        else:
            file_path = artifact_dir / f"{name}.md"
        
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
        return self.save_artifact(f"{self.name}_prompt", prompt, artifact_type="traces")
    
    def save_llm_response(self, response: str, identifier: str = "") -> Path:
        """Save the LLM response to an artifact.
        
        Args:
            response: The LLM response content
            identifier: Optional identifier to distinguish between multiple responses
            
        Returns:
            Path to the saved response file
        """
        name = f"{self.name}_response" if not identifier else f"{self.name}_response_{identifier}"
        return self.save_artifact(name, response, artifact_type="traces")
    
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
        
        return self.save_artifact(f"{self.name}_error", content, artifact_type="logs")
    
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
    
    @classmethod
    def load_prompt(cls, prompt_name: str) -> str:
        """Load a prompt template for this agent type.
        
        Args:
            prompt_name: Name of the prompt template (without extension)
            
        Returns:
            Formatted prompt template
        """
        # Dictionary mapping agent classes to directory names
        agent_dir_map = {
            "SchemaParseAgent": "schema_parser",
            "RefDataAgent": "ref_data",
            "DataSynthAgent": "data_synth"
        }
        
        # Get agent type from the agent name mapping or derive it
        agent_type = agent_dir_map.get(cls.__name__)
        if not agent_type:
            # Fall back to automatic conversion
            agent_type = cls.__name__.lower()
            if agent_type.endswith('agent'):
                agent_type = agent_type[:-5]  # Remove 'agent' suffix
                
                # Convert camel case to snake case (e.g., SchemaParser -> schema_parser)
                agent_type = re.sub(r'([a-z])([A-Z])', r'\1_\2', agent_type).lower()
        
        template = load_prompt(agent_type, prompt_name)
        return template
    
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