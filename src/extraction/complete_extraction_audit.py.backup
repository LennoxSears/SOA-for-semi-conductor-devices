#!/usr/bin/env python3
"""
Complete audit of rule extraction from Excel file
Check if all available rules were extracted
"""

import pandas as pd
import json
from soa_rules import load_soa_rules

def audit_all_sheets():
    """Audit all sheets in the Excel file for rule content"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    print("=== COMPLETE EXCEL RULE EXTRACTION AUDIT ===")
    
    # Get all sheet names
    xl_file = pd.ExcelFile(excel_file)
    all_sheets = xl_file.sheet_names
    
    print(f"Total sheets in Excel: {len(all_sheets)}")
    
    rule_summary = {
        'total_sheets': len(all_sheets),
        'soa_sheets': 0,
        'sheets_with_rules': 0,
        'sheets_with_tmaxfrac': 0,
        'total_parameters_found': 0,
        'extracted_parameters': 0,
        'sheet_details': {}
    }
    
    # Analyze each sheet
    for sheet_name in all_sheets:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {sheet_name}")
        print(f"{'='*60}")
        
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            sheet_analysis = analyze_sheet_for_rules(df, sheet_name)
            rule_summary['sheet_details'][sheet_name] = sheet_analysis
            
            if 'SOA' in sheet_name:
                rule_summary['soa_sheets'] += 1
            
            if sheet_analysis['has_rules']:
                rule_summary['sheets_with_rules'] += 1
            
            if sheet_analysis['has_tmaxfrac']:
                rule_summary['sheets_with_tmaxfrac'] += 1
            
            rule_summary['total_parameters_found'] += sheet_analysis['parameter_count']
            
        except Exception as e:
            print(f"Error reading {sheet_name}: {e}")
            rule_summary['sheet_details'][sheet_name] = {
                'error': str(e),
                'has_rules': False,
                'has_tmaxfrac': False,
                'parameter_count': 0
            }
    
    return rule_summary

def analyze_sheet_for_rules(df, sheet_name):
    """Analyze a single sheet for rule content"""
    
    analysis = {
        'sheet_name': sheet_name,
        'dimensions': f"{df.shape[0]}x{df.shape[1]}",
        'has_rules': False,
        'has_tmaxfrac': False,
        'parameter_count': 0,
        'tmaxfrac_locations': [],
        'parameters_found': [],
        'rule_structure': None
    }
    
    print(f"Sheet dimensions: {analysis['dimensions']}")
    
    # Look for tmaxfrac
    tmaxfrac_locations = []
    for row_idx in range(min(30, df.shape[0])):
        for col_idx in range(df.shape[1]):
            cell_value = str(df.iloc[row_idx, col_idx]).lower()
            if 'tmaxfrac' in cell_value:
                tmaxfrac_locations.append((row_idx, col_idx))
                analysis['has_tmaxfrac'] = True
                print(f"Found tmaxfrac at row {row_idx}, col {col_idx}")
    
    analysis['tmaxfrac_locations'] = tmaxfrac_locations
    
    # If tmaxfrac found, look for parameters
    if tmaxfrac_locations:
        for tmaxfrac_row, tmaxfrac_col in tmaxfrac_locations:
            parameters = extract_parameters_from_tmaxfrac_section(df, tmaxfrac_row, tmaxfrac_col)
            analysis['parameters_found'].extend(parameters)
            analysis['parameter_count'] += len(parameters)
            
            if parameters:
                analysis['has_rules'] = True
                print(f"Found {len(parameters)} parameters in this tmaxfrac section")
                for param in parameters[:5]:  # Show first 5
                    print(f"  - {param['name']}: {param['values']}")
                if len(parameters) > 5:
                    print(f"  ... and {len(parameters) - 5} more")
    
    # Look for other rule patterns even without tmaxfrac
    if not analysis['has_rules']:
        other_rules = look_for_other_rule_patterns(df, sheet_name)
        if other_rules:
            analysis['has_rules'] = True
            analysis['parameter_count'] = len(other_rules)
            analysis['parameters_found'] = other_rules
            print(f"Found {len(other_rules)} other rule patterns")
    
    return analysis

def extract_parameters_from_tmaxfrac_section(df, tmaxfrac_row, tmaxfrac_col):
    """Extract parameters from a tmaxfrac section"""
    
    parameters = []
    
    # Get tmaxfrac values
    tmaxfrac_values = []
    if tmaxfrac_row + 1 < df.shape[0]:
        values_row = df.iloc[tmaxfrac_row + 1]
        for col_idx in range(tmaxfrac_col, min(tmaxfrac_col + 5, df.shape[1])):
            if pd.notna(values_row.iloc[col_idx]):
                try:
                    val = float(values_row.iloc[col_idx])
                    tmaxfrac_values.append(val)
                except:
                    pass
    
    # Look for parameters
    start_row = tmaxfrac_row + 2
    for row_idx in range(start_row, min(start_row + 100, df.shape[0])):
        if row_idx >= df.shape[0]:
            break
            
        row_data = df.iloc[row_idx]
        
        # Check if this looks like a parameter row
        severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
        param_name = str(row_data.iloc[1]) if len(row_data) > 1 and pd.notna(row_data.iloc[1]) else ""
        
        # Skip invalid rows
        if param_name in ['nan', 'parameter', ''] or len(param_name) < 3:
            continue
        
        # Skip if severity doesn't look right
        if severity.lower() not in ['high', 'medium', 'low', 'severity'] and len(severity) > 10:
            continue
        
        # Extract values
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
            parameters.append({
                'name': param_name,
                'severity': severity.lower() if severity.lower() in ['high', 'medium', 'low'] else 'unknown',
                'values': param_values,
                'row': row_idx
            })
    
    return parameters

def look_for_other_rule_patterns(df, sheet_name):
    """Look for other rule patterns that might not use tmaxfrac"""
    
    rules = []
    
    # Look for voltage/current limits, min/max values, etc.
    rule_keywords = ['limit', 'max', 'min', 'voltage', 'current', 'vdd', 'vss', 'high', 'low']
    
    for row_idx in range(min(50, df.shape[0])):
        for col_idx in range(min(10, df.shape[1])):
            if pd.notna(df.iloc[row_idx, col_idx]):
                cell_value = str(df.iloc[row_idx, col_idx]).lower()
                
                # Look for parameter-like patterns
                if any(keyword in cell_value for keyword in rule_keywords):
                    if len(cell_value) < 50:  # Avoid very long cells
                        # Check if there are numeric values in nearby cells
                        nearby_values = []
                        for c in range(max(0, col_idx-2), min(df.shape[1], col_idx+5)):
                            if pd.notna(df.iloc[row_idx, c]):
                                try:
                                    val = float(df.iloc[row_idx, c])
                                    nearby_values.append(val)
                                except:
                                    pass
                        
                        if nearby_values:
                            rules.append({
                                'name': cell_value,
                                'values': nearby_values,
                                'location': f"row {row_idx}, col {col_idx}",
                                'type': 'other_pattern'
                            })
    
    # Remove duplicates
    unique_rules = []
    seen_names = set()
    for rule in rules:
        if rule['name'] not in seen_names:
            unique_rules.append(rule)
            seen_names.add(rule['name'])
    
    return unique_rules[:10]  # Limit to 10 to avoid noise

def compare_with_extracted():
    """Compare audit results with what was actually extracted"""
    
    print(f"\n{'='*80}")
    print("COMPARISON WITH EXTRACTED RULES")
    print(f"{'='*80}")
    
    # Load extracted rules
    soa = load_soa_rules()
    
    extracted_summary = {
        'devices': len(soa.devices),
        'total_parameters': sum(len(device.parameters) for device in soa.devices.values()),
        'device_details': {}
    }
    
    for device_key, device in soa.devices.items():
        extracted_summary['device_details'][device_key] = {
            'parameters': len(device.parameters),
            'tmaxfrac_levels': device.tmaxfrac_levels,
            'parameter_names': list(device.parameters.keys())
        }
    
    print("EXTRACTED RULES SUMMARY:")
    print(f"  Devices: {extracted_summary['devices']}")
    print(f"  Total parameters: {extracted_summary['total_parameters']}")
    
    for device_key, details in extracted_summary['device_details'].items():
        print(f"\n  {device_key}:")
        print(f"    Parameters: {details['parameters']}")
        print(f"    tmaxfrac levels: {details['tmaxfrac_levels']}")
        print(f"    Parameter names: {details['parameter_names']}")
    
    return extracted_summary

def generate_extraction_report(audit_results, extracted_summary):
    """Generate final extraction completeness report"""
    
    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETENESS REPORT")
    print(f"{'='*80}")
    
    print(f"📊 EXCEL CONTENT AUDIT:")
    print(f"  Total sheets: {audit_results['total_sheets']}")
    print(f"  SOA sheets: {audit_results['soa_sheets']}")
    print(f"  Sheets with rules: {audit_results['sheets_with_rules']}")
    print(f"  Sheets with tmaxfrac: {audit_results['sheets_with_tmaxfrac']}")
    print(f"  Total parameters found: {audit_results['total_parameters_found']}")
    
    print(f"\n📥 EXTRACTION RESULTS:")
    print(f"  Devices extracted: {extracted_summary['devices']}")
    print(f"  Parameters extracted: {extracted_summary['total_parameters']}")
    
    print(f"\n📈 EXTRACTION RATE:")
    if audit_results['total_parameters_found'] > 0:
        extraction_rate = (extracted_summary['total_parameters'] / audit_results['total_parameters_found']) * 100
        print(f"  Parameter extraction rate: {extraction_rate:.1f}%")
    else:
        print(f"  Parameter extraction rate: N/A (no parameters found)")
    
    print(f"\n📋 DETAILED SHEET ANALYSIS:")
    for sheet_name, details in audit_results['sheet_details'].items():
        if details.get('has_rules', False) or details.get('has_tmaxfrac', False):
            status = "✅ EXTRACTED" if any(sheet_name in device.metadata.get('source_sheet', '') 
                                         for device in extracted_summary['device_details'].values() 
                                         if hasattr(device, 'metadata')) else "❌ NOT EXTRACTED"
            print(f"  {sheet_name}: {details['parameter_count']} params, tmaxfrac: {details['has_tmaxfrac']} {status}")
    
    # Identify missing extractions
    print(f"\n🔍 POTENTIALLY MISSED EXTRACTIONS:")
    for sheet_name, details in audit_results['sheet_details'].items():
        if details.get('parameter_count', 0) > 0:
            # Check if this sheet was extracted
            extracted = False
            for device_key, device_details in extracted_summary['device_details'].items():
                # This is a simplified check - in real implementation, would need better tracking
                if sheet_name.replace(' ', '_').lower() in device_key.lower():
                    extracted = True
                    break
            
            if not extracted and details['parameter_count'] > 5:  # Only flag sheets with significant parameters
                print(f"  ⚠️  {sheet_name}: {details['parameter_count']} parameters not extracted")

def main():
    """Main audit function"""
    
    # Perform complete audit
    audit_results = audit_all_sheets()
    
    # Compare with extracted rules
    extracted_summary = compare_with_extracted()
    
    # Generate final report
    generate_extraction_report(audit_results, extracted_summary)
    
    return audit_results, extracted_summary

if __name__ == "__main__":
    audit_results, extracted_summary = main()