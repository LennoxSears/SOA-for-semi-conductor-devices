#!/usr/bin/env python3
"""
Device-Grouped SOA Rule Extractor
Extracts rules organized by device types as they appear in Excel sheets
"""

import pandas as pd
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Union, Optional, Any
from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType

@dataclass
class DeviceInfo:
    """Device information extracted from Excel"""
    name: str
    type: str
    category: str
    subcategory: str
    description: str
    source_sheet: str
    technology: str = "smos10hv"

@dataclass
class ParameterRule:
    """Individual parameter rule"""
    name: str
    severity: str
    parameter_type: str
    unit: str
    description: str
    tmaxfrac_constraints: Dict[float, Union[float, str]]
    conditions: List[str]
    notes: str = ""

@dataclass
class DeviceRuleSet:
    """Complete rule set for a device"""
    device_info: DeviceInfo
    parameters: List[ParameterRule]
    tmaxfrac_levels: List[float]
    rule_count: int
    extraction_notes: str = ""

class DeviceGroupedExtractor:
    """Extract SOA rules grouped by device types"""
    
    def __init__(self, excel_file: str):
        self.excel_file = excel_file
        self.device_rules = {}
        self.extraction_log = []
        
    def extract_all_devices(self) -> Dict[str, DeviceRuleSet]:
        """Extract all devices with their complete rule sets"""
        
        print("=== DEVICE-GROUPED SOA EXTRACTION ===")
        
        xl_file = pd.ExcelFile(self.excel_file)
        
        # Process each sheet and identify devices
        for sheet_name in xl_file.sheet_names:
            print(f"\n{'='*60}")
            print(f"PROCESSING SHEET: {sheet_name}")
            print(f"{'='*60}")
            
            try:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
                devices = self._extract_devices_from_sheet(df, sheet_name)
                
                for device_key, device_rules in devices.items():
                    if device_key in self.device_rules:
                        # Merge with existing device
                        self._merge_device_rules(device_key, device_rules)
                    else:
                        self.device_rules[device_key] = device_rules
                        
                    print(f"  Device: {device_key}")
                    print(f"    Parameters: {len(device_rules.parameters)}")
                    print(f"    tmaxfrac levels: {device_rules.tmaxfrac_levels}")
                    
            except Exception as e:
                print(f"Error processing {sheet_name}: {e}")
                self.extraction_log.append(f"❌ {sheet_name}: {str(e)}")
        
        print(f"\n🎯 EXTRACTED {len(self.device_rules)} DEVICE TYPES")
        return self.device_rules
    
    def _extract_devices_from_sheet(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, DeviceRuleSet]:
        """Extract device information and rules from a single sheet"""
        
        devices = {}
        
        # Look for device sections in the sheet
        device_sections = self._identify_device_sections(df, sheet_name)
        
        for section in device_sections:
            device_info = section['device_info']
            device_key = self._generate_device_key(device_info)
            
            # Extract parameters for this device
            parameters = self._extract_device_parameters(df, section)
            
            if parameters:
                device_rules = DeviceRuleSet(
                    device_info=device_info,
                    parameters=parameters,
                    tmaxfrac_levels=section.get('tmaxfrac_levels', []),
                    rule_count=len(parameters),
                    extraction_notes=f"Extracted from {sheet_name}"
                )
                
                devices[device_key] = device_rules
        
        return devices
    
    def _identify_device_sections(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Identify different device sections within a sheet"""
        
        sections = []
        
        # Look for device identifiers and tmaxfrac sections
        for row_idx in range(min(50, df.shape[0])):
            for col_idx in range(df.shape[1]):
                cell_value = str(df.iloc[row_idx, col_idx])
                
                # Check for device type indicators
                device_info = self._parse_device_info(cell_value, sheet_name, row_idx)
                if device_info:
                    # Look for associated tmaxfrac
                    tmaxfrac_info = self._find_nearby_tmaxfrac(df, row_idx, col_idx)
                    
                    section = {
                        'device_info': device_info,
                        'start_row': row_idx,
                        'tmaxfrac_levels': tmaxfrac_info.get('levels', []),
                        'tmaxfrac_row': tmaxfrac_info.get('row', None),
                        'tmaxfrac_col': tmaxfrac_info.get('col', None)
                    }
                    sections.append(section)
        
        # If no specific device sections found, create one for the whole sheet
        if not sections:
            device_info = self._create_default_device_info(sheet_name)
            tmaxfrac_info = self._find_any_tmaxfrac(df)
            
            sections.append({
                'device_info': device_info,
                'start_row': 0,
                'tmaxfrac_levels': tmaxfrac_info.get('levels', []),
                'tmaxfrac_row': tmaxfrac_info.get('row', None),
                'tmaxfrac_col': tmaxfrac_info.get('col', None)
            })
        
        return sections
    
    def _parse_device_info(self, cell_value: str, sheet_name: str, row_idx: int) -> Optional[DeviceInfo]:
        """Parse device information from cell content"""
        
        cell_lower = cell_value.lower()
        
        # Look for specific device type patterns
        device_patterns = {
            'core nmos': ('NMOS Core', 'mos_transistor', 'core', 'nmos'),
            'core pmos': ('PMOS Core', 'mos_transistor', 'core', 'pmos'),
            'nmos5': ('NMOS 5V', 'mos_transistor', '5v', 'nmos'),
            'pmos5': ('PMOS 5V', 'mos_transistor', '5v', 'pmos'),
            'nmos_ll': ('NMOS Low Leakage', 'mos_transistor', 'low_leakage', 'nmos'),
            'pmos_ll': ('PMOS Low Leakage', 'mos_transistor', 'low_leakage', 'pmos'),
            'nmos_ull': ('NMOS Ultra Low Leakage', 'mos_transistor', 'ultra_low_leakage', 'nmos'),
            'pmos_ull': ('PMOS Ultra Low Leakage', 'mos_transistor', 'ultra_low_leakage', 'pmos'),
            'cglv': ('CGLV Capacitor', 'capacitor', 'gate', 'low_voltage'),
            'cghv': ('CGHV Capacitor', 'capacitor', 'gate', 'high_voltage'),
            'cghvf': ('CGHVF Capacitor', 'capacitor', 'gate', 'high_voltage_fast'),
            'cdp': ('CDP Capacitor', 'capacitor', 'diffusion', 'poly'),
            'cfr': ('CFR Capacitor', 'capacitor', 'fringe', 'general'),
        }
        
        for pattern, (name, dev_type, category, subcategory) in device_patterns.items():
            if pattern in cell_lower:
                return DeviceInfo(
                    name=name,
                    type=dev_type,
                    category=category,
                    subcategory=subcategory,
                    description=cell_value.strip(),
                    source_sheet=sheet_name
                )
        
        return None
    
    def _create_default_device_info(self, sheet_name: str) -> DeviceInfo:
        """Create default device info based on sheet name"""
        
        sheet_lower = sheet_name.lower()
        
        if 'mos' in sheet_lower and 'sym' in sheet_lower:
            return DeviceInfo(
                name="MOS Symmetric",
                type="mos_transistor", 
                category="symmetric",
                subcategory="on_off",
                description="MOS transistors with symmetric on/off characteristics",
                source_sheet=sheet_name
            )
        elif 'caps' in sheet_lower:
            return DeviceInfo(
                name="Capacitors",
                type="capacitor",
                category="general",
                subcategory="all_types",
                description="Various capacitor types",
                source_sheet=sheet_name
            )
        elif 'sub' in sheet_lower and 'well' in sheet_lower:
            return DeviceInfo(
                name="Substrate Well",
                type="substrate",
                category="well",
                subcategory="isolation",
                description="Substrate and well isolation structures",
                source_sheet=sheet_name
            )
        elif 'diode' in sheet_lower:
            return DeviceInfo(
                name="Diodes",
                type="diode",
                category="general",
                subcategory="forward_reverse",
                description="Diode structures",
                source_sheet=sheet_name
            )
        elif 'bjt' in sheet_lower:
            return DeviceInfo(
                name="BJT",
                type="bjt",
                category="bipolar",
                subcategory="general",
                description="Bipolar junction transistors",
                source_sheet=sheet_name
            )
        elif 'resistor' in sheet_lower:
            return DeviceInfo(
                name="Resistors",
                type="resistor",
                category="general",
                subcategory="all_types",
                description="Resistor structures",
                source_sheet=sheet_name
            )
        else:
            return DeviceInfo(
                name=sheet_name.replace('10HV ', '').replace('SOA ', ''),
                type="unknown",
                category="general",
                subcategory="unknown",
                description=f"Device from {sheet_name}",
                source_sheet=sheet_name
            )
    
    def _find_nearby_tmaxfrac(self, df: pd.DataFrame, start_row: int, start_col: int) -> Dict:
        """Find tmaxfrac information near a device identifier"""
        
        # Search in nearby rows
        search_range = 10
        for row_offset in range(-2, search_range):
            row_idx = start_row + row_offset
            if 0 <= row_idx < df.shape[0]:
                tmaxfrac_info = self._extract_tmaxfrac_from_row(df, row_idx)
                if tmaxfrac_info:
                    return tmaxfrac_info
        
        return {}
    
    def _find_any_tmaxfrac(self, df: pd.DataFrame) -> Dict:
        """Find any tmaxfrac in the sheet"""
        
        for row_idx in range(min(30, df.shape[0])):
            tmaxfrac_info = self._extract_tmaxfrac_from_row(df, row_idx)
            if tmaxfrac_info:
                return tmaxfrac_info
        
        return {}
    
    def _extract_tmaxfrac_from_row(self, df: pd.DataFrame, row_idx: int) -> Optional[Dict]:
        """Extract tmaxfrac information from a specific row"""
        
        for col_idx in range(df.shape[1]):
            cell_value = str(df.iloc[row_idx, col_idx]).lower()
            if 'tmaxfrac' in cell_value:
                # Get tmaxfrac values from next row
                levels = []
                if row_idx + 1 < df.shape[0]:
                    values_row = df.iloc[row_idx + 1]
                    for c in range(col_idx, min(col_idx + 10, df.shape[1])):
                        if pd.notna(values_row.iloc[c]):
                            try:
                                val = float(values_row.iloc[c])
                                levels.append(val)
                            except:
                                pass
                
                return {
                    'levels': levels,
                    'row': row_idx,
                    'col': col_idx
                }
        
        return None
    
    def _extract_device_parameters(self, df: pd.DataFrame, section: Dict) -> List[ParameterRule]:
        """Extract parameters for a specific device section"""
        
        parameters = []
        
        if section.get('tmaxfrac_row') is not None:
            # Extract from tmaxfrac section
            parameters.extend(self._extract_tmaxfrac_parameters(df, section))
        
        # Extract other parameters in the section
        parameters.extend(self._extract_other_parameters(df, section))
        
        return parameters
    
    def _extract_tmaxfrac_parameters(self, df: pd.DataFrame, section: Dict) -> List[ParameterRule]:
        """Extract parameters from tmaxfrac section"""
        
        parameters = []
        tmaxfrac_row = section['tmaxfrac_row']
        tmaxfrac_col = section['tmaxfrac_col']
        tmaxfrac_levels = section['tmaxfrac_levels']
        
        if not tmaxfrac_levels:
            return parameters
        
        # Look for parameters starting after tmaxfrac
        start_row = tmaxfrac_row + 2
        for row_idx in range(start_row, min(start_row + 100, df.shape[0])):
            if row_idx >= df.shape[0]:
                break
            
            row_data = df.iloc[row_idx]
            
            # Get parameter info
            severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
            param_name = str(row_data.iloc[1]) if len(row_data) > 1 and pd.notna(row_data.iloc[1]) else ""
            
            # Skip invalid rows
            if not self._is_valid_parameter_name(param_name) or not self._is_valid_severity(severity):
                continue
            
            # Extract tmaxfrac values
            tmaxfrac_constraints = {}
            for i, level in enumerate(tmaxfrac_levels):
                col_idx = tmaxfrac_col + i
                if col_idx < df.shape[1] and pd.notna(row_data.iloc[col_idx]):
                    value = row_data.iloc[col_idx]
                    if isinstance(value, (int, float)):
                        tmaxfrac_constraints[level] = float(value)
                    else:
                        tmaxfrac_constraints[level] = str(value)
            
            if tmaxfrac_constraints:
                param_rule = ParameterRule(
                    name=param_name,
                    severity=severity.lower() if severity.lower() in ['high', 'medium', 'low'] else 'high',
                    parameter_type=self._infer_parameter_type(param_name),
                    unit=self._infer_parameter_unit(param_name),
                    description=f"{severity} severity limit for {param_name}",
                    tmaxfrac_constraints=tmaxfrac_constraints,
                    conditions=[],
                    notes=f"Extracted from tmaxfrac section at row {row_idx}"
                )
                parameters.append(param_rule)
        
        return parameters
    
    def _extract_other_parameters(self, df: pd.DataFrame, section: Dict) -> List[ParameterRule]:
        """Extract non-tmaxfrac parameters"""
        
        parameters = []
        # Implementation for other parameter patterns
        # This would look for voltage limits, current limits, etc.
        return parameters
    
    def _is_valid_parameter_name(self, param_name: str) -> bool:
        """Check if parameter name is valid"""
        if param_name in ['nan', 'parameter', '', 'NaN'] or len(param_name) < 2:
            return False
        if len(param_name) > 50:  # Too long, likely description
            return False
        return True
    
    def _is_valid_severity(self, severity: str) -> bool:
        """Check if severity is valid"""
        if len(severity) > 20:  # Too long, likely description
            return False
        return True
    
    def _infer_parameter_type(self, param_name: str) -> str:
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
    
    def _infer_parameter_unit(self, param_name: str) -> str:
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
    
    def _generate_device_key(self, device_info: DeviceInfo) -> str:
        """Generate unique device key"""
        return f"{device_info.type}_{device_info.category}_{device_info.subcategory}"
    
    def _merge_device_rules(self, device_key: str, new_rules: DeviceRuleSet):
        """Merge new rules with existing device rules"""
        existing = self.device_rules[device_key]
        
        # Merge parameters
        existing.parameters.extend(new_rules.parameters)
        existing.rule_count = len(existing.parameters)
        
        # Merge tmaxfrac levels
        for level in new_rules.tmaxfrac_levels:
            if level not in existing.tmaxfrac_levels:
                existing.tmaxfrac_levels.append(level)
        
        # Update notes
        existing.extraction_notes += f"; Merged from {new_rules.device_info.source_sheet}"
    
    def save_device_grouped_rules(self, output_dir: str = "."):
        """Save device-grouped rules to files"""
        
        output_path = Path(output_dir)
        
        # Create device-grouped JSON
        device_grouped_data = {
            "soa_device_rules": {
                "version": "2.0",
                "technology": "smos10hv",
                "description": "SOA rules organized by device types",
                "extraction_info": {
                    "total_devices": len(self.device_rules),
                    "total_parameters": sum(len(device.parameters) for device in self.device_rules.values()),
                    "extraction_date": "2025-09-15"
                },
                "devices": {}
            }
        }
        
        for device_key, device_rules in self.device_rules.items():
            device_data = {
                "device_info": asdict(device_rules.device_info),
                "rule_count": device_rules.rule_count,
                "tmaxfrac_levels": device_rules.tmaxfrac_levels,
                "parameters": {}
            }
            
            for param in device_rules.parameters:
                device_data["parameters"][param.name] = {
                    "severity": param.severity,
                    "type": param.parameter_type,
                    "unit": param.unit,
                    "description": param.description,
                    "tmaxfrac_constraints": param.tmaxfrac_constraints,
                    "conditions": param.conditions,
                    "notes": param.notes
                }
            
            device_grouped_data["soa_device_rules"]["devices"][device_key] = device_data
        
        # Save to JSON
        with open(output_path / "device_grouped_soa_rules.json", "w") as f:
            json.dump(device_grouped_data, f, indent=2)
        
        # Create device summary
        with open(output_path / "device_summary.txt", "w") as f:
            f.write("Device-Grouped SOA Rules Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total devices: {len(self.device_rules)}\n")
            f.write(f"Total parameters: {sum(len(device.parameters) for device in self.device_rules.values())}\n\n")
            
            for device_key, device_rules in self.device_rules.items():
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
                    f.write(f"  Parameter examples:\n")
                    for param in device_rules.parameters[:3]:  # Show first 3
                        f.write(f"    - {param.name} ({param.parameter_type}, {param.unit})\n")
                    if len(device_rules.parameters) > 3:
                        f.write(f"    ... and {len(device_rules.parameters) - 3} more\n")
        
        print(f"\n✅ Device-grouped rules saved to {output_path}/")
        print(f"   - device_grouped_soa_rules.json")
        print(f"   - device_summary.txt")
        
        return len(self.device_rules), sum(len(device.parameters) for device in self.device_rules.values())

def main():
    """Main extraction function"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ Excel file not found: {excel_file}")
        print("Please ensure the Excel file is in the current directory.")
        return
    
    # Create extractor
    extractor = DeviceGroupedExtractor(excel_file)
    
    # Extract all devices
    device_rules = extractor.extract_all_devices()
    
    # Save results
    total_devices, total_params = extractor.save_device_grouped_rules()
    
    print(f"\n🎯 DEVICE-GROUPED EXTRACTION COMPLETE:")
    print(f"   Total devices: {total_devices}")
    print(f"   Total parameters: {total_params}")
    
    # Show device breakdown
    print(f"\n📋 DEVICE BREAKDOWN:")
    for device_key, device_rules in device_rules.items():
        print(f"  {device_key}: {device_rules.rule_count} parameters")
        print(f"    {device_rules.device_info.name} ({device_rules.device_info.source_sheet})")
    
    return device_rules

if __name__ == "__main__":
    main()