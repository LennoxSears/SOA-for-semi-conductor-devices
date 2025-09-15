#!/usr/bin/env python3
"""
Basic DSL usage example for SOA rules
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

def demonstrate_dsl_loading():
    """Demonstrate loading SOA rules from JSON"""
    
    print("🔧 DSL Loading Example")
    print("=" * 40)
    
    # Load final results
    results_file = Path(__file__).parent.parent.parent / "data" / "results" / "final_soa_device_rules.json"
    
    if not results_file.exists():
        print("❌ Results file not found. Run extraction first.")
        return
    
    with open(results_file, 'r') as f:
        soa_data = json.load(f)
    
    print(f"✅ Loaded SOA rules")
    print(f"   Version: {soa_data['soa_device_rules']['version']}")
    print(f"   Technology: {soa_data['soa_device_rules']['technology']}")
    print(f"   Total devices: {soa_data['soa_device_rules']['extraction_info']['total_devices']}")
    print(f"   Total parameters: {soa_data['soa_device_rules']['extraction_info']['total_parameters']}")
    
    return soa_data

def demonstrate_device_exploration(soa_data):
    """Demonstrate exploring device types and parameters"""
    
    print("\n🔍 Device Exploration Example")
    print("=" * 40)
    
    devices = soa_data['soa_device_rules']['devices']
    
    print(f"📋 Available devices ({len(devices)}):")
    for device_key, device_data in list(devices.items())[:5]:  # Show first 5
        device_info = device_data['device_info']
        param_count = device_data['parameter_count']
        has_tmaxfrac = device_data['tmaxfrac_info']['has_tmaxfrac']
        
        tmaxfrac_marker = "🕒" if has_tmaxfrac else "📊"
        print(f"   {tmaxfrac_marker} {device_info['name']} ({device_info['type']})")
        print(f"      Parameters: {param_count}")
        if has_tmaxfrac:
            levels = device_data['tmaxfrac_info']['levels']
            print(f"      tmaxfrac levels: {levels}")
        print()

def demonstrate_parameter_validation(soa_data):
    """Demonstrate parameter validation"""
    
    print("✅ Parameter Validation Example")
    print("=" * 40)
    
    # Get first device with parameters
    devices = soa_data['soa_device_rules']['devices']
    device_key = list(devices.keys())[0]
    device_data = devices[device_key]
    
    print(f"📋 Validating device: {device_data['device_info']['name']}")
    
    # Show first few parameters
    parameters = device_data['parameters'][:3]
    
    for param in parameters:
        print(f"\n🔸 Parameter: {param['name']}")
        print(f"   Severity: {param['severity']}")
        print(f"   Constraints: {param['constraints']}")
        
        if param.get('tmaxfrac_constraints'):
            print(f"   tmaxfrac: {param['tmaxfrac_constraints']}")

def demonstrate_rule_types(soa_data):
    """Demonstrate different rule types"""
    
    print("\n📊 Rule Types Example")
    print("=" * 40)
    
    rule_types = {
        'simple_numeric': 0,
        'equations': 0,
        'tmaxfrac': 0,
        'multi_constraint': 0
    }
    
    devices = soa_data['soa_device_rules']['devices']
    
    for device_data in devices.values():
        for param in device_data['parameters']:
            constraints = param['constraints']
            
            # Count constraint types
            if len(constraints) == 1 and any(isinstance(v, (int, float)) for v in constraints.values()):
                rule_types['simple_numeric'] += 1
            elif any('(' in str(v) or '+' in str(v) or '-' in str(v) for v in constraints.values()):
                rule_types['equations'] += 1
            elif param.get('tmaxfrac_constraints'):
                rule_types['tmaxfrac'] += 1
            elif len(constraints) > 1:
                rule_types['multi_constraint'] += 1
    
    print("📈 Rule type distribution:")
    for rule_type, count in rule_types.items():
        print(f"   • {rule_type.replace('_', ' ').title()}: {count}")

def main():
    """Main demonstration function"""
    
    print("🎯 SOA DSL Basic Usage Examples")
    print("=" * 60)
    
    # Load SOA data
    soa_data = demonstrate_dsl_loading()
    if not soa_data:
        return
    
    # Demonstrate various capabilities
    demonstrate_device_exploration(soa_data)
    demonstrate_parameter_validation(soa_data)
    demonstrate_rule_types(soa_data)
    
    print("\n✅ DSL demonstration complete!")
    print("\nNext steps:")
    print("   • Explore src/dsl/soa_dsl_implementation.py for full DSL engine")
    print("   • Check data/results/ for complete extracted data")
    print("   • Review docs/proposal/ for business case and architecture")

if __name__ == "__main__":
    main()