#!/usr/bin/env python3
"""
Complete SOA DSL Implementation with validation and manipulation capabilities
"""

import json
import yaml
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Union, Optional, Any
from enum import Enum
import re

class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ParameterType(Enum):
    VOLTAGE = "voltage"
    CURRENT = "current"
    TEMPERATURE = "temperature"
    GENERAL = "general"

class ComparisonOperator(Enum):
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    EQUAL = "=="
    NOT_EQUAL = "!="

@dataclass
class Condition:
    """Represents a condition for rule application"""
    parameter: str
    operator: ComparisonOperator
    value: Union[float, str]
    description: str = ""

@dataclass
class SOAParameter:
    """Represents a single SOA parameter with multi-level support"""
    name: str
    severity: Severity
    param_type: ParameterType
    unit: str
    values: Dict[float, Union[float, str]]  # tmaxfrac -> value mapping
    conditions: List[Condition] = field(default_factory=list)
    description: str = ""
    
    def get_value_at_tmaxfrac(self, tmaxfrac: float) -> Union[float, str, None]:
        """Get parameter value at specific tmaxfrac level"""
        if tmaxfrac in self.values:
            return self.values[tmaxfrac]
        
        # Find closest tmaxfrac level
        if self.values:
            closest = min(self.values.keys(), key=lambda x: abs(x - tmaxfrac))
            return self.values[closest]
        return None
    
    def is_no_limit(self, tmaxfrac: float) -> bool:
        """Check if parameter has no limit at given tmaxfrac"""
        value = self.get_value_at_tmaxfrac(tmaxfrac)
        return str(value).lower() == "no-limit"
    
    def validate_value(self, test_value: float, tmaxfrac: float) -> bool:
        """Validate a test value against the parameter limit"""
        limit = self.get_value_at_tmaxfrac(tmaxfrac)
        
        if self.is_no_limit(tmaxfrac):
            return True
        
        try:
            limit_val = float(limit)
            # Determine comparison based on parameter name
            if "high" in self.name.lower() or "max" in self.name.lower():
                return test_value <= limit_val
            elif "low" in self.name.lower() or "min" in self.name.lower():
                return test_value >= limit_val
            else:
                # Default to upper limit
                return test_value <= limit_val
        except (ValueError, TypeError):
            return True  # Can't validate non-numeric limits

@dataclass
class DeviceRules:
    """Represents SOA rules for a specific device type"""
    device_type: str
    subcategory: str
    tmaxfrac_levels: List[float]
    parameters: Dict[str, SOAParameter]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate_conditions(self, tmaxfrac: float, **test_values) -> List[str]:
        """Validate device conditions against SOA rules"""
        violations = []
        
        for param_name, param in self.parameters.items():
            if param_name in test_values:
                test_val = test_values[param_name]
                if not param.validate_value(test_val, tmaxfrac):
                    limit = param.get_value_at_tmaxfrac(tmaxfrac)
                    violations.append(
                        f"{param_name}: {test_val} violates {param.severity.value} "
                        f"limit of {limit} {param.unit} at tmaxfrac={tmaxfrac}"
                    )
        
        return violations
    
    def get_parameter_limits(self, tmaxfrac: float) -> Dict[str, Dict[str, Any]]:
        """Get all parameter limits at specific tmaxfrac level"""
        limits = {}
        for param_name, param in self.parameters.items():
            limits[param_name] = {
                'value': param.get_value_at_tmaxfrac(tmaxfrac),
                'unit': param.unit,
                'severity': param.severity.value,
                'type': param.param_type.value,
                'no_limit': param.is_no_limit(tmaxfrac)
            }
        return limits

class SOARulesEngine:
    """Main engine for SOA rules management and validation"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceRules] = {}
        self.global_config = {
            'version': '1.0',
            'technology': 'smos10hv',
            'temperature_scaling': {
                'enabled': True,
                'method': 'tmaxfrac'
            }
        }
    
    def add_device(self, device_key: str, rules: DeviceRules):
        """Add device rules to the engine"""
        self.devices[device_key] = rules
    
    def load_from_json(self, json_data: Dict[str, Any]):
        """Load SOA rules from JSON format"""
        if 'soa_rules' in json_data:
            rules_data = json_data['soa_rules']
            
            # Load global config
            if 'global_config' in rules_data:
                self.global_config.update(rules_data['global_config'])
            
            # Load device rules
            if 'devices' in rules_data:
                for device_key, device_data in rules_data['devices'].items():
                    self._load_device_from_dict(device_key, device_data)
    
    def _load_device_from_dict(self, device_key: str, device_data: Dict[str, Any]):
        """Load a single device from dictionary data"""
        parameters = {}
        
        if 'parameters' in device_data:
            for param_name, param_data in device_data['parameters'].items():
                # Convert values to proper format
                values = {}
                if 'values' in param_data and 'multi_level' in param_data['values']:
                    ml_values = param_data['values']['multi_level']
                    if isinstance(ml_values, dict):
                        values = {float(k): v for k, v in ml_values.items()}
                
                parameters[param_name] = SOAParameter(
                    name=param_data.get('name', param_name),
                    severity=Severity(param_data.get('severity', 'high')),
                    param_type=ParameterType(param_data.get('type', 'general')),
                    unit=param_data.get('unit', ''),
                    values=values,
                    description=param_data.get('description', '')
                )
        
        device_rules = DeviceRules(
            device_type=device_data.get('device_type', 'unknown'),
            subcategory=device_data.get('subcategory', 'general'),
            tmaxfrac_levels=device_data.get('multi_level', {}).get('tmaxfrac_levels', []),
            parameters=parameters,
            metadata=device_data.get('metadata', {})
        )
        
        self.add_device(device_key, device_rules)
    
    def check_soa_compliance(self, device_key: str, tmaxfrac: float, **test_values) -> Dict[str, Any]:
        """Check SOA compliance for specific device and conditions"""
        if device_key not in self.devices:
            return {'error': f'Device {device_key} not found'}
        
        device_rules = self.devices[device_key]
        violations = device_rules.validate_conditions(tmaxfrac, **test_values)
        
        return {
            'device': device_key,
            'tmaxfrac': tmaxfrac,
            'test_values': test_values,
            'violations': violations,
            'compliant': len(violations) == 0,
            'limits': device_rules.get_parameter_limits(tmaxfrac)
        }
    
    def export_to_json(self) -> Dict[str, Any]:
        """Export all rules to JSON format"""
        devices_data = {}
        
        for device_key, device_rules in self.devices.items():
            device_data = {
                'device_type': device_rules.device_type,
                'subcategory': device_rules.subcategory,
                'multi_level': {
                    'enabled': len(device_rules.tmaxfrac_levels) > 1,
                    'tmaxfrac_levels': device_rules.tmaxfrac_levels
                },
                'parameters': {}
            }
            
            for param_name, param in device_rules.parameters.items():
                device_data['parameters'][param_name] = {
                    'name': param.name,
                    'severity': param.severity.value,
                    'type': param.param_type.value,
                    'unit': param.unit,
                    'values': {
                        'multi_level': {str(k): v for k, v in param.values.items()}
                    },
                    'description': param.description
                }
            
            devices_data[device_key] = device_data
        
        return {
            'soa_rules': {
                'version': self.global_config['version'],
                'technology': self.global_config['technology'],
                'global_config': self.global_config,
                'devices': devices_data
            }
        }
    
    def generate_validation_report(self, device_key: str, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive validation report for multiple scenarios"""
        if device_key not in self.devices:
            return {'error': f'Device {device_key} not found'}
        
        results = []
        summary = {'total_scenarios': len(test_scenarios), 'passed': 0, 'failed': 0}
        
        for i, scenario in enumerate(test_scenarios):
            tmaxfrac = scenario.get('tmaxfrac', 0.1)
            test_values = {k: v for k, v in scenario.items() if k != 'tmaxfrac'}
            
            result = self.check_soa_compliance(device_key, tmaxfrac, **test_values)
            result['scenario_id'] = i
            results.append(result)
            
            if result['compliant']:
                summary['passed'] += 1
            else:
                summary['failed'] += 1
        
        return {
            'device': device_key,
            'summary': summary,
            'results': results
        }

# Example usage and demonstration
def demonstrate_soa_dsl():
    """Demonstrate the SOA DSL capabilities"""
    
    print("=== SOA DSL DEMONSTRATION ===")
    
    # Create SOA engine
    soa = SOARulesEngine()
    
    # Example: Create MOS transistor rules
    mos_params = {
        'vhigh_ds_on': SOAParameter(
            name='vhigh_ds_on',
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit='V',
            values={0.1: 1.65, 0.01: 1.71, 0.0: 1.838},
            description='High voltage limit for drain-source (on state)'
        ),
        'vhigh_ds_off': SOAParameter(
            name='vhigh_ds_off',
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit='V',
            values={0.1: 1.815, 0.01: 1.881, 0.0: 3.0},
            description='High voltage limit for drain-source (off state)'
        )
    }
    
    mos_rules = DeviceRules(
        device_type='mos_transistor',
        subcategory='symmetric_on_off',
        tmaxfrac_levels=[0.1, 0.01, 0.0],
        parameters=mos_params
    )
    
    soa.add_device('nmos_core', mos_rules)
    
    # Test scenarios
    test_scenarios = [
        {'tmaxfrac': 0.1, 'vhigh_ds_on': 1.5, 'vhigh_ds_off': 1.7},  # Should pass
        {'tmaxfrac': 0.1, 'vhigh_ds_on': 2.0, 'vhigh_ds_off': 1.7},  # Should fail
        {'tmaxfrac': 0.0, 'vhigh_ds_on': 1.5, 'vhigh_ds_off': 2.5},  # Should pass at tmaxfrac=0
    ]
    
    # Generate validation report
    report = soa.generate_validation_report('nmos_core', test_scenarios)
    
    print("Validation Report:")
    print(f"Device: {report['device']}")
    print(f"Summary: {report['summary']}")
    
    for result in report['results']:
        print(f"\nScenario {result['scenario_id']}:")
        print(f"  tmaxfrac: {result['tmaxfrac']}")
        print(f"  Test values: {result['test_values']}")
        print(f"  Compliant: {result['compliant']}")
        if result['violations']:
            print(f"  Violations: {result['violations']}")
    
    # Export to JSON
    json_export = soa.export_to_json()
    print(f"\nJSON Export (first 500 chars):")
    print(json.dumps(json_export, indent=2)[:500] + "...")

if __name__ == "__main__":
    demonstrate_soa_dsl()