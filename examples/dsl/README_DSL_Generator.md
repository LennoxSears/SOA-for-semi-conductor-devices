# SOA DSL Generator Tool

Interactive HTML tool for generating Safe Operating Area Domain Specific Language (DSL) rules.

## 🎯 Overview

This tool provides a user-friendly interface for creating SOA DSL rules without manually writing syntax. Simply click, select, and generate professional DSL code.

## 🚀 Quick Start

### Method 1: Direct Browser
1. Open `dsl_generator.html` in any modern browser
2. Fill in the form fields
3. Click "Generate DSL"
4. Copy the generated code

### Method 2: Python Launcher
```bash
python3 examples/dsl/launch_dsl_generator.py
```

## 🔧 Features

### Interactive Form
- **Device Selection**: Choose from MOS, BJT, Diode, Capacitor, etc.
- **Parameter Input**: Specify voltage/current parameters like v[d,s], i[drain]
- **Constraint Values**: Set limits with units
- **Severity Levels**: High, Medium, Low, Critical, etc.

### tmaxfrac Support
- **Enable/Disable**: Toggle tmaxfrac constraints
- **Multiple Levels**: 0.1 (10%), 0.01 (1%), 0.0 (never)
- **Time-based Limits**: Transient constraint specification

### Example Templates
- **NMOS Example**: Core NMOS with tmaxfrac levels
- **PMOS Example**: Core PMOS voltage limits
- **BJT Example**: Bipolar transistor constraints
- **Diode Example**: Forward voltage limits

### Output Features
- **Syntax Highlighting**: Color-coded DSL output
- **Real-time Generation**: Updates as you type
- **Copy to Clipboard**: One-click copying
- **Professional Formatting**: Clean, readable DSL code

## 📋 Generated DSL Format

The tool generates DSL in this format:

```dsl
rule nmos_core_tmaxfrac {
    name: "NMOS Core with tmaxfrac Levels"
    device: mos_transistor.core
    parameter: v[d,s]
    type: vhigh
    severity: high
    
    constraints {
        vhigh: 1.65
    }
    
    tmaxfrac {
        0.1: 1.71,
        0.01: 1.84,
        0.0: 1.65
    }
}
```

## 🎯 Use Cases

### Rule Development
- **Rapid Prototyping**: Quickly create new SOA rules
- **Template Generation**: Use examples as starting points
- **Syntax Validation**: Ensure correct DSL format

### Team Collaboration
- **Standardization**: Consistent rule format across team
- **Documentation**: Clear, readable rule specifications
- **Version Control**: Text-based rules for git tracking

### Integration
- **Code Generation**: Feed DSL into automated tools
- **Simulation Setup**: Use rules in simulation frameworks
- **Validation**: Test rule syntax before implementation

## 📊 Supported Parameters

### Device Types
- **mos_transistor**: NMOS, PMOS transistors
- **bjt**: Bipolar junction transistors
- **diode**: Various diode types
- **capacitor**: Capacitor constraints
- **resistor**: Resistor limitations
- **substrate**: Substrate rules

### Parameter Types
- **vhigh/vlow**: Voltage limits
- **ihigh/ilow**: Current limits
- **power**: Power constraints
- **temperature**: Thermal limits

### Constraint Examples
- **Simple Values**: 1.65, 3.3, 5.0
- **Units**: 1.65V, 100mA, 1W
- **Special Values**: no-limit, TBD
- **Equations**: Supported in advanced mode

## 🔧 Technical Details

### Browser Compatibility
- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support

### File Structure
```
examples/dsl/
├── dsl_generator.html          # Main HTML tool
├── launch_dsl_generator.py     # Python launcher
└── README_DSL_Generator.md     # This documentation
```

### Dependencies
- **None**: Pure HTML/CSS/JavaScript
- **Modern Browser**: ES6+ support required
- **Clipboard API**: For copy functionality

## 🎯 Advanced Usage

### Custom Templates
Add your own examples by modifying the `examples` object in the JavaScript:

```javascript
const examples = {
    custom: {
        ruleName: 'Custom Rule',
        deviceType: 'custom_device',
        // ... other parameters
    }
};
```

### Integration with Tools
The generated DSL can be:
- **Saved to Files**: Copy and save as `.dsl` files
- **Fed to Parsers**: Use in automated processing
- **Version Controlled**: Track changes in git
- **Validated**: Check syntax with DSL parser

## 📞 Support

For questions or enhancements:
1. Check the generated DSL syntax
2. Verify parameter formats
3. Test with example templates
4. Review DSL specification documentation

---

**The DSL Generator makes SOA rule creation fast, consistent, and error-free!**