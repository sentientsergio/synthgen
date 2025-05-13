"""
File I/O utilities for SynthGen.

This module provides functions for reading and writing various file types,
including SQL scripts, CSV files, and JSON files.
"""

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read a text file and return its contents as a string.
    
    Args:
        file_path: Path to the file
        encoding: File encoding
        
    Returns:
        File contents as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def write_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    """Write a string to a text file.
    
    Args:
        file_path: Path to the file
        content: String content to write
        encoding: File encoding
        
    Raises:
        IOError: If the file cannot be written
    """
    # Create directory if it doesn't exist
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)


def read_json(file_path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
    """Read a JSON file and return its contents as a dictionary.
    
    Args:
        file_path: Path to the JSON file
        encoding: File encoding
        
    Returns:
        JSON contents as a dictionary
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with open(file_path, 'r', encoding=encoding) as f:
        return json.load(f)


def write_json(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    indent: int = 2,
    encoding: str = 'utf-8'
) -> None:
    """Write a dictionary to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Dictionary to write
        indent: Number of spaces for indentation
        encoding: File encoding
        
    Raises:
        IOError: If the file cannot be written
    """
    # Create directory if it doesn't exist
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        json.dump(data, f, indent=indent, sort_keys=True)


def read_csv(
    file_path: Union[str, Path],
    has_header: bool = True,
    delimiter: str = ',',
    encoding: str = 'utf-8'
) -> List[Dict[str, str]]:
    """Read a CSV file and return its contents as a list of dictionaries.
    
    If has_header is True, the first row is used as keys for each dictionary.
    Otherwise, the dictionaries use column indices as keys.
    
    Args:
        file_path: Path to the CSV file
        has_header: Whether the CSV has a header row
        delimiter: CSV delimiter
        encoding: File encoding
        
    Returns:
        List of dictionaries, one per row
        
    Raises:
        FileNotFoundError: If the file does not exist
        csv.Error: If the file is not valid CSV
    """
    with open(file_path, 'r', encoding=encoding, newline='') as f:
        if has_header:
            reader = csv.DictReader(f, delimiter=delimiter)
            return list(reader)
        else:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
            return [
                {str(i): value for i, value in enumerate(row)}
                for row in rows
            ]


def write_csv(
    file_path: Union[str, Path],
    data: List[Dict[str, Any]],
    fieldnames: Optional[List[str]] = None,
    delimiter: str = ',',
    encoding: str = 'utf-8'
) -> None:
    """Write a list of dictionaries to a CSV file.
    
    Args:
        file_path: Path to the CSV file
        data: List of dictionaries to write
        fieldnames: List of field names to use as the header row
                   If None, uses the keys of the first dictionary
        delimiter: CSV delimiter
        encoding: File encoding
        
    Raises:
        IOError: If the file cannot be written
    """
    # Create directory if it doesn't exist
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    if not fieldnames and data:
        fieldnames = list(data[0].keys())
    
    with open(file_path, 'w', encoding=encoding, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)


def read_sql_script(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read a SQL script file and return its contents as a string.
    
    This is a convenience wrapper around read_file that may include
    additional SQL-specific preprocessing in the future.
    
    Args:
        file_path: Path to the SQL script file
        encoding: File encoding
        
    Returns:
        SQL script contents as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    return read_file(file_path, encoding)


def list_files(
    directory: Union[str, Path],
    pattern: str = '*',
    recursive: bool = False
) -> List[Path]:
    """List files in a directory that match a glob pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
        
    Raises:
        FileNotFoundError: If the directory does not exist
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist")
    
    if recursive:
        return list(directory_path.glob(f"**/{pattern}"))
    else:
        return list(directory_path.glob(pattern))


def ensure_directory(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for the directory
    """
    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path 