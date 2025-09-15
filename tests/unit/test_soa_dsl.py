"""
Tests for SOA DSL implementation
"""

import pytest
from soa_rules import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType


def test_soa_parameter_creation():
    """Test SOAParameter creation and basic functionality"""
    param = SOAParameter(
        name="vhigh_ds_on",
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: 1.65, 0.01: 1.71, 0.0: 1.838},
        description="High voltage limit for drain-source (on state)"
    )
    
    assert param.name == "vhigh_ds_on"
    assert param.severity == Severity.HIGH
    assert param.param_type == ParameterType.VOLTAGE
    assert param.unit == "V"
    assert param.get_value_at_tmaxfrac(0.1) == 1.65
    assert param.get_value_at_tmaxfrac(0.01) == 1.71
    assert param.get_value_at_tmaxfrac(0.0) == 1.838


def test_soa_parameter_validation():
    """Test SOAParameter validation logic"""
    param = SOAParameter(
        name="vhigh_ds_on",
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: 1.65, 0.01: 1.71, 0.0: 1.838}
    )
    
    # Test validation at different tmaxfrac levels
    assert param.validate_value(1.5, 0.1) == True   # Below limit
    assert param.validate_value(1.7, 0.1) == False  # Above limit
    assert param.validate_value(1.7, 0.01) == True  # Below limit at different tmaxfrac


def test_soa_parameter_no_limit():
    """Test no-limit parameter handling"""
    param = SOAParameter(
        name="test_param",
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: "no-limit", 0.01: 1.5, 0.0: 1.0}
    )
    
    assert param.is_no_limit(0.1) == True
    assert param.is_no_limit(0.01) == False
    assert param.validate_value(999.0, 0.1) == True  # No limit should always pass


def test_device_rules_creation():
    """Test DeviceRules creation and parameter management"""
    param1 = SOAParameter(
        name="vhigh_ds_on",
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: 1.65}
    )
    
    param2 = SOAParameter(
        name="vhigh_ds_off", 
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: 1.815}
    )
    
    device = DeviceRules(
        device_type="mos_transistor",
        subcategory="symmetric_on_off",
        tmaxfrac_levels=[0.1, 0.01, 0.0],
        parameters={"vhigh_ds_on": param1, "vhigh_ds_off": param2}
    )
    
    assert device.device_type == "mos_transistor"
    assert device.subcategory == "symmetric_on_off"
    assert len(device.parameters) == 2
    assert "vhigh_ds_on" in device.parameters
    assert "vhigh_ds_off" in device.parameters


def test_device_rules_validation():
    """Test DeviceRules validation functionality"""
    param = SOAParameter(
        name="vhigh_ds_on",
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: 1.65}
    )
    
    device = DeviceRules(
        device_type="mos_transistor",
        subcategory="symmetric_on_off", 
        tmaxfrac_levels=[0.1],
        parameters={"vhigh_ds_on": param}
    )
    
    # Test compliant case
    violations = device.validate_conditions(0.1, vhigh_ds_on=1.5)
    assert len(violations) == 0
    
    # Test violation case
    violations = device.validate_conditions(0.1, vhigh_ds_on=2.0)
    assert len(violations) == 1
    assert "vhigh_ds_on" in violations[0]


def test_soa_rules_engine():
    """Test SOARulesEngine basic functionality"""
    engine = SOARulesEngine()
    
    # Create test parameter and device
    param = SOAParameter(
        name="vhigh_ds_on",
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: 1.65}
    )
    
    device = DeviceRules(
        device_type="mos_transistor",
        subcategory="symmetric_on_off",
        tmaxfrac_levels=[0.1],
        parameters={"vhigh_ds_on": param}
    )
    
    # Add device to engine
    engine.add_device("test_mos", device)
    
    assert len(engine.devices) == 1
    assert "test_mos" in engine.devices
    
    # Test compliance checking
    result = engine.check_soa_compliance("test_mos", 0.1, vhigh_ds_on=1.5)
    assert result['compliant'] == True
    assert len(result['violations']) == 0
    
    result = engine.check_soa_compliance("test_mos", 0.1, vhigh_ds_on=2.0)
    assert result['compliant'] == False
    assert len(result['violations']) == 1


def test_soa_rules_engine_export_import():
    """Test SOARulesEngine JSON export/import functionality"""
    engine = SOARulesEngine()
    
    # Create test data
    param = SOAParameter(
        name="test_param",
        severity=Severity.HIGH,
        param_type=ParameterType.VOLTAGE,
        unit="V",
        values={0.1: 1.5, 0.01: 1.6}
    )
    
    device = DeviceRules(
        device_type="test_device",
        subcategory="test_sub",
        tmaxfrac_levels=[0.1, 0.01],
        parameters={"test_param": param}
    )
    
    engine.add_device("test_device", device)
    
    # Export to JSON
    json_data = engine.export_to_json()
    
    assert "soa_rules" in json_data
    assert "devices" in json_data["soa_rules"]
    assert "test_device" in json_data["soa_rules"]["devices"]
    
    # Create new engine and import
    new_engine = SOARulesEngine()
    new_engine.load_from_json(json_data)
    
    assert len(new_engine.devices) == 1
    assert "test_device" in new_engine.devices
    
    # Verify imported device works
    result = new_engine.check_soa_compliance("test_device", 0.1, test_param=1.4)
    assert result['compliant'] == True


if __name__ == "__main__":
    pytest.main([__file__])