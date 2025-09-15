#!/usr/bin/env python3
"""
Precise analysis of SOA rules with correct sheet reading
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def precise_soa_analysis():
    """Precise analysis of SOA rules and tmaxfrac"""
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    # Get exact sheet names
    xl_file = pd.ExcelFile(excel_file)
    sheet_names = xl_file.sheet_names
    
    print("Available sheets:")
    for i, name in enumerate(sheet_names):
        print(f"  {i}: '{name}'")
    
    # Analyze key SOA sheets
    soa_sheets = [name for name in sheet_names if 'SOA' in name]
    
    print(f"\nAnalyzing {len(soa_sheets)} SOA sheets...")
    
    all_rules = {}
    
    for sheet_name in soa_sheets:
        print(f"\n{'='*60}")
        print(f"SHEET: {sheet_name}")
        print(f"{'='*60}")
        
        # Read without headers first to see raw structure
        df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        print(f"Raw dimensions: {df_raw.shape}")
        
        # Find tmaxfrac and analyze structure
        rule_data = analyze_sheet_structure(df_raw, sheet_name)
        if rule_data:
            all_rules[sheet_name] = rule_data
    
    # Create comprehensive rule format
    create_soa_dsl(all_rules)

def analyze_sheet_structure(df, sheet_name):
    """Analyze individual sheet structure"""
    
    # Find tmaxfrac row
    tmaxfrac_row = None
    tmaxfrac_col = None
    
    for row_idx in range(min(20, df.shape[0])):
        for col_idx in range(df.shape[1]):
            cell_value = str(df.iloc[row_idx, col_idx]).lower()
            if 'tmaxfrac' in cell_value:
                tmaxfrac_row = row_idx
                tmaxfrac_col = col_idx
                print(f"Found tmaxfrac at row {row_idx}, col {col_idx}")
                break
        if tmaxfrac_row is not None:
            break
    
    if tmaxfrac_row is None:
        print("No tmaxfrac found")
        return None
    
    # Get tmaxfrac values (should be in the row below the tmaxfrac label)
    tmaxfrac_values = []
    if tmaxfrac_row + 1 < df.shape[0]:
        values_row = df.iloc[tmaxfrac_row + 1]
        for col_idx in range(tmaxfrac_col, min(tmaxfrac_col + 5, df.shape[1])):
            cell_value = values_row.iloc[col_idx]
            if pd.notna(cell_value):
                try:
                    val = float(cell_value)
                    tmaxfrac_values.append(val)
                except:
                    pass
    
    print(f"tmaxfrac values: {tmaxfrac_values}")
    
    # Find parameter structure
    parameters = []
    severity_col = 0  # Usually first column
    param_col = 1     # Usually second column
    
    # Look for parameters starting after tmaxfrac
    start_row = tmaxfrac_row + 2
    for row_idx in range(start_row, min(start_row + 50, df.shape[0])):
        row_data = df.iloc[row_idx]
        
        # Get severity and parameter name
        severity = str(row_data.iloc[severity_col]) if pd.notna(row_data.iloc[severity_col]) else ""
        param_name = str(row_data.iloc[param_col]) if pd.notna(row_data.iloc[param_col]) else ""
        
        # Skip empty or header rows
        if param_name in ['nan', 'parameter', ''] or len(param_name) < 3:
            continue
        
        # Get values for each tmaxfrac level
        param_values = []
        for i, tmaxfrac_val in enumerate(tmaxfrac_values):
            col_idx = tmaxfrac_col + i
            if col_idx < df.shape[1] and pd.notna(row_data.iloc[col_idx]):
                param_values.append(str(row_data.iloc[col_idx]))
        
        if param_values:
            parameters.append({
                'name': param_name,
                'severity': severity.lower() if severity.lower() in ['high', 'medium', 'low'] else 'unknown',
                'values': param_values,
                'tmaxfrac_mapping': dict(zip(tmaxfrac_values, param_values))
            })
    
    print(f"Found {len(parameters)} parameters")
    for param in parameters[:3]:  # Show first 3
        print(f"  {param['name']} ({param['severity']}): {param['values']}")
    
    return {
        'sheet_name': sheet_name,
        'tmaxfrac_values': tmaxfrac_values,
        'parameters': parameters,
        'device_info': extract_device_info(sheet_name)
    }

def extract_device_info(sheet_name):
    """Extract device information from sheet name"""
    info = {
        'technology': 'smos10hv',
        'device_type': 'unknown',
        'rule_category': 'soa'
    }
    
    if 'SYM ON-OFF' in sheet_name:
        info['device_type'] = 'mos_transistor'
        info['subcategory'] = 'symmetric_on_off'
    elif 'CAPS' in sheet_name:
        info['device_type'] = 'capacitor'
        info['subcategory'] = 'general'
    elif 'SUB Well' in sheet_name:
        info['device_type'] = 'substrate'
        info['subcategory'] = 'well_isolation'
    elif 'OXRisk' in sheet_name:
        info['device_type'] = 'oxide'
        info['subcategory'] = 'reliability_drift'
    
    return info

def create_soa_dsl(all_rules):
    """Create SOA Domain Specific Language (DSL) format"""
    
    print(f"\n{'='*80}")
    print("SOA DOMAIN SPECIFIC LANGUAGE (DSL) PROPOSAL")
    print(f"{'='*80}")
    
    # JSON-based DSL
    json_dsl = create_json_dsl(all_rules)
    
    # Python-based DSL
    python_dsl = create_python_dsl(all_rules)
    
    print("\n1. JSON-BASED DSL:")
    print("-" * 40)
    print(json.dumps(json_dsl, indent=2))
    
    print("\n2. PYTHON-BASED DSL:")
    print("-" * 40)
    print(python_dsl)

def create_json_dsl(all_rules):
    """Create JSON-based DSL for SOA rules"""
    
    dsl = {
        "soa_rules": {
            "version": "1.0",
            "technology": "smos10hv",
            "description": "SOA rules for semiconductor devices",
            "global_config": {
                "temperature_scaling": {
                    "enabled": True,
                    "method": "tmaxfrac",
                    "description": "Temperature fraction scaling for multi-level rules"
                }
            },
            "devices": {}
        }
    }
    
    for sheet_name, rule_data in all_rules.items():
        device_info = rule_data['device_info']
        device_key = f"{device_info['device_type']}_{device_info.get('subcategory', 'general')}"
        
        device_rules = {
            "device_type": device_info['device_type'],
            "subcategory": device_info.get('subcategory', 'general'),
            "multi_level": {
                "enabled": len(rule_data['tmaxfrac_values']) > 1,
                "tmaxfrac_levels": rule_data['tmaxfrac_values'],
                "description": "Temperature fraction levels for parameter scaling"
            },
            "parameters": {}
        }
        
        for param in rule_data['parameters']:
            param_key = param['name'].replace(' ', '_').lower()
            device_rules["parameters"][param_key] = {
                "name": param['name'],
                "severity": param['severity'],
                "type": infer_param_type(param['name']),
                "unit": infer_param_unit(param['name']),
                "values": {
                    "multi_level": param['tmaxfrac_mapping'] if rule_data['tmaxfrac_values'] else param['values'][0] if param['values'] else None
                },
                "conditions": [],
                "description": f"{param['severity']} severity limit for {param['name']}"
            }
        
        dsl["soa_rules"]["devices"][device_key] = device_rules
    
    return dsl

def create_python_dsl(all_rules):
    """Create Python-based DSL for SOA rules"""
    
    python_code = '''
# SOA Rules DSL - Python Implementation
from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
from enum import Enum

class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"

class ParameterType(Enum):
    VOLTAGE = "voltage"
    CURRENT = "current"
    TEMPERATURE = "temperature"
    GENERAL = "general"

@dataclass
class SOAParameter:
    name: str
    severity: Severity
    param_type: ParameterType
    unit: str
    values: Dict[float, Union[float, str]]  # tmaxfrac -> value mapping
    conditions: List[str] = field(default_factory=list)
    description: str = ""

@dataclass
class DeviceRules:
    device_type: str
    subcategory: str
    tmaxfrac_levels: List[float]
    parameters: Dict[str, SOAParameter]
    
    def get_parameter_value(self, param_name: str, tmaxfrac: float) -> Union[float, str, None]:
        """Get parameter value for specific tmaxfrac level"""
        if param_name in self.parameters:
            param = self.parameters[param_name]
            if tmaxfrac in param.values:
                return param.values[tmaxfrac]
            # Find closest tmaxfrac level
            closest = min(param.values.keys(), key=lambda x: abs(x - tmaxfrac))
            return param.values[closest]
        return None
    
    def validate_conditions(self, **kwargs) -> List[str]:
        """Validate device conditions against SOA rules"""
        violations = []
        for param_name, param in self.parameters.items():
            if param_name in kwargs:
                # Implementation would check actual values against limits
                pass
        return violations

# Example usage:
class SOARules:
    def __init__(self):
        self.devices = {}
    
    def add_device(self, device_key: str, rules: DeviceRules):
        self.devices[device_key] = rules
    
    def check_soa(self, device_type: str, **conditions) -> Dict[str, List[str]]:
        """Check SOA compliance for device with given conditions"""
        results = {}
        for device_key, device_rules in self.devices.items():
            if device_rules.device_type == device_type:
                violations = device_rules.validate_conditions(**conditions)
                if violations:
                    results[device_key] = violations
        return results

# Initialize SOA rules from Excel data
soa = SOARules()
'''
    
    # Add specific device examples from the analyzed data
    for sheet_name, rule_data in all_rules.items():
        device_info = rule_data['device_info']
        device_key = f"{device_info['device_type']}_{device_info.get('subcategory', 'general')}"
        
        python_code += f'''
# {sheet_name} rules
{device_key}_params = {{'''
        
        for param in rule_data['parameters'][:2]:  # Show first 2 parameters as example
            param_key = param['name'].replace(' ', '_').lower()
            python_code += f'''
    "{param_key}": SOAParameter(
        name="{param['name']}",
        severity=Severity.{param['severity'].upper()},
        param_type=ParameterType.{infer_param_type(param['name']).upper()},
        unit="{infer_param_unit(param['name'])}",
        values={param['tmaxfrac_mapping']},
        description="{param['severity']} limit for {param['name']}"
    ),'''
        
        python_code += f'''
}}

{device_key}_rules = DeviceRules(
    device_type="{device_info['device_type']}",
    subcategory="{device_info.get('subcategory', 'general')}",
    tmaxfrac_levels={rule_data['tmaxfrac_values']},
    parameters={device_key}_params
)

soa.add_device("{device_key}", {device_key}_rules)
'''
    
    return python_code

def infer_param_type(param_name):
    """Infer parameter type from name"""
    name_lower = param_name.lower()
    if 'v' in name_lower and ('high' in name_lower or 'low' in name_lower or 'gate' in name_lower):
        return "voltage"
    elif 'i' in name_lower or 'current' in name_lower:
        return "current"
    elif 'temp' in name_lower or 't' == name_lower[0]:
        return "temperature"
    else:
        return "general"

def infer_param_unit(param_name):
    """Infer parameter unit from name"""
    name_lower = param_name.lower()
    if 'v' in name_lower:
        return "V"
    elif 'i' in name_lower or 'current' in name_lower:
        return "A"
    elif 'temp' in name_lower:
        return "°C"
    else:
        return "dimensionless"

if __name__ == "__main__":
    precise_soa_analysis()