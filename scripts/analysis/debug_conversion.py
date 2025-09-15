#!/usr/bin/env python3
"""
Debug the conversion discrepancy between Excel and DSL
"""

import pandas as pd

def debug_excel_reading():
    """Debug Excel reading to understand the data structure"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    print("=== DEBUGGING EXCEL CONVERSION ===")
    
    # Read MOS transistor sheet
    df = pd.read_excel(excel_file, sheet_name="10HV SOA SYM ON-OFF", header=None)
    
    print("Raw Excel data around tmaxfrac:")
    
    # Find tmaxfrac
    for row_idx in range(20):
        for col_idx in range(df.shape[1]):
            cell_value = str(df.iloc[row_idx, col_idx]).lower()
            if 'tmaxfrac' in cell_value:
                print(f"Found tmaxfrac at row {row_idx}, col {col_idx}")
                
                # Show surrounding data
                start_row = max(0, row_idx - 2)
                end_row = min(df.shape[0], row_idx + 20)
                
                print(f"\nData from row {start_row} to {end_row}:")
                for r in range(start_row, end_row):
                    row_data = []
                    for c in range(min(7, df.shape[1])):
                        cell = df.iloc[r, c]
                        if pd.notna(cell):
                            row_data.append(str(cell))
                        else:
                            row_data.append("NaN")
                    print(f"Row {r}: {row_data}")
                
                return row_idx
    
    return None

def debug_parameter_extraction():
    """Debug parameter extraction logic"""
    
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    df = pd.read_excel(excel_file, sheet_name="10HV SOA SYM ON-OFF", header=None)
    
    # Find tmaxfrac row
    tmaxfrac_row = 5  # From previous analysis
    
    print(f"\n=== PARAMETER EXTRACTION DEBUG ===")
    print(f"tmaxfrac row: {tmaxfrac_row}")
    
    # Get tmaxfrac values
    values_row = df.iloc[tmaxfrac_row + 1]
    print(f"Values row {tmaxfrac_row + 1}: {[values_row.iloc[i] for i in range(7)]}")
    
    # Look for vhigh_ds_on specifically
    print(f"\nLooking for vhigh_ds_on parameter:")
    
    for row_idx in range(tmaxfrac_row + 2, tmaxfrac_row + 30):
        if row_idx < df.shape[0]:
            severity = df.iloc[row_idx, 0] if pd.notna(df.iloc[row_idx, 0]) else ""
            param_name = df.iloc[row_idx, 1] if pd.notna(df.iloc[row_idx, 1]) else ""
            
            if 'vhigh_ds_on' in str(param_name):
                print(f"Found at row {row_idx}:")
                row_data = [df.iloc[row_idx, c] for c in range(7)]
                print(f"  Full row: {row_data}")
                
                # Extract values
                values = {}
                tmaxfrac_levels = [0.1, 0.01, 0.0]
                for i, tmaxfrac in enumerate(tmaxfrac_levels):
                    col_idx = 2 + i
                    if col_idx < df.shape[1]:
                        value = df.iloc[row_idx, col_idx]
                        if pd.notna(value):
                            values[tmaxfrac] = value
                
                print(f"  Extracted values: {values}")
                break

if __name__ == "__main__":
    tmaxfrac_row = debug_excel_reading()
    if tmaxfrac_row:
        debug_parameter_extraction()