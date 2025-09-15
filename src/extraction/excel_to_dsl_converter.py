#!/usr/bin/env python3
"""
Excel to SOA DSL Converter - Converts the SMOS10HV Excel file to unified DSL format
"""

import pandas as pd
import json
import yaml
from pathlib import Path
from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType

class ExcelToSOAConverter:
    """Converts Excel SOA rules to unified DSL format"""
    
    def __init__(self, excel_file: str):
        self.excel_file = excel_file
        self.soa_engine = SOARulesEngine()
        self.conversion_log = []
    
    def convert_all_sheets(self) -> SOARulesEngine:
        """Convert all SOA sheets from Excel to DSL format"""
        
        print("=== EXCEL TO SOA DSL CONVERSION ===")
        
        # Get all sheet names
        xl_file = pd.ExcelFile(self.excel_file)
        soa_sheets = [name for name in xl_file.sheet_names if 'SOA' in name]
        
        print(f"Found {len(soa_sheets)} SOA sheets to convert:")
        for sheet in soa_sheets:
            print(f"  - {sheet}")
        
        # Convert each sheet
        for sheet_name in soa_sheets:
            try:
                self._convert_sheet(sheet_name)
                self.conversion_log.append(f"✅ Successfully converted: {sheet_name}")
            except Exception as e:
                self.conversion_log.append(f"❌ Failed to convert {sheet_name}: {str(e)}")
                print(f"Error converting {sheet_name}: {e}")
        
        return self.soa_engine
    
    def _convert_sheet(self, sheet_name: str):
        """Convert a single sheet to DSL format"""
        
        print(f"\nConverting sheet: {sheet_name}")
        
        # Read raw data
        df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
        
        # Find tmaxfrac structure
        tmaxfrac_info = self._extract_tmaxfrac_structure(df)
        
        if not tmaxfrac_info:
            print(f"  No valid tmaxfrac structure found in {sheet_name}")
            return
        
        # Extract device information
        device_info = self._extract_device_info(sheet_name, df)
        
        # Create device rules
        device_rules = self._create_device_rules(tmaxfrac_info, device_info)
        
        # Add to SOA engine
        device_key = f"{device_info['device_type']}_{device_info['subcategory']}"
        self.soa_engine.add_device(device_key, device_rules)
        
        print(f"  ✅ Converted {len(device_rules.parameters)} parameters")
    
    def _extract_tmaxfrac_structure(self, df) -> dict:
        """Extract tmaxfrac values and parameter structure"""
        
        # Find tmaxfrac row
        tmaxfrac_row = None
        tmaxfrac_col = None
        
        for row_idx in range(min(20, df.shape[0])):
            for col_idx in range(df.shape[1]):
                cell_value = str(df.iloc[row_idx, col_idx]).lower()
                if 'tmaxfrac' in cell_value:
                    tmaxfrac_row = row_idx
                    tmaxfrac_col = col_idx
                    break
            if tmaxfrac_row is not None:
                break
        
        if tmaxfrac_row is None:
            return None
        
        # Get tmaxfrac values
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
        
        # Extract parameters
        parameters = []
        start_row = tmaxfrac_row + 2
        
        for row_idx in range(start_row, min(start_row + 100, df.shape[0])):
            row_data = df.iloc[row_idx]
            
            # Get severity and parameter name
            severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
            param_name = str(row_data.iloc[1]) if pd.notna(row_data.iloc[1]) else ""
            
            # Skip invalid rows
            if param_name in ['nan', 'parameter', ''] or len(param_name) < 3:
                continue
            
            # Get values for each tmaxfrac level
            param_values = {}
            for i, tmaxfrac_val in enumerate(tmaxfrac_values):
                col_idx = tmaxfrac_col + i
                if col_idx < df.shape[1] and pd.notna(row_data.iloc[col_idx]):
                    value = row_data.iloc[col_idx]
                    # Handle numeric and string values
                    if isinstance(value, (int, float)):
                        param_values[tmaxfrac_val] = float(value)
                    else:
                        param_values[tmaxfrac_val] = str(value)
            
            if param_values:
                parameters.append({
                    'name': param_name,
                    'severity': severity.lower() if severity.lower() in ['high', 'medium', 'low'] else 'high',
                    'values': param_values
                })
        
        return {
            'tmaxfrac_values': tmaxfrac_values,
            'parameters': parameters
        }
    
    def _extract_device_info(self, sheet_name: str, df) -> dict:
        """Extract device type and category information"""
        
        device_info = {
            'technology': 'smos10hv',
            'device_type': 'unknown',
            'subcategory': 'general',
            'sheet_name': sheet_name
        }
        
        # Parse device type from sheet name
        if 'SYM ON-OFF' in sheet_name:
            device_info.update({
                'device_type': 'mos_transistor',
                'subcategory': 'symmetric_on_off'
            })
        elif 'CAPS' in sheet_name:
            device_info.update({
                'device_type': 'capacitor',
                'subcategory': 'general'
            })
        elif 'SUB Well' in sheet_name and 'HV' in sheet_name:
            device_info.update({
                'device_type': 'substrate',
                'subcategory': 'well_hv'
            })
        elif 'SUB Well' in sheet_name:
            device_info.update({
                'device_type': 'substrate',
                'subcategory': 'well_isolation'
            })
        elif 'OXRisk' in sheet_name:
            device_info.update({
                'device_type': 'oxide',
                'subcategory': 'reliability_drift'
            })
        
        # Look for additional device information in the sheet
        for row_idx in range(min(10, df.shape[0])):
            for col_idx in range(df.shape[1]):
                cell_value = str(df.iloc[row_idx, col_idx]).lower()
                if 'nmos' in cell_value or 'pmos' in cell_value:
                    if device_info['device_type'] == 'unknown':
                        device_info['device_type'] = 'mos_transistor'
                elif 'capacitor' in cell_value:
                    if device_info['device_type'] == 'unknown':
                        device_info['device_type'] = 'capacitor'
        
        return device_info
    
    def _create_device_rules(self, tmaxfrac_info: dict, device_info: dict) -> DeviceRules:
        """Create DeviceRules object from extracted information"""
        
        parameters = {}
        
        for param_data in tmaxfrac_info['parameters']:
            param_name = param_data['name']
            
            # Determine parameter type and unit
            param_type = self._infer_parameter_type(param_name)
            unit = self._infer_parameter_unit(param_name)
            
            # Create SOAParameter
            soa_param = SOAParameter(
                name=param_name,
                severity=Severity(param_data['severity']),
                param_type=param_type,
                unit=unit,
                values=param_data['values'],
                description=f"{param_data['severity']} severity limit for {param_name}"
            )
            
            parameters[param_name] = soa_param
        
        return DeviceRules(
            device_type=device_info['device_type'],
            subcategory=device_info['subcategory'],
            tmaxfrac_levels=tmaxfrac_info['tmaxfrac_values'],
            parameters=parameters,
            metadata={
                'source_sheet': device_info['sheet_name'],
                'technology': device_info['technology']
            }
        )
    
    def _infer_parameter_type(self, param_name: str) -> ParameterType:
        """Infer parameter type from name"""
        name_lower = param_name.lower()
        
        if 'v' in name_lower and ('high' in name_lower or 'low' in name_lower or 'gate' in name_lower):
            return ParameterType.VOLTAGE
        elif 'i' in name_lower or 'current' in name_lower:
            return ParameterType.CURRENT
        elif 'temp' in name_lower or name_lower.startswith('t'):
            return ParameterType.TEMPERATURE
        else:
            return ParameterType.GENERAL
    
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
    
    def save_to_files(self, output_dir: str = "."):
        """Save converted rules to various formats"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Export to JSON
        json_data = self.soa_engine.export_to_json()
        with open(output_path / "soa_rules.json", "w") as f:
            json.dump(json_data, f, indent=2)
        
        # Export to YAML
        with open(output_path / "soa_rules.yaml", "w") as f:
            yaml.dump(json_data, f, default_flow_style=False, indent=2)
        
        # Create Python module
        self._create_python_module(output_path / "soa_rules.py")
        
        # Save conversion log
        with open(output_path / "conversion_log.txt", "w") as f:
            f.write("SOA Rules Conversion Log\n")
            f.write("=" * 30 + "\n\n")
            for entry in self.conversion_log:
                f.write(f"{entry}\n")
        
        print(f"\n✅ Saved converted rules to {output_path}/")
        print(f"   - soa_rules.json")
        print(f"   - soa_rules.yaml") 
        print(f"   - soa_rules.py")
        print(f"   - conversion_log.txt")
    
    def _create_python_module(self, output_file: Path):
        """Create a Python module with the converted rules"""
        
        python_code = '''"""
Auto-generated SOA Rules Module
Converted from SMOS10HV Excel file
"""

from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType

def load_soa_rules() -> SOARulesEngine:
    """Load all SOA rules into the engine"""
    
    soa = SOARulesEngine()
    
'''
        
        # Add each device
        for device_key, device_rules in self.soa_engine.devices.items():
            python_code += f'''
    # {device_key} rules
    {device_key}_params = {{'''
            
            for param_name, param in device_rules.parameters.items():
                safe_param_name = param_name.replace('-', '_').replace(' ', '_')
                python_code += f'''
        "{param_name}": SOAParameter(
            name="{param.name}",
            severity=Severity.{param.severity.name},
            param_type=ParameterType.{param.param_type.name},
            unit="{param.unit}",
            values={dict(param.values)},
            description="{param.description}"
        ),'''
            
            python_code += f'''
    }}
    
    {device_key}_rules = DeviceRules(
        device_type="{device_rules.device_type}",
        subcategory="{device_rules.subcategory}",
        tmaxfrac_levels={device_rules.tmaxfrac_levels},
        parameters={device_key}_params,
        metadata={device_rules.metadata}
    )
    
    soa.add_device("{device_key}", {device_key}_rules)
'''
        
        python_code += '''
    return soa

# Example usage
if __name__ == "__main__":
    soa_engine = load_soa_rules()
    print(f"Loaded {len(soa_engine.devices)} device types")
    
    # Example validation
    for device_key in soa_engine.devices.keys():
        print(f"\\nDevice: {device_key}")
        device = soa_engine.devices[device_key]
        print(f"  Parameters: {list(device.parameters.keys())}")
        print(f"  tmaxfrac levels: {device.tmaxfrac_levels}")
'''
        
        with open(output_file, "w") as f:
            f.write(python_code)

def main():
    """Main conversion function"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    # Create converter
    converter = ExcelToSOAConverter(excel_file)
    
    # Convert all sheets
    soa_engine = converter.convert_all_sheets()
    
    # Print summary
    print(f"\n=== CONVERSION SUMMARY ===")
    print(f"Converted {len(soa_engine.devices)} device types:")
    
    for device_key, device_rules in soa_engine.devices.items():
        print(f"  {device_key}:")
        print(f"    - Type: {device_rules.device_type}")
        print(f"    - Subcategory: {device_rules.subcategory}")
        print(f"    - Parameters: {len(device_rules.parameters)}")
        print(f"    - tmaxfrac levels: {device_rules.tmaxfrac_levels}")
    
    # Save to files
    converter.save_to_files()
    
    print(f"\n=== CONVERSION LOG ===")
    for entry in converter.conversion_log:
        print(entry)

if __name__ == "__main__":
    main()