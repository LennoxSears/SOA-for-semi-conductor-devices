#!/usr/bin/env python3
"""
Complete rule extractor - Extract ALL rules from the Excel file
"""

import pandas as pd
import json
from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType

class CompleteSOAExtractor:
    """Extract all SOA rules from Excel file"""
    
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.soa_engine = SOARulesEngine()
        self.extraction_log = []
    
    def extract_all_rules(self):
        """Extract all rules from all sheets"""
        
        print("=== COMPLETE SOA RULE EXTRACTION ===")
        
        xl_file = pd.ExcelFile(self.excel_file)
        all_sheets = xl_file.sheet_names
        
        total_extracted = 0
        
        for sheet_name in all_sheets:
            print(f"\n{'='*60}")
            print(f"EXTRACTING: {sheet_name}")
            print(f"{'='*60}")
            
            try:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
                extracted_count = self._extract_from_sheet(df, sheet_name)
                total_extracted += extracted_count
                
                if extracted_count > 0:
                    self.extraction_log.append(f"✅ {sheet_name}: {extracted_count} parameters")
                else:
                    self.extraction_log.append(f"⚪ {sheet_name}: No parameters found")
                    
            except Exception as e:
                self.extraction_log.append(f"❌ {sheet_name}: Error - {str(e)}")
                print(f"Error: {e}")
        
        print(f"\n🎯 TOTAL EXTRACTED: {total_extracted} parameters")
        return self.soa_engine
    
    def _extract_from_sheet(self, df, sheet_name):
        """Extract rules from a single sheet"""
        
        extracted_count = 0
        
        # Look for tmaxfrac-based rules
        tmaxfrac_locations = self._find_tmaxfrac_locations(df)
        
        if tmaxfrac_locations:
            for tmaxfrac_row, tmaxfrac_col in tmaxfrac_locations:
                device_rules = self._extract_tmaxfrac_rules(df, sheet_name, tmaxfrac_row, tmaxfrac_col)
                if device_rules and device_rules.parameters:
                    device_key = self._generate_device_key(sheet_name, tmaxfrac_row)
                    self.soa_engine.add_device(device_key, device_rules)
                    extracted_count += len(device_rules.parameters)
                    print(f"  Extracted {len(device_rules.parameters)} parameters from tmaxfrac at row {tmaxfrac_row}")
        
        # Look for other rule patterns
        other_rules = self._extract_other_rules(df, sheet_name)
        if other_rules:
            device_key = f"{self._clean_sheet_name(sheet_name)}_other_rules"
            self.soa_engine.add_device(device_key, other_rules)
            extracted_count += len(other_rules.parameters)
            print(f"  Extracted {len(other_rules.parameters)} other rule parameters")
        
        return extracted_count
    
    def _find_tmaxfrac_locations(self, df):
        """Find all tmaxfrac locations in the sheet"""
        locations = []
        
        for row_idx in range(min(50, df.shape[0])):
            for col_idx in range(df.shape[1]):
                cell_value = str(df.iloc[row_idx, col_idx]).lower()
                if 'tmaxfrac' in cell_value:
                    locations.append((row_idx, col_idx))
        
        return locations
    
    def _extract_tmaxfrac_rules(self, df, sheet_name, tmaxfrac_row, tmaxfrac_col):
        """Extract rules from a tmaxfrac section"""
        
        # Get tmaxfrac values
        tmaxfrac_values = []
        if tmaxfrac_row + 1 < df.shape[0]:
            values_row = df.iloc[tmaxfrac_row + 1]
            for col_idx in range(tmaxfrac_col, min(tmaxfrac_col + 10, df.shape[1])):
                if pd.notna(values_row.iloc[col_idx]):
                    try:
                        val = float(values_row.iloc[col_idx])
                        tmaxfrac_values.append(val)
                    except:
                        # Handle non-numeric headers
                        pass
        
        if not tmaxfrac_values:
            return None
        
        print(f"    tmaxfrac values: {tmaxfrac_values}")
        
        # Extract parameters
        parameters = {}
        start_row = tmaxfrac_row + 2
        
        for row_idx in range(start_row, min(start_row + 200, df.shape[0])):
            if row_idx >= df.shape[0]:
                break
            
            row_data = df.iloc[row_idx]
            
            # Get severity and parameter name
            severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
            param_name = str(row_data.iloc[1]) if len(row_data) > 1 and pd.notna(row_data.iloc[1]) else ""
            
            # Skip invalid rows
            if not self._is_valid_parameter_row(severity, param_name):
                continue
            
            # Extract values for each tmaxfrac level
            param_values = {}
            for i, tmaxfrac_val in enumerate(tmaxfrac_values):
                col_idx = tmaxfrac_col + i
                if col_idx < df.shape[1] and pd.notna(row_data.iloc[col_idx]):
                    value = row_data.iloc[col_idx]
                    if isinstance(value, (int, float)):
                        param_values[tmaxfrac_val] = float(value)
                    else:
                        param_values[tmaxfrac_val] = str(value)
            
            if param_values:
                # Create SOAParameter
                soa_param = SOAParameter(
                    name=param_name,
                    severity=self._normalize_severity(severity),
                    param_type=self._infer_parameter_type(param_name),
                    unit=self._infer_parameter_unit(param_name),
                    values=param_values,
                    description=f"{severity} severity limit for {param_name}"
                )
                
                # Use unique key to handle duplicates
                param_key = f"{param_name}_{row_idx}"
                parameters[param_key] = soa_param
        
        if not parameters:
            return None
        
        # Create device rules
        device_info = self._extract_device_info(sheet_name, tmaxfrac_row)
        
        return DeviceRules(
            device_type=device_info['device_type'],
            subcategory=device_info['subcategory'],
            tmaxfrac_levels=tmaxfrac_values,
            parameters=parameters,
            metadata={
                'source_sheet': sheet_name,
                'tmaxfrac_row': tmaxfrac_row,
                'technology': 'smos10hv'
            }
        )
    
    def _extract_other_rules(self, df, sheet_name):
        """Extract non-tmaxfrac rules"""
        
        parameters = {}
        
        # Look for voltage/current limits and other patterns
        for row_idx in range(min(100, df.shape[0])):
            for col_idx in range(min(10, df.shape[1])):
                if pd.notna(df.iloc[row_idx, col_idx]):
                    cell_value = str(df.iloc[row_idx, col_idx])
                    
                    # Look for parameter-like patterns
                    if self._looks_like_parameter(cell_value):
                        # Look for numeric values in the same row
                        values = self._extract_row_values(df, row_idx, col_idx)
                        
                        if values:
                            param_key = f"{cell_value}_{row_idx}_{col_idx}"
                            parameters[param_key] = SOAParameter(
                                name=cell_value,
                                severity=Severity.HIGH,  # Default
                                param_type=self._infer_parameter_type(cell_value),
                                unit=self._infer_parameter_unit(cell_value),
                                values={0.0: values[0] if values else 0.0},  # Single value
                                description=f"Other rule for {cell_value}"
                            )
        
        if not parameters:
            return None
        
        device_info = self._extract_device_info(sheet_name, 0)
        
        return DeviceRules(
            device_type=device_info['device_type'],
            subcategory=f"{device_info['subcategory']}_other",
            tmaxfrac_levels=[0.0],
            parameters=parameters,
            metadata={
                'source_sheet': sheet_name,
                'rule_type': 'other_patterns',
                'technology': 'smos10hv'
            }
        )
    
    def _is_valid_parameter_row(self, severity, param_name):
        """Check if this looks like a valid parameter row"""
        
        # Skip empty or invalid parameter names
        if param_name in ['nan', 'parameter', '', 'NaN'] or len(param_name) < 2:
            return False
        
        # Skip very long parameter names (likely descriptions)
        if len(param_name) > 50:
            return False
        
        # Skip if severity is too long (likely a description)
        if len(severity) > 20:
            return False
        
        return True
    
    def _looks_like_parameter(self, cell_value):
        """Check if cell value looks like a parameter name"""
        
        if len(cell_value) < 3 or len(cell_value) > 30:
            return False
        
        # Look for parameter-like patterns
        param_indicators = ['v', 'i', 'limit', 'max', 'min', 'high', 'low', 'voltage', 'current']
        
        cell_lower = cell_value.lower()
        return any(indicator in cell_lower for indicator in param_indicators)
    
    def _extract_row_values(self, df, row_idx, start_col):
        """Extract numeric values from a row"""
        
        values = []
        for col_idx in range(start_col + 1, min(start_col + 10, df.shape[1])):
            if pd.notna(df.iloc[row_idx, col_idx]):
                try:
                    val = float(df.iloc[row_idx, col_idx])
                    values.append(val)
                except:
                    pass
        
        return values
    
    def _normalize_severity(self, severity):
        """Normalize severity to enum value"""
        severity_lower = severity.lower()
        if severity_lower in ['high', 'medium', 'low']:
            return Severity(severity_lower)
        return Severity.HIGH
    
    def _infer_parameter_type(self, param_name):
        """Infer parameter type from name"""
        name_lower = param_name.lower()
        
        if 'v' in name_lower and ('high' in name_lower or 'low' in name_lower or 'gate' in name_lower or 'drain' in name_lower):
            return ParameterType.VOLTAGE
        elif 'i' in name_lower or 'current' in name_lower:
            return ParameterType.CURRENT
        elif 'temp' in name_lower or name_lower.startswith('t'):
            return ParameterType.TEMPERATURE
        else:
            return ParameterType.GENERAL
    
    def _infer_parameter_unit(self, param_name):
        """Infer parameter unit from name"""
        name_lower = param_name.lower()
        
        if 'v' in name_lower or 'voltage' in name_lower:
            return "V"
        elif 'i' in name_lower or 'current' in name_lower:
            return "A"
        elif 'temp' in name_lower:
            return "°C"
        else:
            return "dimensionless"
    
    def _extract_device_info(self, sheet_name, row_hint):
        """Extract device information from sheet name and context"""
        
        device_info = {
            'technology': 'smos10hv',
            'device_type': 'unknown',
            'subcategory': 'general'
        }
        
        sheet_lower = sheet_name.lower()
        
        # Parse device type from sheet name
        if 'mos' in sheet_lower and 'sym' in sheet_lower:
            device_info.update({
                'device_type': 'mos_transistor',
                'subcategory': 'symmetric_on_off'
            })
        elif 'mos' in sheet_lower and 'monitor' in sheet_lower:
            device_info.update({
                'device_type': 'mos_transistor',
                'subcategory': 'monitor'
            })
        elif 'caps' in sheet_lower or 'capacitor' in sheet_lower:
            device_info.update({
                'device_type': 'capacitor',
                'subcategory': 'general'
            })
        elif 'sub' in sheet_lower and 'well' in sheet_lower:
            if 'hv' in sheet_lower:
                device_info.update({
                    'device_type': 'substrate',
                    'subcategory': 'well_hv'
                })
            else:
                device_info.update({
                    'device_type': 'substrate',
                    'subcategory': 'well_isolation'
                })
        elif 'oxrisk' in sheet_lower or 'oxide' in sheet_lower:
            device_info.update({
                'device_type': 'oxide',
                'subcategory': 'reliability_drift'
            })
        elif 'diode' in sheet_lower:
            device_info.update({
                'device_type': 'diode',
                'subcategory': 'forward_reverse'
            })
        elif 'bjt' in sheet_lower:
            device_info.update({
                'device_type': 'bjt',
                'subcategory': 'reverse'
            })
        elif 'resistor' in sheet_lower:
            device_info.update({
                'device_type': 'resistor',
                'subcategory': 'general'
            })
        elif 'hv' in sheet_lower and 'on' in sheet_lower:
            device_info.update({
                'device_type': 'hv_device',
                'subcategory': 'on_state'
            })
        elif 'hci' in sheet_lower or 'tddb' in sheet_lower:
            device_info.update({
                'device_type': 'reliability',
                'subcategory': 'hci_tddb'
            })
        
        return device_info
    
    def _generate_device_key(self, sheet_name, row_hint):
        """Generate unique device key"""
        device_info = self._extract_device_info(sheet_name, row_hint)
        base_key = f"{device_info['device_type']}_{device_info['subcategory']}"
        
        # Add row hint to make unique if needed
        if row_hint > 0:
            base_key += f"_r{row_hint}"
        
        return base_key
    
    def _clean_sheet_name(self, sheet_name):
        """Clean sheet name for use in device key"""
        return sheet_name.replace(' ', '_').replace('-', '_').lower()
    
    def save_complete_extraction(self, output_dir="."):
        """Save the complete extraction results"""
        
        from pathlib import Path
        output_path = Path(output_dir)
        
        # Export to JSON
        json_data = self.soa_engine.export_to_json()
        with open(output_path / "complete_soa_rules.json", "w") as f:
            json.dump(json_data, f, indent=2)
        
        # Save extraction log
        with open(output_path / "complete_extraction_log.txt", "w") as f:
            f.write("Complete SOA Rules Extraction Log\n")
            f.write("=" * 40 + "\n\n")
            for entry in self.extraction_log:
                f.write(f"{entry}\n")
        
        # Create summary
        total_devices = len(self.soa_engine.devices)
        total_params = sum(len(device.parameters) for device in self.soa_engine.devices.values())
        
        with open(output_path / "extraction_summary.txt", "w") as f:
            f.write("Complete SOA Rules Extraction Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total devices extracted: {total_devices}\n")
            f.write(f"Total parameters extracted: {total_params}\n\n")
            
            f.write("Device breakdown:\n")
            for device_key, device in self.soa_engine.devices.items():
                f.write(f"  {device_key}: {len(device.parameters)} parameters\n")
                f.write(f"    Type: {device.device_type}\n")
                f.write(f"    Subcategory: {device.subcategory}\n")
                f.write(f"    tmaxfrac levels: {device.tmaxfrac_levels}\n")
                f.write(f"    Source: {device.metadata.get('source_sheet', 'unknown')}\n\n")
        
        print(f"\n✅ Complete extraction saved to {output_path}/")
        print(f"   - complete_soa_rules.json")
        print(f"   - complete_extraction_log.txt")
        print(f"   - extraction_summary.txt")
        
        return total_devices, total_params

def main():
    """Main extraction function"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    # Create extractor
    extractor = CompleteSOAExtractor(excel_file)
    
    # Extract all rules
    soa_engine = extractor.extract_all_rules()
    
    # Save results
    total_devices, total_params = extractor.save_complete_extraction()
    
    print(f"\n🎯 COMPLETE EXTRACTION SUMMARY:")
    print(f"   Total devices: {total_devices}")
    print(f"   Total parameters: {total_params}")
    print(f"   Extraction log entries: {len(extractor.extraction_log)}")
    
    return soa_engine

if __name__ == "__main__":
    soa_engine = main()