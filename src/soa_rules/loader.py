"""
SOA Rules Loader - Load rules from JSON files
"""

import json
from pathlib import Path
from .soa_dsl_implementation import SOARulesEngine

def load_soa_rules(json_file: str = "complete_soa_rules.json") -> SOARulesEngine:
    """Load SOA rules from JSON file"""
    
    # Try to find the JSON file in various locations
    possible_paths = [
        Path(json_file),
        Path.cwd() / json_file,
        Path(__file__).parent.parent.parent / json_file,
    ]
    
    json_path = None
    for path in possible_paths:
        if path.exists():
            json_path = path
            break
    
    if json_path is None:
        raise FileNotFoundError(f"Could not find {json_file} in any of the expected locations")
    
    # Load and parse JSON
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    
    # Create engine and load data
    soa_engine = SOARulesEngine()
    soa_engine.load_from_json(json_data)
    
    return soa_engine

def load_complete_soa_rules() -> SOARulesEngine:
    """Load the complete SOA rules (744 parameters)"""
    return load_soa_rules("complete_soa_rules.json")

def load_basic_soa_rules() -> SOARulesEngine:
    """Load the basic SOA rules (14 parameters)"""
    return load_soa_rules("soa_rules.json")