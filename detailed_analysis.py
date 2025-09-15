#!/usr/bin/env python3
"""
Detailed analysis of SOA rules, focusing on tmaxfrac and multi-level structures
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def analyze_tmaxfrac_and_multilevel():
    """Deep dive into tmaxfrac parameter and multi-level rule structures"""
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    print("=== DETAILED SOA RULES ANALYSIS ===")
    
    # Focus on sheets with SOA rules
    soa_sheets = [
        "10HV SOA SYM ON-OFF",
        "10HV SOA CAPS", 
        "10HV SOA SUB Well",
        "10HV SOA OXRisk Drift",
        "10HV SOA SUB Well HV"
    ]
    
    rules_data = {}
    
    for sheet_name in soa_sheets:
        print(f"\n{'='*80}")
        print(f"ANALYZING: {sheet_name}")
        print(f"{'='*80}")
        
        try:
            # Read with headers to understand structure better
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Find tmaxfrac rows and analyze structure
            tmaxfrac_info = analyze_tmaxfrac_structure(df, sheet_name)
            if tmaxfrac_info:
                rules_data[sheet_name] = tmaxfrac_info
                
        except Exception as e:
            print(f"Error analyzing {sheet_name}: {e}")
    
    # Generate unified rule format
    print(f"\n{'='*80}")
    print("UNIFIED RULE FORMAT ANALYSIS")
    print(f"{'='*80}")
    
    generate_unified_format(rules_data)

def analyze_tmaxfrac_structure(df, sheet_name):
    """Analyze the tmaxfrac parameter structure in detail"""
    print(f"\nAnalyzing tmaxfrac structure in {sheet_name}...")
    
    # Find tmaxfrac row
    tmaxfrac_row = None
    for idx, row in df.iterrows():
        if any('tmaxfrac' in str(cell).lower() for cell in row if pd.notna(cell)):
            tmaxfrac_row = idx
            break
    
    if tmaxfrac_row is None:
        print("No tmaxfrac found in this sheet")
        return None
    
    print(f"Found tmaxfrac at row {tmaxfrac_row}")
    
    # Get tmaxfrac values
    tmaxfrac_values = []
    tmaxfrac_data = df.iloc[tmaxfrac_row]
    for col_idx, value in enumerate(tmaxfrac_data):
        if pd.notna(value) and str(value).replace('.', '').replace('-', '').isdigit():
            tmaxfrac_values.append(float(value))
    
    print(f"tmaxfrac values: {tmaxfrac_values}")
    
    # Analyze rule structure around tmaxfrac
    rule_structure = {}
    
    # Look for parameter names and their corresponding values
    start_row = max(0, tmaxfrac_row - 5)
    end_row = min(len(df), tmaxfrac_row + 50)
    
    parameters = []
    severity_levels = []
    
    for idx in range(start_row, end_row):
        row_data = df.iloc[idx]
        
        # Check for severity levels
        if pd.notna(row_data.iloc[0]) and str(row_data.iloc[0]).lower() in ['high', 'medium', 'low', 'severity']:
            severity = str(row_data.iloc[0]).lower()
            if severity != 'severity':
                severity_levels.append(severity)
        
        # Check for parameter names (usually in second column)
        if len(row_data) > 1 and pd.notna(row_data.iloc[1]):
            param_name = str(row_data.iloc[1])
            if param_name not in ['parameter', 'tmaxfrac', 'nan'] and len(param_name) > 2:
                # Get values for this parameter across tmaxfrac levels
                param_values = []
                for col_idx in range(2, min(len(row_data), 2 + len(tmaxfrac_values))):
                    if pd.notna(row_data.iloc[col_idx]):
                        value = str(row_data.iloc[col_idx])
                        param_values.append(value)
                
                if param_values:
                    parameters.append({
                        'name': param_name,
                        'values': param_values,
                        'row': idx
                    })
    
    rule_structure = {
        'tmaxfrac_values': tmaxfrac_values,
        'parameters': parameters,
        'severity_levels': list(set(severity_levels))
    }
    
    print(f"Found {len(parameters)} parameters with multi-level values")
    print(f"Severity levels: {severity_levels}")
    
    # Show some examples
    print("\nExample parameters:")
    for i, param in enumerate(parameters[:5]):
        print(f"  {param['name']}: {param['values']}")
    
    return rule_structure

def generate_unified_format(rules_data):
    """Generate a unified JSON format for SOA rules"""
    
    print("\nProposed Unified SOA Rule Format:")
    print("-" * 50)
    
    # Create a comprehensive rule schema
    unified_schema = {
        "soa_rule_schema": {
            "version": "1.0",
            "technology": "smos10hv",
            "description": "Unified format for SOA (Safe Operating Area) rules",
            "rule_structure": {
                "device_type": "string",  # e.g., "nmos", "pmos", "capacitor"
                "rule_category": "string",  # e.g., "voltage_limits", "current_limits"
                "multi_level_config": {
                    "enabled": "boolean",
                    "tmaxfrac_levels": "array of numbers",  # e.g., [0.1, 0.01, 0.0]
                    "description": "Temperature fraction levels for multi-level rules"
                },
                "parameters": {
                    "parameter_name": {
                        "type": "string",  # "voltage", "current", "temperature"
                        "unit": "string",  # "V", "A", "C"
                        "severity": "string",  # "high", "medium", "low"
                        "values": {
                            "single_level": "number or string",
                            "multi_level": "array corresponding to tmaxfrac_levels"
                        },
                        "conditions": "array of condition objects",
                        "description": "string"
                    }
                }
            }
        }
    }
    
    # Create example rules based on analyzed data
    example_rules = []
    
    for sheet_name, rule_data in rules_data.items():
        if rule_data and 'parameters' in rule_data:
            device_type = extract_device_type(sheet_name)
            
            rule = {
                "device_type": device_type,
                "rule_category": extract_rule_category(sheet_name),
                "multi_level_config": {
                    "enabled": True,
                    "tmaxfrac_levels": rule_data['tmaxfrac_values'],
                    "description": f"Multi-level rules for {device_type} with temperature fraction scaling"
                },
                "parameters": {}
            }
            
            # Convert parameters to unified format
            for param in rule_data['parameters'][:3]:  # Show first 3 as examples
                param_name = param['name']
                rule["parameters"][param_name] = {
                    "type": infer_parameter_type(param_name),
                    "unit": infer_unit(param_name),
                    "severity": "high",  # Default, could be extracted from data
                    "values": {
                        "multi_level": param['values']
                    },
                    "description": f"Multi-level {param_name} limits"
                }
            
            example_rules.append(rule)
    
    # Print the schema and examples
    print(json.dumps(unified_schema, indent=2))
    
    print(f"\n{'='*50}")
    print("EXAMPLE RULES IN UNIFIED FORMAT:")
    print(f"{'='*50}")
    
    for rule in example_rules:
        print(json.dumps(rule, indent=2))
        print("-" * 30)

def extract_device_type(sheet_name):
    """Extract device type from sheet name"""
    if "SYM ON-OFF" in sheet_name:
        return "mos_transistor"
    elif "CAPS" in sheet_name:
        return "capacitor"
    elif "SUB Well" in sheet_name:
        return "substrate_well"
    elif "OXRisk" in sheet_name:
        return "oxide_reliability"
    else:
        return "unknown"

def extract_rule_category(sheet_name):
    """Extract rule category from sheet name"""
    if "SOA" in sheet_name:
        return "safe_operating_area"
    else:
        return "general_limits"

def infer_parameter_type(param_name):
    """Infer parameter type from name"""
    param_lower = param_name.lower()
    if 'v' in param_lower and ('high' in param_lower or 'low' in param_lower):
        return "voltage"
    elif 'i' in param_lower or 'current' in param_lower:
        return "current"
    elif 'temp' in param_lower or 't' in param_lower:
        return "temperature"
    else:
        return "general"

def infer_unit(param_name):
    """Infer unit from parameter name"""
    param_lower = param_name.lower()
    if 'v' in param_lower:
        return "V"
    elif 'i' in param_lower or 'current' in param_lower:
        return "A"
    elif 'temp' in param_lower:
        return "C"
    else:
        return "dimensionless"

if __name__ == "__main__":
    analyze_tmaxfrac_and_multilevel()