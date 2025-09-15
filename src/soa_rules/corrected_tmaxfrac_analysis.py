#!/usr/bin/env python3
"""
Corrected analysis of tmaxfrac parameter - Transient Time Fraction for SOA rules
"""

import json
from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType
from dataclasses import dataclass
from typing import Dict, List, Union, Optional

@dataclass
class TransientTimeLimit:
    """Represents a transient time-based SOA limit"""
    voltage_limit: Union[float, str]
    max_time_fraction: float  # tmaxfrac value
    description: str
    
    def is_violation(self, applied_voltage: float, time_duration: float, total_transient_time: float) -> bool:
        """Check if applied conditions violate the SOA rule"""
        
        # Check if voltage exceeds limit
        if isinstance(self.voltage_limit, str) and self.voltage_limit.lower() == "no-limit":
            return False
        
        try:
            voltage_limit_val = float(self.voltage_limit)
        except (ValueError, TypeError):
            return False
        
        # Check voltage violation
        voltage_violated = applied_voltage > voltage_limit_val
        
        if not voltage_violated:
            return False
        
        # If voltage is violated, check time constraint
        if self.max_time_fraction == 0.0:
            # tmaxfrac = 0: No time allowed at this voltage - immediate warning
            return True
        
        # Calculate maximum allowed time
        max_allowed_time = self.max_time_fraction * total_transient_time
        
        # Check if duration exceeds allowed time
        return time_duration > max_allowed_time

def analyze_corrected_tmaxfrac():
    """Analyze tmaxfrac with correct understanding - transient time fractions"""
    
    print("=== CORRECTED TMAXFRAC ANALYSIS ===")
    print("tmaxfrac = Transient Time Fraction for SOA Compliance")
    print("-" * 60)
    
    print("\nCORRECT INTERPRETATION:")
    print("• tmaxfrac = 0.1  → Allow voltage for max 10% of total transient time")
    print("• tmaxfrac = 0.01 → Allow voltage for max 1% of total transient time") 
    print("• tmaxfrac = 0.0  → NEVER allow this voltage (immediate warning)")
    print("• 'no-limit'      → No restriction on this voltage")
    
    # Example from the Excel data
    print("\nEXAMPLE: vhigh_ds_on for MOS transistor")
    print("tmaxfrac=0.1:  1.65V allowed for ≤10% of transient time")
    print("tmaxfrac=0.01: 1.71V allowed for ≤1% of transient time")
    print("tmaxfrac=0.0:  1.838V NEVER allowed (immediate warning)")
    
    print("\nTRANSIENT SIMULATION LOGIC:")
    print("1. Higher voltages → More restrictive time limits")
    print("2. tmaxfrac=0 voltages → Absolute prohibitions")
    print("3. Progressive voltage/time trade-offs")

def create_transient_aware_dsl():
    """Create DSL that properly handles transient time constraints"""
    
    print("\n=== TRANSIENT-AWARE SOA DSL ===")
    
    # Updated schema for transient time awareness
    transient_schema = {
        "soa_rules": {
            "version": "2.0",
            "technology": "smos10hv", 
            "description": "SOA rules with transient time fraction constraints",
            "global_config": {
                "transient_simulation": {
                    "enabled": True,
                    "method": "tmaxfrac",
                    "description": "Time fraction limits for transient voltage application"
                }
            },
            "devices": {
                "device_key": {
                    "device_type": "mos_transistor",
                    "subcategory": "symmetric_on_off",
                    "transient_limits": {
                        "enabled": True,
                        "tmaxfrac_levels": [0.1, 0.01, 0.0],
                        "description": "Progressive voltage limits with time fraction constraints"
                    },
                    "parameters": {
                        "parameter_name": {
                            "name": "vhigh_ds_on",
                            "severity": "high",
                            "type": "voltage",
                            "unit": "V",
                            "transient_constraints": [
                                {
                                    "voltage_limit": 1.65,
                                    "max_time_fraction": 0.1,
                                    "description": "1.65V allowed for max 10% of transient time"
                                },
                                {
                                    "voltage_limit": 1.71,
                                    "max_time_fraction": 0.01,
                                    "description": "1.71V allowed for max 1% of transient time"
                                },
                                {
                                    "voltage_limit": 1.838,
                                    "max_time_fraction": 0.0,
                                    "description": "1.838V NEVER allowed - immediate warning"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
    
    print("Updated JSON Schema for Transient Time Constraints:")
    print(json.dumps(transient_schema, indent=2))

def demonstrate_transient_validation():
    """Demonstrate transient time validation logic"""
    
    print("\n=== TRANSIENT VALIDATION EXAMPLES ===")
    
    # Create example transient limits for vhigh_ds_on
    limits = [
        TransientTimeLimit(1.65, 0.1, "1.65V for max 10% of time"),
        TransientTimeLimit(1.71, 0.01, "1.71V for max 1% of time"), 
        TransientTimeLimit(1.838, 0.0, "1.838V never allowed")
    ]
    
    # Test scenarios
    test_scenarios = [
        # (voltage, duration, total_time, description)
        (1.5, 50e-6, 100e-6, "1.5V for 50μs of 100μs transient"),
        (1.7, 5e-6, 100e-6, "1.7V for 5μs of 100μs transient (5%)"),
        (1.7, 15e-6, 100e-6, "1.7V for 15μs of 100μs transient (15%)"),
        (1.75, 0.5e-6, 100e-6, "1.75V for 0.5μs of 100μs transient (0.5%)"),
        (1.75, 2e-6, 100e-6, "1.75V for 2μs of 100μs transient (2%)"),
        (1.85, 0.1e-6, 100e-6, "1.85V for any duration (tmaxfrac=0)")
    ]
    
    print("Validation Results:")
    print("-" * 80)
    
    for voltage, duration, total_time, description in test_scenarios:
        print(f"\nScenario: {description}")
        print(f"  Applied: {voltage}V for {duration*1e6:.1f}μs of {total_time*1e6:.1f}μs total")
        
        violations = []
        applicable_limits = []
        
        for limit in limits:
            if isinstance(limit.voltage_limit, (int, float)) and voltage >= limit.voltage_limit:
                applicable_limits.append(limit)
                if limit.is_violation(voltage, duration, total_time):
                    violations.append(limit)
        
        if violations:
            print(f"  ❌ VIOLATION:")
            for violation in violations:
                if violation.max_time_fraction == 0.0:
                    print(f"    - {violation.voltage_limit}V NEVER allowed (tmaxfrac=0)")
                else:
                    max_time = violation.max_time_fraction * total_time * 1e6
                    print(f"    - {violation.voltage_limit}V exceeds {violation.max_time_fraction*100}% time limit ({max_time:.1f}μs)")
        else:
            print(f"  ✅ COMPLIANT")
            if applicable_limits:
                for limit in applicable_limits:
                    if limit.max_time_fraction > 0:
                        max_time = limit.max_time_fraction * total_time * 1e6
                        print(f"    - Within {limit.voltage_limit}V limit ({limit.max_time_fraction*100}% = {max_time:.1f}μs)")

def create_updated_python_dsl():
    """Create updated Python DSL classes for transient time constraints"""
    
    python_code = '''
# Updated SOA DSL for Transient Time Constraints
from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
from enum import Enum

@dataclass
class TransientConstraint:
    """Single transient time constraint for a voltage level"""
    voltage_limit: Union[float, str]  # Voltage threshold
    max_time_fraction: float          # tmaxfrac value (0.0 to 1.0)
    description: str = ""
    
    def validate_transient(self, applied_voltage: float, 
                          duration: float, total_time: float) -> Optional[str]:
        """Validate transient conditions against this constraint"""
        
        # Skip if voltage doesn't reach this limit
        if isinstance(self.voltage_limit, str):
            if self.voltage_limit.lower() == "no-limit":
                return None
            try:
                voltage_limit_val = float(self.voltage_limit)
            except:
                return None
        else:
            voltage_limit_val = self.voltage_limit
        
        if applied_voltage < voltage_limit_val:
            return None
        
        # Check time constraint
        if self.max_time_fraction == 0.0:
            return f"CRITICAL: {voltage_limit_val}V never allowed (tmaxfrac=0)"
        
        max_allowed_time = self.max_time_fraction * total_time
        if duration > max_allowed_time:
            return (f"Time violation: {voltage_limit_val}V applied for "
                   f"{duration*1e6:.1f}μs exceeds limit of "
                   f"{max_allowed_time*1e6:.1f}μs ({self.max_time_fraction*100}%)")
        
        return None

@dataclass 
class TransientAwareParameter:
    """SOA parameter with transient time constraints"""
    name: str
    severity: str
    param_type: str
    unit: str
    transient_constraints: List[TransientConstraint]
    description: str = ""
    
    def validate_transient_profile(self, voltage_profile: List[tuple]) -> List[str]:
        """
        Validate a complete voltage profile against transient constraints
        voltage_profile: List of (voltage, start_time, end_time) tuples
        """
        violations = []
        
        # Calculate total transient time
        if not voltage_profile:
            return violations
        
        total_time = max(end_time for _, _, end_time in voltage_profile)
        
        # Check each voltage application period
        for voltage, start_time, end_time in voltage_profile:
            duration = end_time - start_time
            
            # Check against all constraints
            for constraint in self.transient_constraints:
                violation = constraint.validate_transient(voltage, duration, total_time)
                if violation:
                    violations.append(f"{self.name}: {violation}")
        
        return violations

class TransientSOAEngine:
    """SOA engine with transient time validation capabilities"""
    
    def __init__(self):
        self.devices = {}
    
    def validate_transient_simulation(self, device_key: str, 
                                    parameter_profiles: Dict[str, List[tuple]]) -> Dict:
        """
        Validate complete transient simulation against SOA rules
        
        parameter_profiles: {
            "vhigh_ds_on": [(voltage1, t1_start, t1_end), (voltage2, t2_start, t2_end), ...],
            "vhigh_ds_off": [...],
            ...
        }
        """
        
        if device_key not in self.devices:
            return {"error": f"Device {device_key} not found"}
        
        device = self.devices[device_key]
        all_violations = []
        
        for param_name, voltage_profile in parameter_profiles.items():
            if param_name in device.parameters:
                param = device.parameters[param_name]
                violations = param.validate_transient_profile(voltage_profile)
                all_violations.extend(violations)
        
        return {
            "device": device_key,
            "violations": all_violations,
            "compliant": len(all_violations) == 0,
            "total_violations": len(all_violations)
        }

# Example usage:
def example_transient_validation():
    """Example of transient SOA validation"""
    
    # Create MOS transistor parameter with transient constraints
    vhigh_ds_on = TransientAwareParameter(
        name="vhigh_ds_on",
        severity="high",
        param_type="voltage", 
        unit="V",
        transient_constraints=[
            TransientConstraint(1.65, 0.1, "1.65V for max 10% of time"),
            TransientConstraint(1.71, 0.01, "1.71V for max 1% of time"),
            TransientConstraint(1.838, 0.0, "1.838V never allowed")
        ]
    )
    
    # Example voltage profile: (voltage, start_time, end_time)
    voltage_profile = [
        (1.2, 0, 50e-6),      # 1.2V for first 50μs
        (1.7, 50e-6, 55e-6),  # 1.7V for 5μs (5% of 100μs total)
        (1.0, 55e-6, 100e-6)  # 1.0V for remaining time
    ]
    
    violations = vhigh_ds_on.validate_transient_profile(voltage_profile)
    
    if violations:
        print("Transient violations found:")
        for violation in violations:
            print(f"  - {violation}")
    else:
        print("Transient profile compliant with SOA rules")

'''
    
    print("\n=== UPDATED PYTHON DSL ===")
    print("Transient-aware SOA validation classes:")
    print(python_code)

def main():
    """Main function demonstrating corrected tmaxfrac understanding"""
    
    analyze_corrected_tmaxfrac()
    create_transient_aware_dsl()
    demonstrate_transient_validation()
    create_updated_python_dsl()
    
    print("\n" + "="*80)
    print("✅ CORRECTED UNDERSTANDING IMPLEMENTED")
    print("="*80)
    print("\nKEY CORRECTIONS:")
    print("• tmaxfrac is NOT temperature-related")
    print("• tmaxfrac defines maximum time fraction for voltage application")
    print("• tmaxfrac=0 means voltage is NEVER allowed (immediate warning)")
    print("• Higher voltages have more restrictive time limits")
    print("• This enables safe transient simulation with time-aware SOA checking")

if __name__ == "__main__":
    main()