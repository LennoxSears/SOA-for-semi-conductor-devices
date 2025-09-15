#!/usr/bin/env python3
"""
Analyze the SOA Excel file to understand rules structure and tmaxfrac parameter
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def analyze_excel_structure():
    """Analyze the Excel file structure and content"""
    excel_file = "SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx"
    
    print("=== Excel File Analysis ===")
    print(f"File: {excel_file}")
    
    # Read all sheet names
    try:
        xl_file = pd.ExcelFile(excel_file)
        sheet_names = xl_file.sheet_names
        print(f"\nFound {len(sheet_names)} sheets:")
        for i, sheet in enumerate(sheet_names):
            print(f"  {i+1}. {sheet}")
        
        # Analyze each sheet
        for sheet_name in sheet_names:
            print(f"\n{'='*60}")
            print(f"ANALYZING SHEET: {sheet_name}")
            print(f"{'='*60}")
            
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                print(f"Sheet dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
                
                # Look for tmaxfrac mentions
                tmaxfrac_found = False
                for row_idx in range(min(50, df.shape[0])):  # Check first 50 rows
                    for col_idx in range(df.shape[1]):
                        cell_value = str(df.iloc[row_idx, col_idx]).lower()
                        if 'tmaxfrac' in cell_value:
                            print(f"Found 'tmaxfrac' at row {row_idx+1}, col {col_idx+1}: {df.iloc[row_idx, col_idx]}")
                            tmaxfrac_found = True
                
                # Show first few rows to understand structure
                print(f"\nFirst 10 rows of data:")
                print(df.head(10).to_string())
                
                # Look for rule patterns
                print(f"\nLooking for rule patterns...")
                rule_keywords = ['rule', 'soa', 'limit', 'max', 'min', 'condition', 'level']
                for keyword in rule_keywords:
                    found_cells = []
                    for row_idx in range(min(100, df.shape[0])):
                        for col_idx in range(df.shape[1]):
                            cell_value = str(df.iloc[row_idx, col_idx]).lower()
                            if keyword in cell_value and len(cell_value) < 100:  # Avoid very long cells
                                found_cells.append((row_idx+1, col_idx+1, df.iloc[row_idx, col_idx]))
                    
                    if found_cells:
                        print(f"  Found '{keyword}' in {len(found_cells)} cells:")
                        for row, col, value in found_cells[:5]:  # Show first 5 matches
                            print(f"    Row {row}, Col {col}: {value}")
                        if len(found_cells) > 5:
                            print(f"    ... and {len(found_cells) - 5} more")
                
            except Exception as e:
                print(f"Error reading sheet {sheet_name}: {e}")
                
    except Exception as e:
        print(f"Error opening Excel file: {e}")

if __name__ == "__main__":
    analyze_excel_structure()