#!/usr/bin/env python3
"""
Comprehensive demonstration of SOA DSL capabilities
Shows all features: loading, validation, manipulation, and reporting
"""

import json
from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType
from soa_rules import load_soa_rules

def demo_basic_usage():
    """Demonstrate basic SOA DSL usage"""
    
    print("=== BASIC SOA DSL USAGE ===")
    
    # Load the converted rules
    soa = load_soa_rules()
    
    print(f"Loaded {len(soa.devices)} device types:")
    for device_key, device in soa.devices.items():
        print(f"  - {device_key}: {len(device.parameters)} parameters")
    
    # Basic validation example
    print("\n--- Basic Validation Example ---")
    
    result = soa.check_soa_compliance(
        "mos_transistor_symmetric_on_off",
        tmaxfrac=0.1,
        vhigh_ds_on=1.5,    # Within limit (1.65V)
        vhigh_ds_off=1.7,   # Within limit (1.815V)
        vhigh_gc=1.6        # Within limit (1.65V)
    )
    
    print(f"Test 1 - Conservative values:")
    print(f"  Compliant: {result['compliant']}")
    print(f"  Violations: {result['violations']}")
    
    # Test with violation
    result = soa.check_soa_compliance(
        "mos_transistor_symmetric_on_off",
        tmaxfrac=0.1,
        vhigh_ds_on=2.0,    # Exceeds limit (1.65V)
        vhigh_ds_off=1.7
    )
    
    print(f"\nTest 2 - Violation case:")
    print(f"  Compliant: {result['compliant']}")
    print(f"  Violations: {result['violations']}")

def demo_multi_level_scaling():
    """Demonstrate multi-level tmaxfrac scaling"""
    
    print("\n=== MULTI-LEVEL TMAXFRAC SCALING ===")
    
    soa = load_soa_rules()
    
    # Test same conditions at different tmaxfrac levels
    test_conditions = {
        'vhigh_ds_on': 1.8,
        'vhigh_ds_off': 2.5,
        'vhigh_gc': 2.0
    }
    
    print("Testing same conditions at different tmaxfrac levels:")
    print(f"Test conditions: {test_conditions}")
    
    for tmaxfrac in [0.1, 0.01, 0.0]:
        result = soa.check_soa_compliance(
            "mos_transistor_symmetric_on_off",
            tmaxfrac=tmaxfrac,
            **test_conditions
        )
        
        status = "✅ PASS" if result['compliant'] else "❌ FAIL"
        print(f"\ntmaxfrac = {tmaxfrac}: {status}")
        
        if result['violations']:
            for violation in result['violations']:
                print(f"  - {violation}")
        
        # Show limits at this tmaxfrac level
        limits = result['limits']
        print(f"  Limits at tmaxfrac={tmaxfrac}:")
        for param, limit_info in limits.items():
            if param in test_conditions:
                print(f"    {param}: {limit_info['value']} {limit_info['unit']} (test: {test_conditions[param]})")

def demo_parameter_analysis():
    """Demonstrate parameter analysis capabilities"""
    
    print("\n=== PARAMETER ANALYSIS ===")
    
    soa = load_soa_rules()
    device = soa.devices["mos_transistor_symmetric_on_off"]
    
    print("MOS Transistor Parameters Analysis:")
    print("-" * 50)
    
    for param_name, param in device.parameters.items():
        print(f"\n{param_name}:")
        print(f"  Type: {param.param_type.value}")
        print(f"  Unit: {param.unit}")
        print(f"  Severity: {param.severity.value}")
        print(f"  Multi-level values:")
        
        for tmaxfrac, value in param.values.items():
            print(f"    tmaxfrac={tmaxfrac}: {value}")
        
        # Show scaling factor
        if len(param.values) > 1:
            values = list(param.values.values())
            if all(isinstance(v, (int, float)) for v in values):
                min_val = min(values)
                max_val = max(values)
                scaling = max_val / min_val if min_val != 0 else "N/A"
                print(f"  Scaling factor: {scaling:.2f}x" if isinstance(scaling, float) else f"  Scaling factor: {scaling}")

def demo_batch_validation():
    """Demonstrate batch validation capabilities"""
    
    print("\n=== BATCH VALIDATION ===")
    
    soa = load_soa_rules()
    
    # Create multiple test scenarios
    test_scenarios = [
        # Conservative scenarios (should pass)
        {'tmaxfrac': 0.1, 'vhigh_ds_on': 1.5, 'vhigh_ds_off': 1.7, 'scenario': 'Conservative'},
        {'tmaxfrac': 0.01, 'vhigh_ds_on': 1.6, 'vhigh_ds_off': 1.8, 'scenario': 'Moderate'},
        {'tmaxfrac': 0.0, 'vhigh_ds_on': 1.7, 'vhigh_ds_off': 2.8, 'scenario': 'Aggressive'},
        
        # Violation scenarios
        {'tmaxfrac': 0.1, 'vhigh_ds_on': 2.0, 'vhigh_ds_off': 1.7, 'scenario': 'Violation 1'},
        {'tmaxfrac': 0.01, 'vhigh_ds_on': 1.5, 'vhigh_ds_off': 2.5, 'scenario': 'Violation 2'},
    ]
    
    # Remove scenario labels for validation
    validation_scenarios = []
    for scenario in test_scenarios:
        val_scenario = {k: v for k, v in scenario.items() if k != 'scenario'}
        validation_scenarios.append(val_scenario)
    
    # Generate validation report
    report = soa.generate_validation_report(
        "mos_transistor_symmetric_on_off",
        validation_scenarios
    )
    
    print("Batch Validation Report:")
    print(f"Total scenarios: {report['summary']['total_scenarios']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    
    print("\nDetailed Results:")
    for i, result in enumerate(report['results']):
        scenario_name = test_scenarios[i]['scenario']
        status = "✅ PASS" if result['compliant'] else "❌ FAIL"
        print(f"\n{scenario_name}: {status}")
        print(f"  tmaxfrac: {result['tmaxfrac']}")
        print(f"  Values: {result['test_values']}")
        
        if result['violations']:
            print(f"  Violations:")
            for violation in result['violations']:
                print(f"    - {violation}")

def demo_capacitor_rules():
    """Demonstrate capacitor rule validation"""
    
    print("\n=== CAPACITOR RULES VALIDATION ===")
    
    soa = load_soa_rules()
    
    if "capacitor_general" not in soa.devices:
        print("Capacitor rules not found in loaded devices")
        return
    
    device = soa.devices["capacitor_general"]
    print(f"Capacitor device has {len(device.parameters)} parameters:")
    
    for param_name in device.parameters.keys():
        print(f"  - {param_name}")
    
    # Test capacitor validation
    test_scenarios = [
        {'tmaxfrac': 0.1, 'vhigh_tnw': 1.5, 'vlow_tnw': -1.5},
        {'tmaxfrac': 0.1, 'vhigh_tnw': 2.0, 'vlow_tnw': -1.5},  # Should violate
    ]
    
    for i, scenario in enumerate(test_scenarios):
        result = soa.check_soa_compliance("capacitor_general", **scenario)
        status = "✅ PASS" if result['compliant'] else "❌ FAIL"
        print(f"\nCapacitor Test {i+1}: {status}")
        print(f"  Conditions: {scenario}")
        if result['violations']:
            for violation in result['violations']:
                print(f"  - {violation}")

def demo_json_export_import():
    """Demonstrate JSON export and import capabilities"""
    
    print("\n=== JSON EXPORT/IMPORT ===")
    
    # Load original rules
    soa_original = load_soa_rules()
    
    # Export to JSON
    json_data = soa_original.export_to_json()
    
    print("Exported rules to JSON format")
    print(f"JSON structure keys: {list(json_data.keys())}")
    print(f"Devices in export: {list(json_data['soa_rules']['devices'].keys())}")
    
    # Create new engine and import
    soa_imported = SOARulesEngine()
    soa_imported.load_from_json(json_data)
    
    print(f"\nImported {len(soa_imported.devices)} devices")
    
    # Verify import worked by running same test
    result_original = soa_original.check_soa_compliance(
        "mos_transistor_symmetric_on_off",
        tmaxfrac=0.1,
        vhigh_ds_on=1.5
    )
    
    result_imported = soa_imported.check_soa_compliance(
        "mos_transistor_symmetric_on_off", 
        tmaxfrac=0.1,
        vhigh_ds_on=1.5
    )
    
    print(f"Original result compliant: {result_original['compliant']}")
    print(f"Imported result compliant: {result_imported['compliant']}")
    print(f"Results match: {result_original['compliant'] == result_imported['compliant']}")

def demo_advanced_features():
    """Demonstrate advanced DSL features"""
    
    print("\n=== ADVANCED FEATURES ===")
    
    soa = load_soa_rules()
    device = soa.devices["mos_transistor_symmetric_on_off"]
    
    # Demonstrate parameter value interpolation
    print("Parameter Value Interpolation:")
    param = device.parameters["vhigh_ds_on"]
    
    # Test interpolation at intermediate tmaxfrac value
    test_tmaxfrac = 0.05  # Between 0.01 and 0.1
    interpolated_value = param.get_value_at_tmaxfrac(test_tmaxfrac)
    
    print(f"Parameter: {param.name}")
    print(f"Defined values: {param.values}")
    print(f"Value at tmaxfrac={test_tmaxfrac}: {interpolated_value}")
    
    # Demonstrate no-limit handling
    print("\nNo-Limit Parameter Handling:")
    for param_name, param in device.parameters.items():
        for tmaxfrac, value in param.values.items():
            if param.is_no_limit(tmaxfrac):
                print(f"  {param_name} has no limit at tmaxfrac={tmaxfrac}")
    
    # Demonstrate parameter type analysis
    print("\nParameter Type Distribution:")
    type_counts = {}
    for param in device.parameters.values():
        param_type = param.param_type.value
        type_counts[param_type] = type_counts.get(param_type, 0) + 1
    
    for param_type, count in type_counts.items():
        print(f"  {param_type}: {count} parameters")

def main():
    """Run all demonstrations"""
    
    print("SOA DSL COMPREHENSIVE DEMONSTRATION")
    print("=" * 50)
    
    try:
        demo_basic_usage()
        demo_multi_level_scaling()
        demo_parameter_analysis()
        demo_batch_validation()
        demo_capacitor_rules()
        demo_json_export_import()
        demo_advanced_features()
        
        print("\n" + "=" * 50)
        print("✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("\nThe SOA DSL provides:")
        print("  ✅ Multi-level tmaxfrac scaling")
        print("  ✅ Comprehensive validation")
        print("  ✅ Batch processing capabilities")
        print("  ✅ JSON export/import")
        print("  ✅ Type-safe parameter handling")
        print("  ✅ Extensible architecture")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()