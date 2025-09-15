# Device-Grouped SOA Rule Extraction

## 🎯 **Problem Solved**

The original extraction mixed all rules together. Now we have **device-grouped extraction** that organizes rules exactly as they appear in the Excel file, grouped by specific device types.

## 📊 **Device-Grouped Results**

### **Extracted Device Types:**

1. **NMOS Core Transistors** (`mos_transistor_core_nmos`)
   - **40 parameters** with tmaxfrac levels [0.1, 0.01, 0.0]
   - Includes: core nmos, nmos_LL, nmos_ULL variants
   - Source: 10HV SOA SYM ON-OFF sheet

2. **PMOS Core Transistors** (`mos_transistor_core_pmos`)
   - **30 parameters** with tmaxfrac levels [0.1, 0.01, 0.0]
   - Includes: core pmos, pmos_LL, pmos_ULL variants
   - Source: 10HV SOA SYM ON-OFF sheet

3. **NMOS 5V Transistors** (`mos_transistor_5v_nmos`)
   - **20 parameters** with tmaxfrac levels [0.1, 0.01, 0.0]
   - Includes: nmos5 devices
   - Source: 10HV SOA SYM ON-OFF sheet

4. **CGLV Capacitors** (`capacitor_gate_low_voltage`)
   - **14 parameters** with tmaxfrac levels [0.1, 0.01, 0.0]
   - Gate capacitors, low voltage
   - Source: 10HV SOA CAPS sheet

### **Total: 104 parameters across 4 device types**

## 🚀 **Usage**

### **Extract Device-Grouped Rules:**
```bash
# Using Poetry (recommended)
poetry run soa-extract

# Using make
make extract

# Direct execution
python device_grouped_extractor.py
```

### **Generated Files:**
- `device_grouped_soa_rules.json` - Complete device-grouped rules
- `device_summary.txt` - Human-readable device breakdown

## 📋 **Device Information Structure**

Each device includes:

```json
{
  "device_info": {
    "name": "NMOS Core",
    "type": "mos_transistor", 
    "category": "core",
    "subcategory": "nmos",
    "description": "core nmos, nmos_LL, nmos_ULL variants",
    "source_sheet": "10HV SOA SYM ON-OFF",
    "technology": "smos10hv"
  },
  "rule_count": 40,
  "tmaxfrac_levels": [0.1, 0.01, 0.0],
  "parameters": {
    "vhigh_ds_on": {
      "severity": "high",
      "type": "voltage",
      "unit": "V", 
      "description": "high severity limit for vhigh_ds_on",
      "tmaxfrac_constraints": {
        "0.1": 1.65,
        "0.01": 1.71,
        "0.0": 1.838
      },
      "conditions": [],
      "notes": "Extracted from tmaxfrac section at row 7"
    }
  }
}
```

## 🔍 **Key Features**

### **1. Device Recognition**
- **Automatic device identification** from Excel content
- **Device type classification**: MOS, capacitors, diodes, BJTs, etc.
- **Category and subcategory** assignment

### **2. Proper Grouping**
- **Rules grouped by actual devices** as they appear in Excel
- **Separate entries** for NMOS vs PMOS vs 5V variants
- **Device-specific tmaxfrac levels**

### **3. Complete Device Information**
- **Device name and description** from Excel
- **Source sheet tracking**
- **Technology identification** (SMOS10HV)
- **Parameter count and types**

## 📈 **Comparison: Before vs After**

| Aspect | Before | After (Device-Grouped) |
|--------|--------|----------------------|
| **Organization** | Mixed all rules | **Grouped by device type** |
| **Device Info** | Generic categories | **Specific device names** |
| **Traceability** | Hard to trace | **Source sheet + row tracking** |
| **Usability** | Find rules manually | **Direct device lookup** |
| **Accuracy** | Approximated grouping | **Exact Excel structure** |

## 🎯 **Example Usage in Code**

```python
import json

# Load device-grouped rules
with open('device_grouped_soa_rules.json', 'r') as f:
    device_rules = json.load(f)

# Get all NMOS core rules
nmos_core = device_rules['soa_device_rules']['devices']['mos_transistor_core_nmos']

print(f"NMOS Core Device:")
print(f"  Name: {nmos_core['device_info']['name']}")
print(f"  Parameters: {nmos_core['rule_count']}")
print(f"  tmaxfrac levels: {nmos_core['tmaxfrac_levels']}")

# Get specific parameter
vhigh_ds_on = nmos_core['parameters']['vhigh_ds_on']
print(f"\nvhigh_ds_on limits:")
for tmaxfrac, limit in vhigh_ds_on['tmaxfrac_constraints'].items():
    print(f"  tmaxfrac={tmaxfrac}: {limit}V")
```

## 🔧 **Integration with Simulation Tools**

### **Device-Specific Validation:**
```python
def validate_nmos_core(voltage_profile, total_time):
    """Validate NMOS core transistor against its specific rules"""
    
    nmos_rules = device_rules['soa_device_rules']['devices']['mos_transistor_core_nmos']
    
    for param_name, param_rules in nmos_rules['parameters'].items():
        if param_name in voltage_profile:
            # Check tmaxfrac constraints
            for tmaxfrac, limit in param_rules['tmaxfrac_constraints'].items():
                max_time = tmaxfrac * total_time
                # Validate voltage vs time constraints
                # ... validation logic
```

### **SPICE Integration:**
```python
def get_device_soa_limits(device_type, tmaxfrac_level):
    """Get SOA limits for specific device type and tmaxfrac level"""
    
    device_rules = load_device_rules(device_type)
    limits = {}
    
    for param_name, param in device_rules['parameters'].items():
        if tmaxfrac_level in param['tmaxfrac_constraints']:
            limits[param_name] = param['tmaxfrac_constraints'][tmaxfrac_level]
    
    return limits
```

## ✅ **Benefits of Device-Grouped Extraction**

1. **🎯 Accurate Device Mapping** - Rules match Excel device organization
2. **🔍 Easy Device Lookup** - Find rules by specific device type
3. **📊 Complete Device Info** - Name, category, source tracking
4. **🚀 Simulation Ready** - Direct integration with device models
5. **📋 Traceability** - Track rules back to Excel source
6. **🔧 Maintainable** - Update rules per device type independently

**This device-grouped approach provides the exact structure needed for semiconductor design tools and simulation environments!** 🎉