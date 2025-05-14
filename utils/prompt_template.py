"""
Prompt template system for loading and formatting prompts from files.

This module provides utilities for loading prompt templates from files and
formatting them with dynamic values.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent


class PromptTemplate:
    """
    A class for loading and formatting prompt templates.
    
    Prompt templates are stored in the prompts/ directory and organized
    by agent type. This class handles loading these templates and formatting
    them with dynamic values.
    """
    
    def __init__(self, template_path: str):
        """
        Initialize a PromptTemplate.
        
        Args:
            template_path: Path to the template file, relative to the prompts/ directory
        """
        self.template_path = template_path
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """
        Load the template from the file.
        
        Returns:
            The template as a string
        
        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        full_path = PROJECT_ROOT / "prompts" / self.template_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template not found: {full_path}")
    
    def format(self, **kwargs: Any) -> str:
        """
        Format the template with the provided values.
        
        Args:
            **kwargs: Dynamic values to insert into the template
        
        Returns:
            The formatted template as a string
        """
        return self.template.format(**kwargs)


def load_prompt(agent_type: str, prompt_name: str) -> PromptTemplate:
    """
    Load a prompt template for a specific agent.
    
    Args:
        agent_type: Type of agent (e.g., 'schema_parser', 'ref_data', 'data_synth')
        prompt_name: Name of the prompt template (without extension)
    
    Returns:
        A PromptTemplate instance
    """
    template_path = f"{agent_type}/{prompt_name}.prompt.md"
    return PromptTemplate(template_path) 