#!/usr/bin/env python3
"""
Test the improved extractor on a single sheet to debug issues
"""

import pandas as pd
import json
from pathlib import Path

def test_single_sheet(sheet_name="10HV SOA OXRisk Drift "):
    """Test extraction on a single sheet with detailed debugging"""
    
    print(f"=== TESTING SINGLE SHEET: {sheet_name} ===")
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    if not Path(excel_file).exists():
        print("❌ Excel file not found")
        return
    
    # Load device mapping
    with open("simple_device_mapping.json", "r") as f:
        device_mapping = json.load(f)
    
    if sheet_name not in device_mapping["sheets"]:
        print(f"❌ Sheet {sheet_name} not in device mapping")
        return
    
    # Read the sheet
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        print(f"✅ Sheet loaded: {df.shape[0]} rows x {df.shape[1]} columns")
    except Exception as e:
        print(f"❌ Error loading sheet: {e}")
        return
    
    # Get device config
    device_config = device_mapping["sheets"][sheet_name]["devices"][0]  # Test first device
    tmaxfrac_row = device_config["tmaxfrac_row"]
    
    print(f"\n📋 Testing device: {device_config['name']}")
    print(f"   Expected tmaxfrac row: {tmaxfrac_row}")
    
    # Debug step 1: Check if tmaxfrac row exists
    if tmaxfrac_row >= df.shape[0]:
        print(f"❌ tmaxfrac row {tmaxfrac_row} is out of bounds (sheet has {df.shape[0]} rows)")
        return
    
    # Debug step 2: Show content around tmaxfrac row
    print(f"\n🔍 Content around row {tmaxfrac_row}:")
    start_row = max(0, tmaxfrac_row - 2)
    end_row = min(df.shape[0], tmaxfrac_row + 5)
    
    for r in range(start_row, end_row):
        row_content = []
        for c in range(min(5, df.shape[1])):
            cell = df.iloc[r, c]
            if pd.notna(cell):
                row_content.append(str(cell)[:30])  # Truncate long content
            else:
                row_content.append("NaN")
        marker = "👉" if r == tmaxfrac_row else "  "
        print(f"{marker} Row {r}: {row_content}")
    
    # Debug step 3: Look for tmaxfrac in the expected row
    print(f"\n🔍 Looking for 'tmaxfrac' in row {tmaxfrac_row}:")
    tmaxfrac_found = False
    tmaxfrac_col = None
    
    for col_idx in range(df.shape[1]):
        if pd.notna(df.iloc[tmaxfrac_row, col_idx]):
            cell_value = str(df.iloc[tmaxfrac_row, col_idx]).lower()
            if 'tmaxfrac' in cell_value:
                tmaxfrac_found = True
                tmaxfrac_col = col_idx
                print(f"   ✅ Found 'tmaxfrac' at column {col_idx}: {df.iloc[tmaxfrac_row, col_idx]}")
                break
    
    if not tmaxfrac_found:
        print(f"   ❌ 'tmaxfrac' not found in row {tmaxfrac_row}")
        
        # Search nearby rows
        print(f"\n🔍 Searching nearby rows for 'tmaxfrac':")
        for offset in range(-5, 6):
            search_row = tmaxfrac_row + offset
            if 0 <= search_row < df.shape[0]:
                for col_idx in range(df.shape[1]):
                    if pd.notna(df.iloc[search_row, col_idx]):
                        cell_value = str(df.iloc[search_row, col_idx]).lower()
                        if 'tmaxfrac' in cell_value:
                            print(f"   📍 Found 'tmaxfrac' at row {search_row}, col {col_idx}: {df.iloc[search_row, col_idx]}")
        return
    
    # Debug step 4: Extract tmaxfrac values
    print(f"\n🔍 Extracting tmaxfrac values from row {tmaxfrac_row + 1}:")
    tmaxfrac_levels = []
    
    if tmaxfrac_row + 1 < df.shape[0]:
        values_row = df.iloc[tmaxfrac_row + 1]
        print(f"   Values row content: {[values_row.iloc[i] for i in range(min(10, df.shape[1]))]}")
        
        for col_idx in range(tmaxfrac_col, min(tmaxfrac_col + 10, df.shape[1])):
            if pd.notna(values_row.iloc[col_idx]):
                try:
                    val = float(values_row.iloc[col_idx])
                    tmaxfrac_levels.append(val)
                    print(f"   ✅ tmaxfrac level: {val}")
                except:
                    print(f"   ⚠️ Non-numeric value: {values_row.iloc[col_idx]}")
    
    if not tmaxfrac_levels:
        print(f"   ❌ No tmaxfrac values extracted")
        return
    
    # Debug step 5: Look for parameters
    print(f"\n🔍 Looking for parameters starting from row {tmaxfrac_row + 2}:")
    start_row = tmaxfrac_row + 2
    param_count = 0
    
    for row_idx in range(start_row, min(start_row + 20, df.shape[0])):  # Check first 20 rows
        row_data = df.iloc[row_idx]
        
        severity = str(row_data.iloc[0]) if pd.notna(row_data.iloc[0]) else ""
        param_name = str(row_data.iloc[1]) if len(row_data) > 1 and pd.notna(row_data.iloc[1]) else ""
        
        # Show row content
        row_content = [str(row_data.iloc[i]) if pd.notna(row_data.iloc[i]) else "NaN" 
                      for i in range(min(5, len(row_data)))]
        
        # Check if valid parameter
        is_valid = (param_name not in ['nan', 'parameter', '', 'NaN'] and 
                   len(param_name) > 2 and len(param_name) < 50 and
                   len(severity) < 20)
        
        marker = "✅" if is_valid else "  "
        print(f"{marker} Row {row_idx}: {row_content}")
        
        if is_valid:
            param_count += 1
            
            # Check tmaxfrac values for this parameter
            tmaxfrac_values = {}
            for i, level in enumerate(tmaxfrac_levels):
                col_idx = tmaxfrac_col + i
                if col_idx < df.shape[1] and pd.notna(row_data.iloc[col_idx]):
                    tmaxfrac_values[level] = row_data.iloc[col_idx]
            
            if tmaxfrac_values:
                print(f"      tmaxfrac values: {tmaxfrac_values}")
            else:
                print(f"      ❌ No tmaxfrac values for this parameter")
    
    print(f"\n📊 SUMMARY:")
    print(f"   tmaxfrac found: {tmaxfrac_found}")
    print(f"   tmaxfrac levels: {tmaxfrac_levels}")
    print(f"   Valid parameters found: {param_count}")

def main():
    """Test different sheets"""
    
    # Test the failing sheets one by one
    failing_sheets = [
        "10HV SOA OXRisk Drift ",
        "10HV SOA SUB Well HV ",
        "10HV Diodes FWD-REV",
        "10HV BJT REV "
    ]
    
    for sheet in failing_sheets:
        test_single_sheet(sheet)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()