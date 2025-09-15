#!/usr/bin/env python3
"""
Improved tmaxfrac extractor - Focus only on tmaxfrac sections using the device mapping
"""

import pandas as pd
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Union

@dataclass
class DeviceInfo:
    """Device information"""
    name: str
    type: str
    category: str
    subcategory: str
    description: str
    source_sheet: str
    technology: str = "smos10hv"

@dataclass
class ParameterRule:
    """Parameter rule with tmaxfrac constraints"""
    name: str
    severity: str
    parameter_type: str
    unit: str
    description: str
    tmaxfrac_constraints: Dict[float, Union[float, str]]
    source_row: int

@dataclass
class DeviceRuleSet:
    """Complete rule set for a device"""
    device_info: DeviceInfo
    parameters: List[ParameterRule]
    tmaxfrac_levels: List[float]
    rule_count: int

class ImprovedTmaxfracExtractor:
    """Extract all tmaxfrac sections using the device mapping"""
    
    def __init__(self, excel_file: str):
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
    
    def extract_all_tmaxfrac_devices(self):
        """Extract all devices using tmaxfrac sections"""
        
        print("=== IMPROVED TMAXFRAC EXTRACTION ===")
        
        total_devices = 0
        total_parameters = 0
        
        for sheet_name, sheet_info in self.device_mapping["sheets"].items():
            print(f"\n{'='*60}")
            print(f"PROCESSING: {sheet_name}")
            print(f"{'='*60}")
            
            try:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
                
                for device_config in sheet_info["devices"]:
                    device_rules = self._extract_device_from_tmaxfrac(df, device_config, sheet_name)
                    
                    if device_rules:
                        device_key = self._generate_device_key(device_config)
                        self.extracted_devices[device_key] = device_rules
                        
                        total_devices += 1
                        total_parameters += device_rules.rule_count
                        
                        print(f"  ✅ {device_config['name']}: {device_rules.rule_count} parameters")
                        print(f"     tmaxfrac levels: {device_rules.tmaxfrac_levels}")
                    else:
                        print(f"  ❌ {device_config['name']}: No parameters extracted")
                        
            except Exception as e:
                print(f"  ❌ Error processing {sheet_name}: {e}")
        
        print(f"\n🎯 EXTRACTION COMPLETE:")
        print(f"  Total devices: {total_devices}")
        print(f"  Total parameters: {total_parameters}")
        
        return self.extracted_devices
    
    def _extract_device_from_tmaxfrac(self, df, device_config, sheet_name):
        """Extract a single device from its tmaxfrac section"""
        
        tmaxfrac_row = device_config["tmaxfrac_row"]
        
        # Validate tmaxfrac row exists
        if tmaxfrac_row >= df.shape[0]:
            print(f"    ⚠️ tmaxfrac row {tmaxfrac_row} out of bounds")
            return None
        
        # Extract tmaxfrac values
        tmaxfrac_levels = self._extract_tmaxfrac_values(df, tmaxfrac_row)
        if not tmaxfrac_levels:
            print(f"    ⚠️ No tmaxfrac values found at row {tmaxfrac_row}")
            return None
        
        # Extract parameters
        parameters = self._extract_parameters_from_section(df, tmaxfrac_row, tmaxfrac_levels)
        if not parameters:
            print(f"    ⚠️ No parameters found in tmaxfrac section")
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
    
    def _extract_parameters_from_section(self, df, tmaxfrac_row, tmaxfrac_levels):
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
            
            # Only add if we have tmaxfrac values
            if tmaxfrac_constraints:
                parameter = ParameterRule(
                    name=param_name,
                    severity=severity.lower() if severity.lower() in ['high', 'medium', 'low'] else 'high',
                    parameter_type=self._infer_parameter_type(param_name),
                    unit=self._infer_parameter_unit(param_name),
                    description=f"{severity} severity limit for {param_name}",
                    tmaxfrac_constraints=tmaxfrac_constraints,
                    source_row=row_idx
                )
                parameters.append(parameter)
        
        return parameters
    
    def _is_valid_parameter_row(self, severity, param_name):
        """Check if this is a valid parameter row"""
        
        # Skip empty or invalid parameter names
        if param_name in ['nan', 'parameter', '', 'NaN'] or len(param_name) < 2:
            return False
        
        # Skip very long parameter names (likely descriptions)
        if len(param_name) > 50:
            return False
        
        # Skip if severity is too long (likely description)
        if len(severity) > 20:
            return False
        
        return True
    
    def _infer_parameter_type(self, param_name):
        """Infer parameter type from name"""
        name_lower = param_name.lower()
        if 'v' in name_lower and ('high' in name_lower or 'low' in name_lower):
            return "voltage"
        elif 'i' in name_lower or 'current' in name_lower:
            return "current"
        elif 'temp' in name_lower:
            return "temperature"
        else:
            return "general"
    
    def _infer_parameter_unit(self, param_name):
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
    
    def _generate_device_key(self, device_config):
        """Generate device key"""
        return f"{device_config['type']}_{device_config['category']}_{device_config['subcategory']}"
    
    def save_extracted_devices(self, output_dir="."):
        """Save extracted devices to files"""
        
        output_path = Path(output_dir)
        
        # Create device-grouped JSON
        device_data = {
            "soa_device_rules": {
                "version": "2.1",
                "technology": "smos10hv",
                "description": "SOA rules extracted from tmaxfrac sections",
                "extraction_info": {
                    "method": "improved_tmaxfrac_extraction",
                    "total_devices": len(self.extracted_devices),
                    "total_parameters": sum(device.rule_count for device in self.extracted_devices.values()),
                    "source_mapping": "simple_device_mapping.json"
                },
                "devices": {}
            }
        }
        
        for device_key, device_rules in self.extracted_devices.items():
            device_data["soa_device_rules"]["devices"][device_key] = {
                "device_info": asdict(device_rules.device_info),
                "rule_count": device_rules.rule_count,
                "tmaxfrac_levels": device_rules.tmaxfrac_levels,
                "parameters": {}
            }
            
            for param in device_rules.parameters:
                device_data["soa_device_rules"]["devices"][device_key]["parameters"][param.name] = {
                    "severity": param.severity,
                    "type": param.parameter_type,
                    "unit": param.unit,
                    "description": param.description,
                    "tmaxfrac_constraints": param.tmaxfrac_constraints,
                    "source_row": param.source_row
                }
        
        # Save to JSON
        with open(output_path / "improved_device_grouped_rules.json", "w") as f:
            json.dump(device_data, f, indent=2)
        
        # Create summary
        with open(output_path / "improved_extraction_summary.txt", "w") as f:
            f.write("Improved Device-Grouped SOA Rules Summary\n")
            f.write("=" * 45 + "\n\n")
            f.write(f"Extraction method: tmaxfrac sections only\n")
            f.write(f"Total devices: {len(self.extracted_devices)}\n")
            f.write(f"Total parameters: {sum(device.rule_count for device in self.extracted_devices.values())}\n\n")
            
            for device_key, device_rules in self.extracted_devices.items():
                f.write(f"\n{device_key.upper()}:\n")
                f.write(f"  Name: {device_rules.device_info.name}\n")
                f.write(f"  Type: {device_rules.device_info.type}\n")
                f.write(f"  Category: {device_rules.device_info.category}\n")
                f.write(f"  Subcategory: {device_rules.device_info.subcategory}\n")
                f.write(f"  Parameters: {device_rules.rule_count}\n")
                f.write(f"  tmaxfrac levels: {device_rules.tmaxfrac_levels}\n")
                f.write(f"  Source: {device_rules.device_info.source_sheet}\n")
                f.write(f"  Description: {device_rules.device_info.description}\n")
                
                if device_rules.parameters:
                    f.write(f"  Sample parameters:\n")
                    for param in device_rules.parameters[:3]:  # Show first 3
                        f.write(f"    - {param.name} ({param.parameter_type}, {param.unit})\n")
                        f.write(f"      tmaxfrac constraints: {param.tmaxfrac_constraints}\n")
                    if len(device_rules.parameters) > 3:
                        f.write(f"    ... and {len(device_rules.parameters) - 3} more\n")
        
        total_devices = len(self.extracted_devices)
        total_params = sum(device.rule_count for device in self.extracted_devices.values())
        
        print(f"\n✅ Improved extraction saved to {output_path}/")
        print(f"   - improved_device_grouped_rules.json")
        print(f"   - improved_extraction_summary.txt")
        
        return total_devices, total_params

def main():
    """Main extraction function"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ Excel file not found: {excel_file}")
        return
    
    try:
        # Create extractor
        extractor = ImprovedTmaxfracExtractor(excel_file)
        
        # Extract all tmaxfrac devices
        extracted_devices = extractor.extract_all_tmaxfrac_devices()
        
        # Save results
        total_devices, total_params = extractor.save_extracted_devices()
        
        print(f"\n🎯 IMPROVED EXTRACTION SUMMARY:")
        print(f"   Method: tmaxfrac sections only")
        print(f"   Total devices: {total_devices}")
        print(f"   Total parameters: {total_params}")
        print(f"   Coverage: Focused on tmaxfrac rules with transient time constraints")
        
        return extracted_devices
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    main()