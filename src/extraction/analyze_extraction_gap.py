#!/usr/bin/env python3
"""
Analyze the gap between complete extraction (744 params) and device-grouped extraction (104 params)
"""

import json
import pandas as pd
from pathlib import Path

def analyze_extraction_gap():
    """Compare complete vs device-grouped extractions to find missing rules"""
    
    print("=== EXTRACTION GAP ANALYSIS ===")
    
    # Load complete extraction results
    complete_file = "complete_soa_rules.json"
    device_grouped_file = "device_grouped_soa_rules.json"
    
    if not Path(complete_file).exists():
        print(f"❌ {complete_file} not found. Run 'make extract-all' first.")
        return
    
    if not Path(device_grouped_file).exists():
        print(f"❌ {device_grouped_file} not found. Run 'make extract' first.")
        return
    
    # Load both extractions
    with open(complete_file, 'r') as f:
        complete_data = json.load(f)
    
    with open(device_grouped_file, 'r') as f:
        device_data = json.load(f)
    
    # Analyze complete extraction
    complete_devices = complete_data['soa_rules']['devices']
    complete_params = 0
    complete_breakdown = {}
    
    print("📊 COMPLETE EXTRACTION ANALYSIS:")
    for device_key, device_info in complete_devices.items():
        param_count = len(device_info['parameters'])
        complete_params += param_count
        complete_breakdown[device_key] = {
            'params': param_count,
            'source': device_info.get('metadata', {}).get('source_sheet', 'unknown'),
            'type': device_info.get('device_type', 'unknown')
        }
        print(f"  {device_key}: {param_count} params from {complete_breakdown[device_key]['source']}")
    
    print(f"\nTotal complete extraction: {complete_params} parameters")
    
    # Analyze device-grouped extraction
    device_grouped_devices = device_data['soa_device_rules']['devices']
    grouped_params = 0
    grouped_breakdown = {}
    
    print(f"\n📋 DEVICE-GROUPED EXTRACTION ANALYSIS:")
    for device_key, device_info in device_grouped_devices.items():
        param_count = len(device_info['parameters'])
        grouped_params += param_count
        grouped_breakdown[device_key] = {
            'params': param_count,
            'source': device_info['device_info']['source_sheet'],
            'type': device_info['device_info']['type']
        }
        print(f"  {device_key}: {param_count} params from {grouped_breakdown[device_key]['source']}")
    
    print(f"\nTotal device-grouped extraction: {grouped_params} parameters")
    
    # Calculate gap
    gap = complete_params - grouped_params
    coverage = (grouped_params / complete_params) * 100 if complete_params > 0 else 0
    
    print(f"\n🎯 GAP ANALYSIS:")
    print(f"  Missing parameters: {gap}")
    print(f"  Coverage: {coverage:.1f}%")
    print(f"  Gap: {100-coverage:.1f}%")
    
    # Identify missing sources
    complete_sources = set(info['source'] for info in complete_breakdown.values())
    grouped_sources = set(info['source'] for info in grouped_breakdown.values())
    missing_sources = complete_sources - grouped_sources
    
    print(f"\n📋 MISSING SOURCES:")
    for source in missing_sources:
        missing_params = sum(info['params'] for device, info in complete_breakdown.items() 
                           if info['source'] == source)
        print(f"  {source}: ~{missing_params} parameters not captured")
    
    # Analyze by sheet
    print(f"\n📊 SHEET-BY-SHEET ANALYSIS:")
    sheet_analysis = analyze_by_sheet()
    
    return {
        'complete_params': complete_params,
        'grouped_params': grouped_params,
        'gap': gap,
        'coverage': coverage,
        'missing_sources': missing_sources,
        'sheet_analysis': sheet_analysis
    }

def analyze_by_sheet():
    """Analyze each Excel sheet to understand rule distribution"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    if not Path(excel_file).exists():
        print("❌ Excel file not found")
        return {}
    
    xl_file = pd.ExcelFile(excel_file)
    sheet_analysis = {}
    
    for sheet_name in xl_file.sheet_names:
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            
            # Count potential parameters
            param_indicators = 0
            tmaxfrac_count = 0
            device_indicators = 0
            
            for row_idx in range(min(100, df.shape[0])):
                for col_idx in range(df.shape[1]):
                    if pd.notna(df.iloc[row_idx, col_idx]):
                        cell_value = str(df.iloc[row_idx, col_idx]).lower()
                        
                        # Count tmaxfrac occurrences
                        if 'tmaxfrac' in cell_value:
                            tmaxfrac_count += 1
                        
                        # Count parameter-like patterns
                        if any(pattern in cell_value for pattern in ['vhigh', 'vlow', 'ihigh', 'ilow', 'limit']):
                            if len(cell_value) < 30:  # Avoid long descriptions
                                param_indicators += 1
                        
                        # Count device indicators
                        if any(pattern in cell_value for pattern in ['nmos', 'pmos', 'capacitor', 'diode', 'bjt']):
                            device_indicators += 1
            
            sheet_analysis[sheet_name] = {
                'dimensions': f"{df.shape[0]}x{df.shape[1]}",
                'tmaxfrac_sections': tmaxfrac_count,
                'param_indicators': param_indicators,
                'device_indicators': device_indicators,
                'estimated_params': param_indicators // 3  # Rough estimate
            }
            
            print(f"  {sheet_name}:")
            print(f"    Dimensions: {sheet_analysis[sheet_name]['dimensions']}")
            print(f"    tmaxfrac sections: {tmaxfrac_count}")
            print(f"    Parameter indicators: {param_indicators}")
            print(f"    Device indicators: {device_indicators}")
            print(f"    Estimated parameters: {sheet_analysis[sheet_name]['estimated_params']}")
            
        except Exception as e:
            print(f"  {sheet_name}: Error - {e}")
            sheet_analysis[sheet_name] = {'error': str(e)}
    
    return sheet_analysis

def identify_missing_patterns():
    """Identify what types of rules are being missed"""
    
    print(f"\n🔍 IDENTIFYING MISSING RULE PATTERNS:")
    
    # Load complete extraction to see what was found
    with open("complete_soa_rules.json", 'r') as f:
        complete_data = json.load(f)
    
    # Analyze rule patterns in complete extraction
    all_devices = complete_data['soa_rules']['devices']
    
    print(f"\nComplete extraction device types:")
    device_types = {}
    for device_key, device_info in all_devices.items():
        device_type = device_info.get('device_type', 'unknown')
        source_sheet = device_info.get('metadata', {}).get('source_sheet', 'unknown')
        param_count = len(device_info['parameters'])
        
        if device_type not in device_types:
            device_types[device_type] = []
        
        device_types[device_type].append({
            'key': device_key,
            'source': source_sheet,
            'params': param_count
        })
    
    for device_type, devices in device_types.items():
        total_params = sum(d['params'] for d in devices)
        print(f"\n  {device_type.upper()}: {total_params} total parameters")
        for device in devices:
            print(f"    {device['key']}: {device['params']} params from {device['source']}")
    
    return device_types

def main():
    """Main analysis function"""
    
    gap_analysis = analyze_extraction_gap()
    device_types = identify_missing_patterns()
    
    print(f"\n{'='*80}")
    print("SUMMARY AND RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if gap_analysis:
        print(f"📊 Current Status:")
        print(f"  Complete extraction: {gap_analysis['complete_params']} parameters")
        print(f"  Device-grouped: {gap_analysis['grouped_params']} parameters")
        print(f"  Missing: {gap_analysis['gap']} parameters ({100-gap_analysis['coverage']:.1f}%)")
        
        print(f"\n🎯 Next Steps:")
        print(f"  1. Improve device recognition for missing sources")
        print(f"  2. Enhance parameter extraction for non-tmaxfrac rules")
        print(f"  3. Add support for 'other_rules' patterns")
        print(f"  4. Map all device variants to proper categories")
        
        if gap_analysis['missing_sources']:
            print(f"\n📋 Priority Sources to Fix:")
            for source in gap_analysis['missing_sources']:
                print(f"  - {source}")

if __name__ == "__main__":
    main()