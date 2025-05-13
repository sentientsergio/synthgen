#!/usr/bin/env python3
"""
SynthGen Command Line Interface.

This module provides a command-line interface for the SynthGen tool,
allowing users to generate synthetic data for SQL Server schemas.
"""

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Optional

from orchestrator import Orchestrator


def parse_args():
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="SynthGen: Generate realistic, constraint-valid synthetic data for SQL Server schemas",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "sql_script",
        help="Path to the SQL Server CREATE script for the target schema"
    )
    
    parser.add_argument(
        "ref_data_dir",
        help="Directory containing reference data CSVs (one per lookup table)"
    )
    
    parser.add_argument(
        "--rules", "-r",
        help="Path to the Generation-Rules JSON document"
    )
    
    parser.add_argument(
        "--artifacts-dir", "-a",
        default="artifacts",
        help="Directory to store artifacts and output files"
    )
    
    parser.add_argument(
        "--run-id",
        help="Unique identifier for this run (for reproducibility)"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Random seed for reproducible generation"
    )
    
    parser.add_argument(
        "--llm-model",
        default="gpt-4o",
        help="Specific OpenAI model to use"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main CLI entry point.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    # Validate input paths
    sql_script_path = Path(args.sql_script)
    if not sql_script_path.is_file():
        print(f"Error: SQL script not found: {args.sql_script}", file=sys.stderr)
        return 1
    
    ref_data_dir = Path(args.ref_data_dir)
    if not ref_data_dir.is_dir():
        print(f"Error: Reference data directory not found: {args.ref_data_dir}", file=sys.stderr)
        return 1
    
    if args.rules:
        rules_path = Path(args.rules)
        if not rules_path.is_file():
            print(f"Error: Rules file not found: {args.rules}", file=sys.stderr)
            return 1
    else:
        rules_path = None
    
    # Use provided seed or generate a random one
    seed = args.seed
    if seed is None:
        seed = random.randint(1, 1_000_000)
        print(f"Using random seed: {seed}")
    
    # Create and run the orchestrator
    orchestrator = Orchestrator(
        sql_script_path=sql_script_path,
        ref_data_dir=ref_data_dir,
        rules_path=rules_path,
        run_id=args.run_id,
        artifacts_dir=args.artifacts_dir,
        llm_provider="openai",  # Only using OpenAI for PoC
        llm_model=args.llm_model,
        seed=seed
    )
    
    try:
        # Save run metadata
        orchestrator.save_run_metadata()
        
        # Run the pipeline
        result = orchestrator.run()
        
        # Print summary
        print("\nExecution Summary:")
        print(f"  Run ID: {result['run_id']}")
        print(f"  Execution time: {result['execution_time']:.2f} seconds")
        print(f"  Artifacts directory: {result['artifacts_dir']}")
        
        if result.get("errors"):
            print(f"  Errors: {len(result['errors'])}")
            return 1
        else:
            print("  Status: Success")
            print(f"  Validation result: {result.get('validation_result', 'unknown')}")
            return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 