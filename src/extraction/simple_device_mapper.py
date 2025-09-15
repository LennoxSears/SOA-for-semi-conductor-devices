#!/usr/bin/env python3
"""
Simple device mapper - Create clear device mapping from pattern analysis
"""

import json
from pathlib import Path

def create_device_mapping():
    """Create a simple, clear device mapping based on our pattern analysis"""
    
    print("=== CREATING SIMPLE DEVICE MAPPING ===")
    
    # Load the pattern mapping we generated
    if not Path("pattern_mapping.json").exists():
        print("❌ pattern_mapping.json not found. Run identify_all_patterns.py first.")
        return None
    
    with open("pattern_mapping.json", "r") as f:
        pattern_data = json.load(f)
    
    # Create a simple mapping of sheet -> device types -> tmaxfrac sections
    device_mapping = {
        "technology": "smos10hv",
        "version": "2.0",
        "description": "Simple device mapping for complete SOA extraction",
        "sheets": {}
    }
    
    # Define clear device mapping for each sheet
    sheet_device_mapping = {
        "10HV SOA SYM ON-OFF": {
            "devices": [
                {
                    "name": "NMOS Core",
                    "type": "mos_transistor",
                    "category": "core", 
                    "subcategory": "nmos",
                    "tmaxfrac_row": 5,
                    "description": "core nmos, nmos_LL, nmos_ULL"
                },
                {
                    "name": "PMOS Core", 
                    "type": "mos_transistor",
                    "category": "core",
                    "subcategory": "pmos", 
                    "tmaxfrac_row": 21,
                    "description": "core pmos, pmos_LL, pmos_ULL"
                },
                {
                    "name": "NMOS 5V",
                    "type": "mos_transistor", 
                    "category": "5v",
                    "subcategory": "nmos",
                    "tmaxfrac_row": 37,
                    "description": "nmos5"
                },
                {
                    "name": "PMOS 5V",
                    "type": "mos_transistor",
                    "category": "5v", 
                    "subcategory": "pmos",
                    "tmaxfrac_row": 53,
                    "description": "pmos5"
                }
            ]
        },
        
        "10HV SOA CAPS": {
            "devices": [
                {
                    "name": "All Capacitors",
                    "type": "capacitor",
                    "category": "general",
                    "subcategory": "all_types",
                    "tmaxfrac_row": 5,
                    "description": "CGLV, CGHV, CGHVF, CGHVm13, CDP, CDPF, CDPFm13, CFRLV, CFRLVm13, CFR45, CFR45m13, CFR90, CFR90m13, CFR120, CFR120m13"
                }
            ]
        },
        
        "10HV SOA SUB Well ": {
            "devices": [
                {
                    "name": "Substrate Well",
                    "type": "substrate",
                    "category": "well",
                    "subcategory": "isolation",
                    "tmaxfrac_row": 7,
                    "description": "100V/70V substrate rules for all sym devices, caps, diodes"
                }
            ]
        },
        
        "10HV SOA OXRisk Drift ": {
            "devices": [
                {
                    "name": "Oxide Reliability",
                    "type": "oxide",
                    "category": "reliability",
                    "subcategory": "drift",
                    "tmaxfrac_row": 6,
                    "description": "OxideRisk for design: sym devices, gate caps, CDP"
                }
            ]
        },
        
        "10HV SOA SUB Well HV ": {
            "devices": [
                {
                    "name": "Substrate HV",
                    "type": "substrate",
                    "category": "well",
                    "subcategory": "high_voltage",
                    "tmaxfrac_row": 7,
                    "description": "100V/40V substrate rules"
                },
                {
                    "name": "Substrate HV Additional",
                    "type": "substrate", 
                    "category": "well",
                    "subcategory": "high_voltage_additional",
                    "tmaxfrac_row": 66,
                    "description": "Additional HV substrate rules"
                }
            ]
        },
        
        "10HV Diodes FWD-REV": {
            "devices": [
                {
                    "name": "Diodes",
                    "type": "diode",
                    "category": "general",
                    "subcategory": "forward_reverse",
                    "tmaxfrac_row": 5,
                    "description": "Diode REV and FWD limits"
                }
            ]
        },
        
        "10HV BJT REV ": {
            "devices": [
                {
                    "name": "BJT NPN",
                    "type": "bjt",
                    "category": "npn",
                    "subcategory": "general",
                    "tmaxfrac_row": 5,
                    "description": "npn_b"
                },
                {
                    "name": "BJT PNP",
                    "type": "bjt",
                    "category": "pnp", 
                    "subcategory": "general",
                    "tmaxfrac_row": 17,
                    "description": "pnp, pnp_iso"
                },
                {
                    "name": "BJT PNP ISO",
                    "type": "bjt",
                    "category": "pnp",
                    "subcategory": "isolated",
                    "tmaxfrac_row": 28,
                    "description": "pnp_iso special limits"
                }
            ]
        }
    }
    
    # Add the mapping to our device_mapping
    device_mapping["sheets"] = sheet_device_mapping
    
    # Calculate totals
    total_devices = 0
    total_tmaxfrac_sections = 0
    
    for sheet_name, sheet_info in sheet_device_mapping.items():
        device_count = len(sheet_info["devices"])
        total_devices += device_count
        total_tmaxfrac_sections += device_count  # Each device has one tmaxfrac section
        
        print(f"\n{sheet_name}:")
        print(f"  Devices: {device_count}")
        for device in sheet_info["devices"]:
            print(f"    - {device['name']} ({device['type']}) at row {device['tmaxfrac_row']}")
    
    device_mapping["summary"] = {
        "total_sheets": len(sheet_device_mapping),
        "total_devices": total_devices,
        "total_tmaxfrac_sections": total_tmaxfrac_sections
    }
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total sheets with devices: {len(sheet_device_mapping)}")
    print(f"  Total devices: {total_devices}")
    print(f"  Total tmaxfrac sections: {total_tmaxfrac_sections}")
    
    # Save the mapping
    with open("simple_device_mapping.json", "w") as f:
        json.dump(device_mapping, f, indent=2)
    
    print(f"\n✅ Simple device mapping saved to simple_device_mapping.json")
    
    return device_mapping

def validate_mapping():
    """Validate the mapping against our pattern analysis"""
    
    print(f"\n=== VALIDATING MAPPING ===")
    
    # Load both files
    if not Path("pattern_mapping.json").exists() or not Path("simple_device_mapping.json").exists():
        print("❌ Required files not found")
        return
    
    with open("pattern_mapping.json", "r") as f:
        pattern_data = json.load(f)
    
    with open("simple_device_mapping.json", "r") as f:
        device_mapping = json.load(f)
    
    # Compare tmaxfrac sections
    pattern_tmaxfrac = pattern_data["summary"]["total_tmaxfrac_sections"]
    mapping_tmaxfrac = device_mapping["summary"]["total_tmaxfrac_sections"]
    
    print(f"tmaxfrac sections in pattern analysis: {pattern_tmaxfrac}")
    print(f"tmaxfrac sections in device mapping: {mapping_tmaxfrac}")
    print(f"Coverage: {(mapping_tmaxfrac/pattern_tmaxfrac)*100:.1f}%")
    
    # Check each sheet
    print(f"\nSheet-by-sheet validation:")
    for sheet_name in device_mapping["sheets"]:
        if sheet_name in pattern_data["sheets"]:
            pattern_sections = pattern_data["sheets"][sheet_name]["tmaxfrac_sections"]
            mapping_sections = len(device_mapping["sheets"][sheet_name]["devices"])
            status = "✅" if pattern_sections == mapping_sections else "⚠️"
            print(f"  {sheet_name}: {mapping_sections}/{pattern_sections} {status}")
        else:
            print(f"  {sheet_name}: Not in pattern data ❌")

def main():
    """Main function"""
    device_mapping = create_device_mapping()
    if device_mapping:
        validate_mapping()
    return device_mapping

if __name__ == "__main__":
    main()