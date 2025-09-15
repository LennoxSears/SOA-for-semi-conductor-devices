"""
SOA (Safe Operating Area) Rules for Semiconductor Devices

A comprehensive Python package for analyzing, validating, and manipulating
SOA rules for SMOS10HV semiconductor technology with transient time constraints.
"""

__version__ = "1.0.0"
__author__ = "Your Organization"

from .soa_dsl_implementation import (
    SOARulesEngine,
    DeviceRules,
    SOAParameter,
    Severity,
    ParameterType,
    ComparisonOperator,
    Condition
)

from .complete_rule_extractor import CompleteSOAExtractor
from .loader import load_soa_rules, load_complete_soa_rules, load_basic_soa_rules

__all__ = [
    "SOARulesEngine",
    "DeviceRules", 
    "SOAParameter",
    "Severity",
    "ParameterType",
    "ComparisonOperator",
    "Condition",
    "CompleteSOAExtractor",
    "load_soa_rules",
    "load_complete_soa_rules", 
    "load_basic_soa_rules"
]