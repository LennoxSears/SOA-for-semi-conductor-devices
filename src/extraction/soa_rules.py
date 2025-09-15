"""
Auto-generated SOA Rules Module
Converted from SMOS10HV Excel file
"""

from soa_dsl_implementation import SOARulesEngine, DeviceRules, SOAParameter, Severity, ParameterType

def load_soa_rules() -> SOARulesEngine:
    """Load all SOA rules into the engine"""
    
    soa = SOARulesEngine()
    

    # mos_transistor_symmetric_on_off rules
    mos_transistor_symmetric_on_off_params = {
        "vhigh_ds_on": SOAParameter(
            name="vhigh_ds_on",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: 5.5, 0.01: 5.6370000000000005, 0.0: 5.914000000000001},
            description="high severity limit for vhigh_ds_on"
        ),
        "vhigh_ds_off": SOAParameter(
            name="vhigh_ds_off",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: 6.050000000000001, 0.01: 6.200700000000001, 0.0: 6.505400000000001},
            description="high severity limit for vhigh_ds_off"
        ),
        "vhigh_gc": SOAParameter(
            name="vhigh_gc",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: 5.5, 0.01: 6.595, 0.0: 6.917},
            description="high severity limit for vhigh_gc"
        ),
        "vlow_gc": SOAParameter(
            name="vlow_gc",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: -5.5, 0.01: -6.595, 0.0: -6.917},
            description="high severity limit for vlow_gc"
        ),
        "vhigh_gb_on": SOAParameter(
            name="vhigh_gb_on",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: 6.917, 0.01: 'no-limit', 0.0: 'no-limit'},
            description="high severity limit for vhigh_gb_on"
        ),
        "vlow_gb_on": SOAParameter(
            name="vlow_gb_on",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: -6.917, 0.01: 'no-limit', 0.0: 'no-limit'},
            description="high severity limit for vlow_gb_on"
        ),
        "vfwd_jun_on": SOAParameter(
            name="vfwd_jun_on",
            severity=Severity.HIGH,
            param_type=ParameterType.GENERAL,
            unit="V",
            values={0.1: 'no-limit', 0.01: 'no-limit', 0.0: 'no-limit'},
            description="high severity limit for vfwd_jun_on"
        ),
        "vrev_jun_on": SOAParameter(
            name="vrev_jun_on",
            severity=Severity.HIGH,
            param_type=ParameterType.GENERAL,
            unit="V",
            values={0.1: -6.800000000000001, 0.01: 'no-limit', 0.0: 'no-limit'},
            description="high severity limit for vrev_jun_on"
        ),
        "vfwd_jun_off": SOAParameter(
            name="vfwd_jun_off",
            severity=Severity.HIGH,
            param_type=ParameterType.GENERAL,
            unit="V",
            values={0.1: 'no-limit', 0.01: 'no-limit', 0.0: 'no-limit'},
            description="high severity limit for vfwd_jun_off"
        ),
        "vrev_jun_off": SOAParameter(
            name="vrev_jun_off",
            severity=Severity.HIGH,
            param_type=ParameterType.GENERAL,
            unit="V",
            values={0.1: -6.800000000000001, 0.01: 'no-limit', 0.0: 'no-limit'},
            description="high severity limit for vrev_jun_off"
        ),
    }
    
    mos_transistor_symmetric_on_off_rules = DeviceRules(
        device_type="mos_transistor",
        subcategory="symmetric_on_off",
        tmaxfrac_levels=[0.1, 0.01, 0.0],
        parameters=mos_transistor_symmetric_on_off_params,
        metadata={'source_sheet': '10HV SOA SYM ON-OFF', 'technology': 'smos10hv'}
    )
    
    soa.add_device("mos_transistor_symmetric_on_off", mos_transistor_symmetric_on_off_rules)

    # capacitor_general rules
    capacitor_general_params = {
        "vhigh_tnw": SOAParameter(
            name="vhigh_tnw",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: 5.5, 0.01: 6.595, 0.0: 6.917},
            description="high severity limit for vhigh_tnw"
        ),
        "vlow_tnw": SOAParameter(
            name="vlow_tnw",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: -5.5, 0.01: -6.595, 0.0: -6.917},
            description="high severity limit for vlow_tnw"
        ),
        "vhigh_tb": SOAParameter(
            name="vhigh_tb",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: 120.0, 0.01: 125.0, 0.0: 130.0},
            description="high severity limit for vhigh_tb"
        ),
        "vlow_tb": SOAParameter(
            name="vlow_tb",
            severity=Severity.HIGH,
            param_type=ParameterType.VOLTAGE,
            unit="V",
            values={0.1: -120.0, 0.01: -125.0, 0.0: -130.0},
            description="high severity limit for vlow_tb"
        ),
    }
    
    capacitor_general_rules = DeviceRules(
        device_type="capacitor",
        subcategory="general",
        tmaxfrac_levels=[0.1, 0.01, 0.0],
        parameters=capacitor_general_params,
        metadata={'source_sheet': '10HV SOA CAPS', 'technology': 'smos10hv'}
    )
    
    soa.add_device("capacitor_general", capacitor_general_rules)

    # substrate_well_hv rules
    substrate_well_hv_params = {
    }
    
    substrate_well_hv_rules = DeviceRules(
        device_type="substrate",
        subcategory="well_hv",
        tmaxfrac_levels=[0.0],
        parameters=substrate_well_hv_params,
        metadata={'source_sheet': '10HV SOA SUB Well HV ', 'technology': 'smos10hv'}
    )
    
    soa.add_device("substrate_well_hv", substrate_well_hv_rules)

    # oxide_reliability_drift rules
    oxide_reliability_drift_params = {
    }
    
    oxide_reliability_drift_rules = DeviceRules(
        device_type="oxide",
        subcategory="reliability_drift",
        tmaxfrac_levels=[],
        parameters=oxide_reliability_drift_params,
        metadata={'source_sheet': '10HV SOA OXRisk Drift ', 'technology': 'smos10hv'}
    )
    
    soa.add_device("oxide_reliability_drift", oxide_reliability_drift_rules)

    return soa

# Example usage
if __name__ == "__main__":
    soa_engine = load_soa_rules()
    print(f"Loaded {len(soa_engine.devices)} device types")
    
    # Example validation
    for device_key in soa_engine.devices.keys():
        print(f"\nDevice: {device_key}")
        device = soa_engine.devices[device_key]
        print(f"  Parameters: {list(device.parameters.keys())}")
        print(f"  tmaxfrac levels: {device.tmaxfrac_levels}")
