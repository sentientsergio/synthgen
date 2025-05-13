#!/usr/bin/env python3
"""
Simple test script for the file I/O utilities.

This script demonstrates the basic functionality of the file I/O utilities
to ensure they're working correctly before proceeding with more complex
components.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.file_io import (
    ensure_directory,
    read_file,
    write_file,
    read_json,
    write_json,
    read_csv,
    write_csv,
    list_files
)


def test_text_file_operations():
    """Test basic text file reading and writing."""
    print("\n=== Testing basic text file operations ===")
    
    # Create a temporary directory for our tests
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write a text file
        test_file = Path(temp_dir) / "test.txt"
        test_content = "Hello, World!\nThis is a test file."
        write_file(test_file, test_content)
        print(f"Wrote content to {test_file}")
        
        # Read the text file back
        read_content = read_file(test_file)
        print(f"Read content: {read_content}")
        
        # Verify content matches
        assert read_content == test_content, "File content doesn't match what was written"
        print("✅ Text content matches")


def test_json_operations():
    """Test JSON file reading and writing."""
    print("\n=== Testing JSON file operations ===")
    
    # Create a temporary directory for our tests
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write a JSON file
        test_file = Path(temp_dir) / "test.json"
        test_data = {
            "name": "Test",
            "values": [1, 2, 3],
            "nested": {
                "key": "value"
            }
        }
        write_json(test_file, test_data)
        print(f"Wrote JSON to {test_file}")
        
        # Read the JSON file back
        read_data = read_json(test_file)
        print(f"Read JSON: {read_data}")
        
        # Verify data matches
        assert read_data == test_data, "JSON data doesn't match what was written"
        print("✅ JSON data matches")


def test_csv_operations():
    """Test CSV file reading and writing."""
    print("\n=== Testing CSV file operations ===")
    
    # Create a temporary directory for our tests
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write a CSV file
        test_file = Path(temp_dir) / "test.csv"
        test_data = [
            {"name": "Alice", "age": "30", "city": "New York"},
            {"name": "Bob", "age": "25", "city": "San Francisco"},
            {"name": "Charlie", "age": "35", "city": "Chicago"}
        ]
        write_csv(test_file, test_data)
        print(f"Wrote CSV to {test_file}")
        
        # Read the CSV file back
        read_data = read_csv(test_file)
        print(f"Read CSV: {read_data}")
        
        # Verify data matches
        assert len(read_data) == len(test_data), "CSV row count doesn't match"
        assert all(rd["name"] in [td["name"] for td in test_data] for rd in read_data), "CSV data doesn't match"
        print("✅ CSV data matches")


def test_directory_operations():
    """Test directory operations."""
    print("\n=== Testing directory operations ===")
    
    # Create a temporary directory for our tests
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory
        sub_dir = Path(temp_dir) / "sub" / "nested"
        ensure_directory(sub_dir)
        print(f"Created directory: {sub_dir}")
        
        # Create some files in the directories
        write_file(Path(temp_dir) / "file1.txt", "Content 1")
        write_file(Path(temp_dir) / "file2.txt", "Content 2")
        write_file(Path(temp_dir) / "sub" / "file3.txt", "Content 3")
        write_file(Path(temp_dir) / "sub" / "nested" / "file4.txt", "Content 4")
        
        # List files in the directory
        files = list_files(temp_dir, pattern="*.txt")
        print(f"Files in {temp_dir}: {[f.name for f in files]}")
        assert len(files) == 2, "Should find 2 files in the root directory"
        
        # List files recursively
        files = list_files(temp_dir, pattern="*.txt", recursive=True)
        print(f"Files in {temp_dir} (recursive): {[str(f.relative_to(temp_dir)) for f in files]}")
        assert len(files) == 4, "Should find 4 files total"
        print("✅ Directory operations work correctly")


def main():
    """Run all tests."""
    print("Testing file I/O utilities...")
    
    test_text_file_operations()
    test_json_operations()
    test_csv_operations()
    test_directory_operations()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main() 