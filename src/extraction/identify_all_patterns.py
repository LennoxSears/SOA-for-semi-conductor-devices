#!/usr/bin/env python3
"""
Identify all device sections and rule patterns in Excel sheets
"""

import pandas as pd
import json
from pathlib import Path

def identify_all_patterns():
    """Identify all device sections and rule patterns across all sheets"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    if not Path(excel_file).exists():
        print("❌ Excel file not found")
        return
    
    print("=== IDENTIFYING ALL DEVICE SECTIONS AND RULE PATTERNS ===")
    
    xl_file = pd.ExcelFile(excel_file)
    all_patterns = {}
    
    for sheet_name in xl_file.sheet_names:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {sheet_name}")
        print(f"{'='*60}")
        
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            sheet_patterns = analyze_sheet_patterns(df, sheet_name)
            all_patterns[sheet_name] = sheet_patterns
            
        except Exception as e:
            print(f"Error: {e}")
            all_patterns[sheet_name] = {'error': str(e)}
    
    # Generate comprehensive mapping
    generate_pattern_mapping(all_patterns)
    
    return all_patterns

def analyze_sheet_patterns(df, sheet_name):
    """Analyze patterns in a single sheet"""
    
    patterns = {
        'tmaxfrac_sections': [],
        'device_identifiers': [],
        'parameter_blocks': [],
        'rule_structures': [],
        'other_patterns': []
    }
    
    print(f"Sheet dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
    
    # Find all tmaxfrac sections
    for row_idx in range(df.shape[0]):
        for col_idx in range(df.shape[1]):
            if pd.notna(df.iloc[row_idx, col_idx]):
                cell_value = str(df.iloc[row_idx, col_idx]).lower()
                
                if 'tmaxfrac' in cell_value:
                    tmaxfrac_info = analyze_tmaxfrac_section(df, row_idx, col_idx, sheet_name)
                    patterns['tmaxfrac_sections'].append(tmaxfrac_info)
                    print(f"  📊 tmaxfrac section at row {row_idx}: {tmaxfrac_info['param_count']} parameters")
    
    # Find device identifiers
    device_patterns = find_device_identifiers(df, sheet_name)
    patterns['device_identifiers'] = device_patterns
    
    if device_patterns:
        print(f"  🔧 Device identifiers found:")
        for device in device_patterns:
            print(f"    {device['type']} at row {device['row']}: {device['description']}")
    
    # Find parameter blocks (non-tmaxfrac)
    param_blocks = find_parameter_blocks(df, sheet_name)
    patterns['parameter_blocks'] = param_blocks
    
    if param_blocks:
        print(f"  📋 Parameter blocks found: {len(param_blocks)}")
        for block in param_blocks:
            print(f"    Block at row {block['start_row']}-{block['end_row']}: {block['param_count']} parameters")
    
    # Find other rule structures
    other_rules = find_other_rule_structures(df, sheet_name)
    patterns['other_patterns'] = other_rules
    
    if other_rules:
        print(f"  🔍 Other rule patterns: {len(other_rules)}")
    
    return patterns

def analyze_tmaxfrac_section(df, tmaxfrac_row, tmaxfrac_col, sheet_name):
    """Analyze a tmaxfrac section in detail"""
    
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
                    pass
    
    # Find associated device info
    device_context = find_device_context(df, tmaxfrac_row, sheet_name)
    
    # Count parameters in this section
    param_count = count_parameters_in_section(df, tmaxfrac_row, tmaxfrac_col)
    
    return {
        'row': tmaxfrac_row,
        'col': tmaxfrac_col,
        'tmaxfrac_values': tmaxfrac_values,
        'device_context': device_context,
        'param_count': param_count,
        'sheet': sheet_name
    }

def find_device_context(df, tmaxfrac_row, sheet_name):
    """Find device context around a tmaxfrac section"""
    
    # Look in nearby rows for device identifiers
    search_range = 10
    for offset in range(-search_range, search_range):
        row_idx = tmaxfrac_row + offset
        if 0 <= row_idx < df.shape[0]:
            for col_idx in range(df.shape[1]):
                if pd.notna(df.iloc[row_idx, col_idx]):
                    cell_value = str(df.iloc[row_idx, col_idx])
                    device_info = parse_device_identifier(cell_value, sheet_name)
                    if device_info:
                        return device_info
    
    return None

def parse_device_identifier(cell_value, sheet_name):
    """Parse device identifier from cell content"""
    
    cell_lower = cell_value.lower()
    
    # Comprehensive device patterns
    device_patterns = {
        # MOS Transistors
        'core nmos': {'type': 'mos_transistor', 'category': 'core', 'subcategory': 'nmos', 'name': 'NMOS Core'},
        'nmos_ll': {'type': 'mos_transistor', 'category': 'low_leakage', 'subcategory': 'nmos', 'name': 'NMOS Low Leakage'},
        'nmos_ull': {'type': 'mos_transistor', 'category': 'ultra_low_leakage', 'subcategory': 'nmos', 'name': 'NMOS Ultra Low Leakage'},
        'core pmos': {'type': 'mos_transistor', 'category': 'core', 'subcategory': 'pmos', 'name': 'PMOS Core'},
        'pmos_ll': {'type': 'mos_transistor', 'category': 'low_leakage', 'subcategory': 'pmos', 'name': 'PMOS Low Leakage'},
        'pmos_ull': {'type': 'mos_transistor', 'category': 'ultra_low_leakage', 'subcategory': 'pmos', 'name': 'PMOS Ultra Low Leakage'},
        'nmos5': {'type': 'mos_transistor', 'category': '5v', 'subcategory': 'nmos', 'name': 'NMOS 5V'},
        'pmos5': {'type': 'mos_transistor', 'category': '5v', 'subcategory': 'pmos', 'name': 'PMOS 5V'},
        
        # Capacitors
        'cglv': {'type': 'capacitor', 'category': 'gate', 'subcategory': 'low_voltage', 'name': 'CGLV Capacitor'},
        'cghv': {'type': 'capacitor', 'category': 'gate', 'subcategory': 'high_voltage', 'name': 'CGHV Capacitor'},
        'cghvf': {'type': 'capacitor', 'category': 'gate', 'subcategory': 'high_voltage_fast', 'name': 'CGHVF Capacitor'},
        'cghvm13': {'type': 'capacitor', 'category': 'gate', 'subcategory': 'high_voltage_m13', 'name': 'CGHVm13 Capacitor'},
        'cdp': {'type': 'capacitor', 'category': 'diffusion', 'subcategory': 'poly', 'name': 'CDP Capacitor'},
        'cdpf': {'type': 'capacitor', 'category': 'diffusion', 'subcategory': 'poly_fast', 'name': 'CDPF Capacitor'},
        'cdpfm13': {'type': 'capacitor', 'category': 'diffusion', 'subcategory': 'poly_fast_m13', 'name': 'CDPFm13 Capacitor'},
        'cfrlv': {'type': 'capacitor', 'category': 'fringe', 'subcategory': 'low_voltage', 'name': 'CFRLV Capacitor'},
        'cfrlvm13': {'type': 'capacitor', 'category': 'fringe', 'subcategory': 'low_voltage_m13', 'name': 'CFRLVm13 Capacitor'},
        'cfr45': {'type': 'capacitor', 'category': 'fringe', 'subcategory': '45nm', 'name': 'CFR45 Capacitor'},
        'cfr45m13': {'type': 'capacitor', 'category': 'fringe', 'subcategory': '45nm_m13', 'name': 'CFR45m13 Capacitor'},
        'cfr90': {'type': 'capacitor', 'category': 'fringe', 'subcategory': '90nm', 'name': 'CFR90 Capacitor'},
        'cfr90m13': {'type': 'capacitor', 'category': 'fringe', 'subcategory': '90nm_m13', 'name': 'CFR90m13 Capacitor'},
        'cfr120': {'type': 'capacitor', 'category': 'fringe', 'subcategory': '120nm', 'name': 'CFR120 Capacitor'},
        'cfr120m13': {'type': 'capacitor', 'category': 'fringe', 'subcategory': '120nm_m13', 'name': 'CFR120m13 Capacitor'},
        
        # Diodes
        'diode': {'type': 'diode', 'category': 'general', 'subcategory': 'standard', 'name': 'Diode'},
        'diode_fwd': {'type': 'diode', 'category': 'forward', 'subcategory': 'standard', 'name': 'Forward Diode'},
        'diode_rev': {'type': 'diode', 'category': 'reverse', 'subcategory': 'standard', 'name': 'Reverse Diode'},
        
        # BJTs
        'bjt': {'type': 'bjt', 'category': 'bipolar', 'subcategory': 'standard', 'name': 'BJT'},
        'npn': {'type': 'bjt', 'category': 'npn', 'subcategory': 'standard', 'name': 'NPN BJT'},
        'pnp': {'type': 'bjt', 'category': 'pnp', 'subcategory': 'standard', 'name': 'PNP BJT'},
        
        # Resistors
        'resistor': {'type': 'resistor', 'category': 'general', 'subcategory': 'standard', 'name': 'Resistor'},
        'res_poly': {'type': 'resistor', 'category': 'poly', 'subcategory': 'standard', 'name': 'Poly Resistor'},
        'res_diff': {'type': 'resistor', 'category': 'diffusion', 'subcategory': 'standard', 'name': 'Diffusion Resistor'},
        
        # Substrate/Well
        'substrate': {'type': 'substrate', 'category': 'bulk', 'subcategory': 'standard', 'name': 'Substrate'},
        'well': {'type': 'substrate', 'category': 'well', 'subcategory': 'isolation', 'name': 'Well'},
        'nwell': {'type': 'substrate', 'category': 'nwell', 'subcategory': 'isolation', 'name': 'N-Well'},
        'pwell': {'type': 'substrate', 'category': 'pwell', 'subcategory': 'isolation', 'name': 'P-Well'},
    }
    
    for pattern, device_info in device_patterns.items():
        if pattern in cell_lower:
            device_info['description'] = cell_value.strip()
            device_info['source_sheet'] = sheet_name
            return device_info
    
    return None

def find_device_identifiers(df, sheet_name):
    """Find all device identifiers in the sheet"""
    
    devices = []
    
    for row_idx in range(min(50, df.shape[0])):  # Check first 50 rows
        for col_idx in range(df.shape[1]):
            if pd.notna(df.iloc[row_idx, col_idx]):
                cell_value = str(df.iloc[row_idx, col_idx])
                device_info = parse_device_identifier(cell_value, sheet_name)
                if device_info:
                    device_info['row'] = row_idx
                    device_info['col'] = col_idx
                    devices.append(device_info)
    
    return devices

def count_parameters_in_section(df, tmaxfrac_row, tmaxfrac_col):
    """Count parameters in a tmaxfrac section"""
    
    param_count = 0
    start_row = tmaxfrac_row + 2  # Skip tmaxfrac and header rows
    
    for row_idx in range(start_row, min(start_row + 100, df.shape[0])):
        if row_idx >= df.shape[0]:
            break
        
        row_data = df.iloc[row_idx]
        
        # Check if this looks like a parameter row
        severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
        param_name = str(row_data.iloc[1]) if len(row_data) > 1 and pd.notna(row_data.iloc[1]) else ""
        
        # Valid parameter criteria
        if (param_name not in ['nan', 'parameter', '', 'NaN'] and 
            len(param_name) > 2 and len(param_name) < 50 and
            severity not in ['nan', '', 'NaN'] and len(severity) < 20):
            
            # Check if there are values in tmaxfrac columns
            has_values = False
            for col_offset in range(5):  # Check next 5 columns
                col_idx = tmaxfrac_col + col_offset
                if col_idx < df.shape[1] and pd.notna(row_data.iloc[col_idx]):
                    has_values = True
                    break
            
            if has_values:
                param_count += 1
    
    return param_count

def find_parameter_blocks(df, sheet_name):
    """Find parameter blocks that don't use tmaxfrac"""
    
    blocks = []
    current_block = None
    
    for row_idx in range(df.shape[0]):
        # Look for parameter-like patterns
        if len(df.iloc[row_idx]) > 1:
            cell1 = str(df.iloc[row_idx, 0]) if pd.notna(df.iloc[row_idx, 0]) else ""
            cell2 = str(df.iloc[row_idx, 1]) if pd.notna(df.iloc[row_idx, 1]) else ""
            
            # Check if this looks like a parameter row
            is_param_row = False
            if (any(pattern in cell2.lower() for pattern in ['vhigh', 'vlow', 'ihigh', 'ilow', 'limit', 'max', 'min']) and
                len(cell2) < 30):
                is_param_row = True
            
            if is_param_row:
                if current_block is None:
                    current_block = {
                        'start_row': row_idx,
                        'end_row': row_idx,
                        'param_count': 1,
                        'sheet': sheet_name
                    }
                else:
                    current_block['end_row'] = row_idx
                    current_block['param_count'] += 1
            else:
                if current_block is not None and current_block['param_count'] > 2:
                    blocks.append(current_block)
                current_block = None
    
    # Add final block if exists
    if current_block is not None and current_block['param_count'] > 2:
        blocks.append(current_block)
    
    return blocks

def find_other_rule_structures(df, sheet_name):
    """Find other rule structures and patterns"""
    
    patterns = []
    
    # Look for voltage/current limit patterns
    for row_idx in range(df.shape[0]):
        for col_idx in range(df.shape[1]):
            if pd.notna(df.iloc[row_idx, col_idx]):
                cell_value = str(df.iloc[row_idx, col_idx]).lower()
                
                # Look for limit patterns
                if any(pattern in cell_value for pattern in ['voltage limit', 'current limit', 'breakdown', 'threshold']):
                    patterns.append({
                        'type': 'limit_pattern',
                        'row': row_idx,
                        'col': col_idx,
                        'content': cell_value,
                        'sheet': sheet_name
                    })
    
    return patterns

def generate_pattern_mapping(all_patterns):
    """Generate comprehensive mapping of all patterns found"""
    
    print(f"\n{'='*80}")
    print("COMPREHENSIVE PATTERN MAPPING")
    print(f"{'='*80}")
    
    total_tmaxfrac_sections = 0
    total_devices = 0
    total_param_blocks = 0
    
    mapping = {
        'sheets': {},
        'summary': {
            'total_sheets': len(all_patterns),
            'sheets_with_tmaxfrac': 0,
            'sheets_with_devices': 0,
            'total_tmaxfrac_sections': 0,
            'total_devices': 0,
            'total_param_blocks': 0
        }
    }
    
    for sheet_name, patterns in all_patterns.items():
        if 'error' in patterns:
            continue
        
        sheet_summary = {
            'tmaxfrac_sections': len(patterns['tmaxfrac_sections']),
            'device_identifiers': len(patterns['device_identifiers']),
            'parameter_blocks': len(patterns['parameter_blocks']),
            'estimated_total_params': 0
        }
        
        # Calculate estimated parameters
        for section in patterns['tmaxfrac_sections']:
            sheet_summary['estimated_total_params'] += section['param_count']
        
        for block in patterns['parameter_blocks']:
            sheet_summary['estimated_total_params'] += block['param_count']
        
        mapping['sheets'][sheet_name] = sheet_summary
        
        # Update totals
        if sheet_summary['tmaxfrac_sections'] > 0:
            mapping['summary']['sheets_with_tmaxfrac'] += 1
        if sheet_summary['device_identifiers'] > 0:
            mapping['summary']['sheets_with_devices'] += 1
        
        mapping['summary']['total_tmaxfrac_sections'] += sheet_summary['tmaxfrac_sections']
        mapping['summary']['total_devices'] += sheet_summary['device_identifiers']
        mapping['summary']['total_param_blocks'] += sheet_summary['parameter_blocks']
        
        print(f"\n{sheet_name}:")
        print(f"  tmaxfrac sections: {sheet_summary['tmaxfrac_sections']}")
        print(f"  Device identifiers: {sheet_summary['device_identifiers']}")
        print(f"  Parameter blocks: {sheet_summary['parameter_blocks']}")
        print(f"  Estimated parameters: {sheet_summary['estimated_total_params']}")
        
        if patterns['device_identifiers']:
            print(f"  Devices found:")
            for device in patterns['device_identifiers']:
                print(f"    - {device['name']} ({device['type']}) at row {device['row']}")
    
    # Save mapping to file
    with open("pattern_mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n📊 OVERALL SUMMARY:")
    print(f"  Total sheets: {mapping['summary']['total_sheets']}")
    print(f"  Sheets with tmaxfrac: {mapping['summary']['sheets_with_tmaxfrac']}")
    print(f"  Sheets with devices: {mapping['summary']['sheets_with_devices']}")
    print(f"  Total tmaxfrac sections: {mapping['summary']['total_tmaxfrac_sections']}")
    print(f"  Total device identifiers: {mapping['summary']['total_devices']}")
    print(f"  Total parameter blocks: {mapping['summary']['total_param_blocks']}")
    
    print(f"\n✅ Pattern mapping saved to pattern_mapping.json")
    
    return mapping

def main():
    """Main function"""
    all_patterns = identify_all_patterns()
    return all_patterns

if __name__ == "__main__":
    main()