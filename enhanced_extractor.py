#!/usr/bin/env python3
"""
Enhanced extractor that handles both tmaxfrac and non-tmaxfrac parameter blocks
"""

import pandas as pd
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class ParameterRule:
    name: str
    severity: str
    constraints: Dict[str, Any]
    tmaxfrac_constraints: Optional[Dict[float, Any]] = None
    source_row: int = 0
    source_sheet: str = ""

@dataclass
class DeviceInfo:
    name: str
    type: str
    category: str
    subcategory: str
    description: str
    source_sheet: str

@dataclass
class DeviceRuleSet:
    device_info: DeviceInfo
    parameters: List[ParameterRule]
    tmaxfrac_levels: List[float]
    rule_count: int

class EnhancedExtractor:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.device_mapping = self._load_device_mapping()
        self.extracted_devices = {}
    
    def _load_device_mapping(self):
        """Load the simple device mapping"""
        mapping_file = "simple_device_mapping.json"
        if not Path(mapping_file).exists():
            raise FileNotFoundError(f"{mapping_file} not found. Run simple_device_mapper.py first.")
        
        with open(mapping_file, "r") as f:
            return json.load(f)
    
    def extract_all_parameters(self):
        """Extract both tmaxfrac and non-tmaxfrac parameters"""
        
        print("=== ENHANCED PARAMETER EXTRACTION ===")
        
        total_devices = 0
        total_parameters = 0
        
        for sheet_name, sheet_info in self.device_mapping["sheets"].items():
            print(f"\n{'='*60}")
            print(f"PROCESSING: {sheet_name}")
            print(f"{'='*60}")
            
            try:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
                
                for device_config in sheet_info["devices"]:
                    # Try tmaxfrac extraction first
                    device_rules = self._extract_device_from_tmaxfrac(df, device_config, sheet_name)
                    
                    # If no tmaxfrac, try general parameter extraction
                    if not device_rules:
                        device_rules = self._extract_device_general(df, device_config, sheet_name)
                    
                    if device_rules:
                        device_key = self._generate_device_key(device_config)
                        self.extracted_devices[device_key] = device_rules
                        
                        total_devices += 1
                        total_parameters += device_rules.rule_count
                        
                        print(f"  ✅ {device_config['name']}: {device_rules.rule_count} parameters")
                        if device_rules.tmaxfrac_levels:
                            print(f"     tmaxfrac levels: {device_rules.tmaxfrac_levels}")
                    else:
                        print(f"  ❌ {device_config['name']}: No parameters extracted")
                        
            except Exception as e:
                print(f"  ❌ Error processing sheet: {e}")
        
        print(f"\n🎯 EXTRACTION COMPLETE:")
        print(f"  Total devices: {total_devices}")
        print(f"  Total parameters: {total_parameters}")
        
        # Save results
        self._save_results()
        
        return self.extracted_devices
    
    def _extract_device_from_tmaxfrac(self, df, device_config, sheet_name):
        """Extract device using tmaxfrac section (same as improved extractor)"""
        
        tmaxfrac_row = device_config["tmaxfrac_row"]
        
        # Validate tmaxfrac row exists
        if tmaxfrac_row >= df.shape[0]:
            return None
        
        # Extract tmaxfrac values
        tmaxfrac_levels = self._extract_tmaxfrac_values(df, tmaxfrac_row)
        if not tmaxfrac_levels:
            return None
        
        # Extract parameters
        parameters = self._extract_parameters_from_tmaxfrac_section(df, tmaxfrac_row, tmaxfrac_levels, sheet_name)
        if not parameters:
            return None
        
        # Create device info
        device_info = DeviceInfo(
            name=device_config["name"],
            type=device_config["type"],
            category=device_config["category"],
            subcategory=device_config["subcategory"],
            description=device_config["description"],
            source_sheet=sheet_name
        )
        
        return DeviceRuleSet(
            device_info=device_info,
            parameters=parameters,
            tmaxfrac_levels=tmaxfrac_levels,
            rule_count=len(parameters)
        )
    
    def _extract_device_general(self, df, device_config, sheet_name):
        """Extract device using general parameter patterns (non-tmaxfrac)"""
        
        # Look for parameter blocks around the device area
        start_row = max(0, device_config["tmaxfrac_row"] - 10)
        end_row = min(df.shape[0], device_config["tmaxfrac_row"] + 50)
        
        parameters = []
        
        for row_idx in range(start_row, end_row):
            if row_idx >= df.shape[0]:
                break
            
            row_data = df.iloc[row_idx]
            
            # Get severity and parameter name
            severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
            param_name = str(row_data.iloc[1]) if len(row_data) > 1 and pd.notna(row_data.iloc[1]) else ""
            
            # Validate parameter row
            if not self._is_valid_parameter_row(severity, param_name):
                continue
            
            # Extract general constraints (vlow, vhigh, etc.)
            constraints = {}
            for col_idx in range(2, min(df.shape[1], 8)):  # Check columns 2-7
                if pd.notna(row_data.iloc[col_idx]):
                    value = row_data.iloc[col_idx]
                    col_name = f"col_{col_idx}"
                    
                    # Try to identify column meaning from headers
                    if col_idx == 3:
                        col_name = "vlow"
                    elif col_idx == 4:
                        col_name = "vhigh"
                    
                    if isinstance(value, (int, float)):
                        constraints[col_name] = float(value)
                    else:
                        constraints[col_name] = str(value)
            
            if constraints:
                param = ParameterRule(
                    name=param_name,
                    severity=severity,
                    constraints=constraints,
                    source_row=row_idx,
                    source_sheet=sheet_name
                )
                parameters.append(param)
        
        if not parameters:
            return None
        
        # Create device info
        device_info = DeviceInfo(
            name=device_config["name"],
            type=device_config["type"],
            category=device_config["category"],
            subcategory=device_config["subcategory"],
            description=device_config["description"],
            source_sheet=sheet_name
        )
        
        return DeviceRuleSet(
            device_info=device_info,
            parameters=parameters,
            tmaxfrac_levels=[],
            rule_count=len(parameters)
        )
    
    def _extract_tmaxfrac_values(self, df, tmaxfrac_row):
        """Extract tmaxfrac values from the row after tmaxfrac label"""
        
        # Find tmaxfrac column
        tmaxfrac_col = None
        for col_idx in range(df.shape[1]):
            if pd.notna(df.iloc[tmaxfrac_row, col_idx]):
                cell_value = str(df.iloc[tmaxfrac_row, col_idx]).lower()
                if 'tmaxfrac' in cell_value:
                    tmaxfrac_col = col_idx
                    break
        
        if tmaxfrac_col is None:
            return []
        
        # Get values from next few rows (pattern varies)
        tmaxfrac_levels = []
        for offset in range(1, 4):  # Check next 3 rows
            if tmaxfrac_row + offset >= df.shape[0]:
                break
                
            values_row = df.iloc[tmaxfrac_row + offset]
            found_values = []
            
            for col_idx in range(tmaxfrac_col, min(tmaxfrac_col + 10, df.shape[1])):
                if pd.notna(values_row.iloc[col_idx]):
                    try:
                        val = float(values_row.iloc[col_idx])
                        found_values.append(val)
                    except:
                        # If we hit non-numeric, stop looking in this row
                        break
            
            if found_values:
                tmaxfrac_levels = found_values
                break
        
        return tmaxfrac_levels
    
    def _extract_parameters_from_tmaxfrac_section(self, df, tmaxfrac_row, tmaxfrac_levels, sheet_name):
        """Extract parameters from tmaxfrac section"""
        
        parameters = []
        
        # Find tmaxfrac column
        tmaxfrac_col = None
        for col_idx in range(df.shape[1]):
            if pd.notna(df.iloc[tmaxfrac_row, col_idx]):
                cell_value = str(df.iloc[tmaxfrac_row, col_idx]).lower()
                if 'tmaxfrac' in cell_value:
                    tmaxfrac_col = col_idx
                    break
        
        if tmaxfrac_col is None:
            return parameters
        
        # Extract parameters starting after header row
        start_row = tmaxfrac_row + 2
        
        for row_idx in range(start_row, min(start_row + 100, df.shape[0])):
            if row_idx >= df.shape[0]:
                break
            
            row_data = df.iloc[row_idx]
            
            # Get severity and parameter name
            severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
            param_name = str(row_data.iloc[1]) if len(row_data) > 1 and pd.notna(row_data.iloc[1]) else ""
            
            # Validate parameter row
            if not self._is_valid_parameter_row(severity, param_name):
                continue
            
            # Extract tmaxfrac values for this parameter
            # Values start from column where tmaxfrac levels were found
            tmaxfrac_constraints = {}
            
            # Find where the tmaxfrac values start (usually column 3 or 4)
            value_start_col = 3  # Most common pattern
            for i, level in enumerate(tmaxfrac_levels):
                col_idx = value_start_col + i
                if col_idx < df.shape[1] and pd.notna(row_data.iloc[col_idx]):
                    value = row_data.iloc[col_idx]
                    if isinstance(value, (int, float)):
                        tmaxfrac_constraints[level] = float(value)
                    else:
                        tmaxfrac_constraints[level] = str(value)
            
            # Extract general constraints too
            constraints = {}
            for col_idx in range(2, min(df.shape[1], 8)):
                if pd.notna(row_data.iloc[col_idx]):
                    value = row_data.iloc[col_idx]
                    col_name = f"col_{col_idx}"
                    
                    if isinstance(value, (int, float)):
                        constraints[col_name] = float(value)
                    else:
                        constraints[col_name] = str(value)
            
            if tmaxfrac_constraints or constraints:
                param = ParameterRule(
                    name=param_name,
                    severity=severity,
                    constraints=constraints,
                    tmaxfrac_constraints=tmaxfrac_constraints,
                    source_row=row_idx,
                    source_sheet=sheet_name
                )
                parameters.append(param)
        
        return parameters
    
    def _is_valid_parameter_row(self, severity, param_name):
        """Check if this is a valid parameter row"""
        
        # Skip empty or invalid rows
        if param_name in ['nan', 'parameter', '', 'NaN', 'parameter ']:
            return False
        
        if len(param_name) < 2 or len(param_name) > 100:
            return False
        
        if len(severity) > 20:
            return False
        
        return True
    
    def _generate_device_key(self, device_config):
        """Generate a unique key for the device"""
        return f"{device_config['category']}_{device_config['subcategory']}_{device_config['name']}".replace(" ", "_")
    
    def _save_results(self):
        """Save extraction results"""
        
        # Convert to serializable format
        results = {}
        for device_key, device_rules in self.extracted_devices.items():
            results[device_key] = {
                "device_info": asdict(device_rules.device_info),
                "parameters": [asdict(param) for param in device_rules.parameters],
                "tmaxfrac_levels": device_rules.tmaxfrac_levels,
                "rule_count": device_rules.rule_count
            }
        
        # Save JSON
        with open("enhanced_device_grouped_rules.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Save summary
        with open("enhanced_extraction_summary.txt", "w") as f:
            f.write("🎯 ENHANCED EXTRACTION SUMMARY:\n")
            f.write(f"   Method: tmaxfrac + general parameter blocks\n")
            f.write(f"   Total devices: {len(self.extracted_devices)}\n")
            f.write(f"   Total parameters: {sum(d.rule_count for d in self.extracted_devices.values())}\n")
            f.write(f"   Coverage: Both tmaxfrac rules and general parameter constraints\n\n")
            
            for device_key, device_rules in self.extracted_devices.items():
                f.write(f"📋 {device_rules.device_info.name}:\n")
                f.write(f"   Parameters: {device_rules.rule_count}\n")
                f.write(f"   tmaxfrac levels: {device_rules.tmaxfrac_levels}\n")
                f.write(f"   Sheet: {device_rules.device_info.source_sheet}\n\n")
        
        print(f"✅ Enhanced extraction saved to ./")
        print(f"   - enhanced_device_grouped_rules.json")
        print(f"   - enhanced_extraction_summary.txt")

def main():
    """Main extraction function"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ Excel file not found: {excel_file}")
        return
    
    extractor = EnhancedExtractor(excel_file)
    results = extractor.extract_all_parameters()
    
    total_params = sum(d.rule_count for d in results.values())
    print(f"\n🎯 ENHANCED EXTRACTION SUMMARY:")
    print(f"   Method: tmaxfrac + general parameter blocks")
    print(f"   Total devices: {len(results)}")
    print(f"   Total parameters: {total_params}")
    print(f"   Coverage: Both tmaxfrac rules and general parameter constraints")

if __name__ == "__main__":
    main()