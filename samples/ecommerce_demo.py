#!/usr/bin/env python3
"""
SynthGen E-commerce Demo
------------------------
This demonstration shows the complete synthetic data generation process for an e-commerce dataset.
It uses three input files:
1. SQL Schema (ecommerce.sql) - Defines the database structure
2. Reference Data (ecommerce_reference.csv) - Contains lookup tables and reference data
3. Rules (ecommerce_rules.json) - Defines patterns and relationships for data generation

The demo produces organized outputs in the runs directory with a unique run ID.
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path

# Add parent directory to path to import from project modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.schema_parse_agent import SchemaParseAgent
from agents.ref_data_agent import RefDataAgent
from agents.data_synth_agent import DataSynthAgent
from orchestrator import Orchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ====================================================================
# CONFIGURATION
# ====================================================================

# Input file paths (relative to this script)
INPUT_DIR = Path(__file__).parent
SCHEMA_FILE = INPUT_DIR / "sql" / "ecommerce.sql"
REFERENCE_FILE = INPUT_DIR / "ecommerce_reference.csv"
RULES_FILE = INPUT_DIR / "rules" / "ecommerce_rules.json"

# Output directory structure
RUN_ID = f"ecommerce_{int(time.time())}"  # Unique ID based on timestamp
OUTPUT_BASE_DIR = Path(__file__).parent.parent / "runs" / RUN_ID
INPUTS_DIR = OUTPUT_BASE_DIR / "inputs"
IR_DIR = OUTPUT_BASE_DIR / "ir"
OUTPUTS_DIR = OUTPUT_BASE_DIR / "outputs"
TRACES_DIR = OUTPUT_BASE_DIR / "traces"
LOGS_DIR = OUTPUT_BASE_DIR / "logs"

# Parameters
NUM_USERS = 100          # Number of user accounts to generate
NUM_PRODUCTS = 200       # Number of products to generate
NUM_ORDERS = 300         # Number of orders to generate
NUM_REVIEWS = 150        # Number of product reviews to generate
SEED = 42                # Random seed for reproducibility

# ====================================================================
# UTILITY FUNCTIONS
# ====================================================================

def setup_directories():
    """Create output directories if they don't exist."""
    for directory in [INPUTS_DIR, IR_DIR, OUTPUTS_DIR, TRACES_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def copy_input_files():
    """Copy input files to the inputs directory for reference."""
    import shutil
    
    # Create copies of input files in the runs directory
    shutil.copy(SCHEMA_FILE, INPUTS_DIR / "ecommerce.sql")
    shutil.copy(REFERENCE_FILE, INPUTS_DIR / "ecommerce_reference.csv") 
    shutil.copy(RULES_FILE, INPUTS_DIR / "ecommerce_rules.json")
    
    logger.info(f"Copied input files to {INPUTS_DIR}")

def load_rules():
    """Load rules from the JSON file."""
    with open(RULES_FILE, "r") as f:
        rules = json.load(f)
    return rules

# ====================================================================
# MAIN DEMO PROCESS
# ====================================================================

def run_demo():
    """Run the complete e-commerce data synthesis demo."""
    logger.info("Starting E-commerce Data Synthesis Demo")
    logger.info(f"Run ID: {RUN_ID}")
    
    # Setup
    setup_directories()
    copy_input_files()
    
    # Step 1: Parse the SQL schema
    logger.info("\n=== STEP 1: Parse SQL Schema ===")
    schema_agent = SchemaParseAgent(run_id=RUN_ID, artifacts_dir=str(TRACES_DIR), seed=SEED)
    schema = schema_agent.run(
        sql_script_path=str(SCHEMA_FILE),
        schema_name="EcommerceDB"
    )
    schema_ir_file = IR_DIR / "schema_ir.json"
    with open(schema_ir_file, "w") as f:
        f.write(schema.to_json(indent=2))
    logger.info(f"Schema parsed and saved to {schema_ir_file}")
    
    # Step 2: Process reference data
    logger.info("\n=== STEP 2: Process Reference Data ===")
    ref_data_agent = RefDataAgent(run_id=RUN_ID, artifacts_dir=str(TRACES_DIR), seed=SEED)
    schema_with_ref_data = ref_data_agent.run(
        schema=schema,
        ref_data_path=str(REFERENCE_FILE),
        intelligent_mapping=True
    )
    ref_data_ir_file = IR_DIR / "ref_data_ir.json"
    with open(ref_data_ir_file, "w") as f:
        f.write(schema_with_ref_data.to_json(indent=2))
    logger.info(f"Reference data processed and saved to {ref_data_ir_file}")
    
    # Step 3: Load rules
    logger.info("\n=== STEP 3: Load Rules ===")
    rules = load_rules()
    rules_ir_file = IR_DIR / "rules_ir.json"
    with open(rules_ir_file, "w") as f:
        json.dump(rules, f, indent=2)
    logger.info(f"Rules loaded and saved to {rules_ir_file}")
    
    # Step 4: Generate synthetic data
    logger.info("\n=== STEP 4: Generate Synthetic Data ===")
    data_synth_agent = DataSynthAgent(run_id=RUN_ID, artifacts_dir=str(TRACES_DIR), seed=SEED)
    
    # Prepare row counts for specific tables
    row_counts = {
        "User": NUM_USERS,
        "Product": NUM_PRODUCTS,
        "Order": NUM_ORDERS,
        "ProductReview": NUM_REVIEWS
    }
    
    output_files = data_synth_agent.run(
        schema=schema_with_ref_data,
        output_dir=str(OUTPUTS_DIR),
        row_counts=row_counts,
        custom_rules=rules.get("rules", {})
    )
    
    # Step 5: Summarize results
    logger.info("\n=== STEP 5: Summarize Results ===")
    summarize_results(output_files)
    
    logger.info("\n=== DEMO COMPLETED SUCCESSFULLY ===")
    logger.info(f"All outputs are in {OUTPUT_BASE_DIR}")
    
    # Return the output directory path for further inspection
    return OUTPUT_BASE_DIR

def summarize_results(output_files=None):
    """Summarize the generated data and provide statistics."""
    # This function would typically analyze the output files and provide statistics
    # For the demo, we'll just list the generated files
    
    output_files = list(OUTPUTS_DIR.glob("**/*"))
    
    logger.info(f"Generated {len(output_files)} output files:")
    for file in sorted(output_files):
        file_size = file.stat().st_size / 1024  # Size in KB
        logger.info(f"  - {file.relative_to(OUTPUT_BASE_DIR)} ({file_size:.1f} KB)")
    
    # Display sample counts
    logger.info("\nGenerated data summary:")
    logger.info(f"  - Users: {NUM_USERS}")
    logger.info(f"  - Products: {NUM_PRODUCTS}")
    logger.info(f"  - Orders: {NUM_ORDERS}")
    logger.info(f"  - Reviews: {NUM_REVIEWS}")

# ====================================================================
# COMMAND LINE INTERFACE
# ====================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="SynthGen E-commerce Demo")
    parser.add_argument("--users", type=int, default=NUM_USERS, help="Number of users to generate")
    parser.add_argument("--products", type=int, default=NUM_PRODUCTS, help="Number of products to generate")
    parser.add_argument("--orders", type=int, default=NUM_ORDERS, help="Number of orders to generate")
    parser.add_argument("--reviews", type=int, default=NUM_REVIEWS, help="Number of reviews to generate")
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed for reproducibility")
    return parser.parse_args()

# ====================================================================
# ENTRY POINT
# ====================================================================

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Update global variables with argument values
    NUM_USERS = args.users
    NUM_PRODUCTS = args.products
    NUM_ORDERS = args.orders
    NUM_REVIEWS = args.reviews
    SEED = args.seed
    
    # Run the demo
    output_dir = run_demo()
    
    print(f"\nTo explore the results, open: {output_dir}") 