"# SOA Rules for Semiconductor Devices - SMOS10HV Technology

## Overview

This repository contains a comprehensive analysis and unified format for **Safe Operating Area (SOA) rules** for the SMOS10HV semiconductor technology. The project converts complex Excel-based SOA specifications into a structured, programmable format that enables automated rule manipulation and validation.

## Key Features

### 🔍 **Excel Analysis Results**
- **13 sheets** analyzed from the SMOS10HV specification
- **5 SOA rule sheets** identified and processed
- **Multi-level tmaxfrac transient time implementation** discovered and documented
- **Complex rule structures** mapped to unified format

### 🏗️ **Unified SOA Rule Format**
- **JSON-based DSL** for rule representation
- **Python implementation** with validation capabilities
- **Multi-level transient time scaling** support via tmaxfrac parameter
- **Automatic Excel-to-DSL conversion** tools

### 📊 **tmaxfrac Parameter Understanding**
The `tmaxfrac` parameter implements **transient time fraction limits** for SOA rules:
- **tmaxfrac = 0.1**: Allow voltage for maximum 10% of total transient simulation time
- **tmaxfrac = 0.01**: Allow voltage for maximum 1% of total transient simulation time  
- **tmaxfrac = 0.0**: **NEVER** allow this voltage (immediate warning/violation)
- **"no-limit"**: No time restriction on this voltage level

Each parameter has different voltage thresholds at each tmaxfrac level, providing **time-aware transient simulation safety**.

## Project Structure

```
SOA-for-semi-conductor-devices/
├── README.md                           # This documentation
├── SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025  2.xlsx  # Source Excel file
├── 
├── # Analysis Scripts
├── analyze_excel.py                    # Initial Excel structure analysis
├── detailed_analysis.py                # Deep dive into tmaxfrac patterns
├── precise_analysis.py                 # Precise rule extraction
├── 
├── # DSL Implementation
├── soa_dsl_implementation.py           # Core DSL classes and validation engine
├── excel_to_dsl_converter.py           # Excel-to-DSL conversion tool
├── 
├── # Generated Output Files
├── soa_rules.json                      # JSON format rules
├── soa_rules.yaml                      # YAML format rules
├── soa_rules.py                        # Python module with rules
├── conversion_log.txt                  # Conversion process log
└── 
└── # Development Environment
    └── .devcontainer/                  # Dev container configuration
        ├── Dockerfile
        └── devcontainer.json
```

## SOA Rules Analysis Summary

### Device Types Identified

1. **MOS Transistors** (`mos_transistor_symmetric_on_off`)
   - **10 parameters** with multi-level tmaxfrac support
   - Voltage limits for drain-source, gate-channel, gate-bulk
   - Forward/reverse junction limits
   - **tmaxfrac levels**: [0.1, 0.01, 0.0]

2. **Capacitors** (`capacitor_general`)
   - **4 parameters** with multi-level support
   - Terminal voltage limits (TNW, TB)
   - **tmaxfrac levels**: [0.1, 0.01, 0.0]

3. **Substrate/Well Devices**
   - Well isolation rules
   - HV substrate rules
   - Limited multi-level support

4. **Oxide Reliability**
   - Drift and reliability parameters
   - Single-level rules

### Multi-Level Rule Pattern

The Excel implements a sophisticated **transient time-aware rule system**:

```
Parameter Name    | tmaxfrac=0.1      | tmaxfrac=0.01     | tmaxfrac=0.0
------------------|-------------------|-------------------|------------------
vhigh_ds_on       | 1.65V (≤10% time) | 1.71V (≤1% time)  | 1.838V (NEVER)
vhigh_ds_off      | 1.815V (≤10% time)| 1.881V (≤1% time) | 3.0V (NEVER)
vhigh_gc          | 1.65V (≤10% time) | 1.969V (≤1% time) | 2.073V (NEVER)
```

**Pattern**: Higher voltages have more restrictive time limits. tmaxfrac=0 voltages trigger immediate warnings and are never allowed during transient simulation.

## Unified DSL Format

### JSON Schema

```json
{
  "soa_rules": {
    "version": "1.0",
    "technology": "smos10hv",
    "global_config": {
      "temperature_scaling": {
        "enabled": true,
        "method": "tmaxfrac"
      }
    },
    "devices": {
      "device_key": {
        "device_type": "mos_transistor",
        "subcategory": "symmetric_on_off",
        "multi_level": {
          "enabled": true,
          "tmaxfrac_levels": [0.1, 0.01, 0.0]
        },
        "parameters": {
          "parameter_name": {
            "name": "vhigh_ds_on",
            "severity": "high",
            "type": "voltage",
            "unit": "V",
            "values": {
              "multi_level": {
                "0.1": 1.65,
                "0.01": 1.71,
                "0.0": 1.838
              }
            },
            "description": "High voltage limit for drain-source (on state)"
          }
        }
      }
    }
  }
}
```

### Python DSL Classes

```python
from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter

# Load rules
soa = SOARulesEngine()
soa.load_from_json(json_data)

# Validate device conditions
result = soa.check_soa_compliance(
    device_key="mos_transistor_symmetric_on_off",
    tmaxfrac=0.1,
    vhigh_ds_on=1.5,  # Test value
    vhigh_ds_off=1.7
)

print(f"Compliant: {result['compliant']}")
print(f"Violations: {result['violations']}")
```

## Usage Examples

### 1. Load and Validate Rules

```python
from soa_rules import load_soa_rules

# Load all converted rules
soa_engine = load_soa_rules()

# Check compliance for NMOS transistor
result = soa_engine.check_soa_compliance(
    "mos_transistor_symmetric_on_off",
    tmaxfrac=0.1,
    vhigh_ds_on=1.5,
    vhigh_ds_off=1.7,
    vhigh_gc=1.6
)

if result['compliant']:
    print("✅ Device operates within SOA limits")
else:
    print("❌ SOA violations found:")
    for violation in result['violations']:
        print(f"  - {violation}")
```

### 2. Transient Time Validation

```python
# Validate transient voltage profile with time constraints
voltage_profile = [
    (1.2, 0, 50e-6),      # 1.2V for first 50μs
    (1.7, 50e-6, 55e-6),  # 1.7V for 5μs (5% of 100μs total)
    (1.0, 55e-6, 100e-6)  # 1.0V for remaining time
]

# Check if 1.7V for 5μs violates tmaxfrac limits
# 1.65V limit: 5μs < 10μs (10% of 100μs) ✅ OK
# 1.71V limit: 1.7V < 1.71V ✅ OK
result = validate_transient_profile("vhigh_ds_on", voltage_profile)
```

### 3. Batch Validation

```python
# Validate multiple scenarios
test_scenarios = [
    {'tmaxfrac': 0.1, 'vhigh_ds_on': 1.5, 'vhigh_ds_off': 1.7},
    {'tmaxfrac': 0.1, 'vhigh_ds_on': 2.0, 'vhigh_ds_off': 1.7},
    {'tmaxfrac': 0.0, 'vhigh_ds_on': 1.5, 'vhigh_ds_off': 2.5}
]

report = soa_engine.generate_validation_report(
    "mos_transistor_symmetric_on_off", 
    test_scenarios
)

print(f"Passed: {report['summary']['passed']}")
print(f"Failed: {report['summary']['failed']}")
```

## Key Insights from Excel Analysis

### 1. **tmaxfrac Implementation**
- **Multi-level time constraints**: Each parameter has 3 voltage thresholds with different time fraction limits
- **Transient simulation safety**: Lower tmaxfrac = more restrictive time limits for higher voltages
- **Progressive restrictions**: tmaxfrac=0.1 (10% time) → tmaxfrac=0.01 (1% time) → tmaxfrac=0.0 (never allowed)

### 2. **Complex Rule Patterns**
- **"no-limit" values**: Some parameters have no restrictions at certain tmaxfrac levels
- **Asymmetric limits**: Different high/low limits for bidirectional parameters
- **Device-specific scaling**: Different devices use different tmaxfrac implementations

### 3. **Rule Categories**
- **Voltage limits**: Most common, with high/low variants
- **Junction limits**: Forward/reverse bias restrictions
- **Transient time scaling**: All major parameters support time-fraction-based limits

## Future Enhancements

### 1. **Extended DSL Features**
- **Conditional rules**: Rules that depend on other parameter values
- **Time-dependent limits**: Rules that vary with operation duration
- **Process corner support**: Rules that adapt to manufacturing variations

### 2. **Integration Capabilities**
- **SPICE integration**: Automatic SOA checking in circuit simulation
- **Design rule checking**: Integration with EDA tools
- **Real-time monitoring**: SOA validation in test equipment

### 3. **Advanced Validation**
- **Monte Carlo analysis**: Statistical SOA compliance checking
- **Worst-case analysis**: Automatic corner case generation
- **Optimization support**: Parameter tuning within SOA constraints

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install pandas openpyxl pyyaml jsonschema
   ```

2. **Convert Excel to DSL**:
   ```bash
   python excel_to_dsl_converter.py
   ```

3. **Use Generated Rules**:
   ```python
   from soa_rules import load_soa_rules
   soa = load_soa_rules()
   # Start validating your designs!
   ```

## Technology Stack

- **Python 3.12+**: Core implementation language
- **pandas**: Excel file processing
- **openpyxl**: Excel file reading
- **jsonschema**: Rule validation
- **dataclasses**: Type-safe rule definitions
- **enum**: Structured parameter types

## Contributing

This project provides a foundation for SOA rule management in semiconductor design. The unified format enables:

- **Automated validation** of device operating conditions
- **Integration** with design and simulation tools
- **Version control** of SOA rule changes
- **Collaborative development** of rule sets

The DSL is designed to be **extensible** and **technology-agnostic**, making it suitable for other semiconductor technologies beyond SMOS10HV." 
