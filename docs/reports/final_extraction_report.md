# Enhanced SOA Parameter Extraction Report

## Overview

- **Technology**: smos10hv
- **Extraction Method**: Enhanced extraction (tmaxfrac + general patterns)
- **Total Devices**: 13
- **Total Parameters**: 277
- **Extraction Date**: 2025-09-15

## Improvements vs Original

- **Parameter Increase**: 8.1x more parameters
- **Coverage Increase**: 714.7%
- **Device Types**: 6 vs 2 device types

## Key Features

- tmaxfrac transient time constraints
- Multiple device types (MOS, BJT, Diodes, Capacitors, Substrate, Oxide)
- Comprehensive parameter coverage
- Device-grouped organization

## Device Type Breakdown

### Mos Transistor

MOS transistors with core and 5V variants

- **Devices**: 4
- **Total Parameters**: 100
- **tmaxfrac Devices**: 4

  🕒 **NMOS Core**: 40 parameters
  🕒 **PMOS Core**: 30 parameters
  🕒 **NMOS 5V**: 20 parameters
  🕒 **PMOS 5V**: 10 parameters

### Bjt

Bipolar junction transistors (NPN, PNP, PNP ISO)

- **Devices**: 3
- **Total Parameters**: 50
- **tmaxfrac Devices**: 3

  🕒 **BJT NPN**: 21 parameters
  🕒 **BJT PNP**: 16 parameters
  🕒 **BJT PNP ISO**: 13 parameters

### Capacitor

Various capacitor types

- **Devices**: 1
- **Total Parameters**: 15
- **tmaxfrac Devices**: 1

  🕒 **All Capacitors**: 15 parameters

### Diode

Forward and reverse diodes

- **Devices**: 1
- **Total Parameters**: 8
- **tmaxfrac Devices**: 1

  🕒 **Diodes**: 8 parameters

### Substrate

Substrate and well constraints

- **Devices**: 3
- **Total Parameters**: 58
- **tmaxfrac Devices**: 3

  🕒 **Substrate Well**: 20 parameters
  🕒 **Substrate HV**: 30 parameters
  🕒 **Substrate HV Additional**: 8 parameters

### Oxide

Oxide reliability constraints

- **Devices**: 1
- **Total Parameters**: 46
- **tmaxfrac Devices**: 1

  🕒 **Oxide Reliability**: 46 parameters

## tmaxfrac Analysis

### Devices with tmaxfrac Constraints (13 devices)

- **NMOS Core**: 40 parameters, levels: [0.1, 0.01, 0.0]
- **PMOS Core**: 30 parameters, levels: [0.1, 0.01, 0.0]
- **NMOS 5V**: 20 parameters, levels: [0.1, 0.01, 0.0]
- **PMOS 5V**: 10 parameters, levels: [0.1, 0.01, 0.0]
- **All Capacitors**: 15 parameters, levels: [0.1, 0.01, 0.0]
- **Substrate Well**: 20 parameters, levels: [0.0]
- **Oxide Reliability**: 46 parameters, levels: [0.0]
- **Substrate HV**: 30 parameters, levels: [0.0]
- **Substrate HV Additional**: 8 parameters, levels: [0.0]
- **Diodes**: 8 parameters, levels: [0.0]
- **BJT NPN**: 21 parameters, levels: [0.0]
- **BJT PNP**: 16 parameters, levels: [0.0]
- **BJT PNP ISO**: 13 parameters, levels: [0.0]

## Conclusion

The enhanced extraction method successfully captures comprehensive SOA rules with significant improvements in parameter coverage and device type diversity. The inclusion of tmaxfrac constraints provides critical transient timing information for semiconductor device safe operating area analysis.
