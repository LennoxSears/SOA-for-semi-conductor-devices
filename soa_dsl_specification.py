#!/usr/bin/env python3
"""
SOA DSL (Domain Specific Language) Specification Design
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Union, Optional
from enum import Enum

class RuleType(Enum):
    VOLTAGE = "voltage"
    CURRENT = "current" 
    POWER = "power"
    TEMPERATURE = "temperature"
    FREQUENCY = "frequency"

class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    REVIEW = "review"
    HIGH = "high"

class ConstraintType(Enum):
    SIMPLE = "simple"           # Simple numeric limits
    EQUATION = "equation"       # Mathematical expressions
    FUNCTION = "function"       # Built-in functions (min, max, etc.)
    CONDITIONAL = "conditional" # If-then-else logic
    TMAXFRAC = "tmaxfrac"      # Time-based transient constraints

@dataclass
class Variable:
    """Represents a variable in the DSL"""
    name: str
    type: str  # voltage, current, temperature, parameter
    pins: Optional[List[str]] = None  # For multi-pin variables like v[d,s]
    description: Optional[str] = None

@dataclass
class Expression:
    """Represents a mathematical expression"""
    type: ConstraintType
    expression: str
    variables: List[Variable]
    description: Optional[str] = None

@dataclass
class TmaxfracConstraint:
    """Time-based transient constraint"""
    levels: Dict[float, Union[float, str]]  # tmaxfrac level -> limit value
    description: str = "Transient maximum fraction constraint"

@dataclass
class SOARule:
    """Complete SOA rule definition"""
    id: str
    name: str
    device_type: str
    device_category: str
    parameter: str
    rule_type: RuleType
    severity: SeverityLevel
    constraints: Dict[str, Expression]
    tmaxfrac: Optional[TmaxfracConstraint] = None
    metadata: Optional[Dict] = None

class SOADSLSpecification:
    """SOA DSL Specification and Examples"""
    
    def __init__(self):
        self.specification = self._create_specification()
        self.examples = self._create_examples()
    
    def _create_specification(self):
        """Create the DSL specification"""
        
        spec = {
            "soa_dsl": {
                "version": "1.0",
                "description": "Unified Domain Specific Language for SOA Rules",
                "syntax": {
                    "variables": {
                        "voltage": "v[pin1, pin2] or v[pin]",
                        "current": "i[pin] or i[device]", 
                        "temperature": "T or temp",
                        "parameters": "$param_name or device.param",
                        "constants": "numeric values or named constants"
                    },
                    "operators": {
                        "arithmetic": "+ - * / ^ ()",
                        "comparison": "< <= > >= == !=",
                        "logical": "&& || !",
                        "functions": "min() max() abs() sqrt() exp() log()"
                    },
                    "constraints": {
                        "simple": "value or range",
                        "equation": "mathematical expression",
                        "conditional": "if condition then expr1 else expr2",
                        "tmaxfrac": "time_level: constraint_value"
                    }
                },
                "rule_structure": {
                    "required_fields": ["id", "name", "device_type", "parameter", "rule_type", "severity"],
                    "optional_fields": ["tmaxfrac", "metadata", "description"],
                    "constraint_types": ["vlow", "vhigh", "ilow", "ihigh", "custom"]
                }
            }
        }
        
        return spec
    
    def _create_examples(self):
        """Create comprehensive examples for all rule types"""
        
        examples = []
        
        # 1. Simple numeric constraint
        examples.append(SOARule(
            id="nmos_core_vds_simple",
            name="NMOS Core VDS Simple Limit",
            device_type="mos_transistor",
            device_category="core_nmos",
            parameter="v[d,s]",
            rule_type=RuleType.VOLTAGE,
            severity=SeverityLevel.HIGH,
            constraints={
                "vhigh": Expression(
                    type=ConstraintType.SIMPLE,
                    expression="1.65",
                    variables=[Variable("v[d,s]", "voltage", ["d", "s"])]
                )
            }
        ))
        
        # 2. Temperature-dependent equation
        examples.append(SOARule(
            id="diode_temp_dependent",
            name="Diode Temperature Dependent Forward Voltage",
            device_type="diode",
            device_category="zener",
            parameter="v[p,n]_forward",
            rule_type=RuleType.VOLTAGE,
            severity=SeverityLevel.REVIEW,
            constraints={
                "vhigh": Expression(
                    type=ConstraintType.EQUATION,
                    expression="0.9943 - (0.0006 * (T - 25))",
                    variables=[
                        Variable("T", "temperature", description="Junction temperature"),
                        Variable("v[p,n]", "voltage", ["p", "n"])
                    ]
                )
            }
        ))
        
        # 3. Multi-pin voltage with function
        examples.append(SOARule(
            id="diode_multi_pin_function",
            name="Diode Multi-Pin with Min Function",
            device_type="diode", 
            device_category="power",
            parameter="v[n,p]_reverse",
            rule_type=RuleType.VOLTAGE,
            severity=SeverityLevel.REVIEW,
            constraints={
                "vlow": Expression(
                    type=ConstraintType.FUNCTION,
                    expression="min(90, 90 + v[p] - v[sub])",
                    variables=[
                        Variable("v[p]", "voltage", ["p"]),
                        Variable("v[sub]", "voltage", ["sub"]),
                        Variable("v[n,p]", "voltage", ["n", "p"])
                    ]
                )
            }
        ))
        
        # 4. Current rule with device parameters
        examples.append(SOARule(
            id="resistor_current_limit",
            name="Resistor Current Limit with Width Dependency",
            device_type="resistor",
            device_category="poly",
            parameter="i[resistor]",
            rule_type=RuleType.CURRENT,
            severity=SeverityLevel.ERROR,
            constraints={
                "imax": Expression(
                    type=ConstraintType.EQUATION,
                    expression="$w * $np * 2.12e-4",
                    variables=[
                        Variable("$w", "parameter", description="Device width"),
                        Variable("$np", "parameter", description="Number of parallel segments"),
                        Variable("i[resistor]", "current")
                    ]
                )
            }
        ))
        
        # 5. tmaxfrac constraint
        examples.append(SOARule(
            id="nmos_tmaxfrac_constraint",
            name="NMOS Core with tmaxfrac Levels",
            device_type="mos_transistor",
            device_category="core_nmos", 
            parameter="v[d,s]",
            rule_type=RuleType.VOLTAGE,
            severity=SeverityLevel.HIGH,
            constraints={
                "vhigh_steady": Expression(
                    type=ConstraintType.SIMPLE,
                    expression="1.65",
                    variables=[Variable("v[d,s]", "voltage", ["d", "s"])]
                )
            },
            tmaxfrac=TmaxfracConstraint(
                levels={
                    0.1: 1.71,    # 10% of time
                    0.01: 1.84,   # 1% of time  
                    0.0: 1.65     # Steady state
                }
            )
        ))
        
        # 6. Conditional constraint
        examples.append(SOARule(
            id="bjt_conditional_limit",
            name="BJT Conditional Voltage Limit",
            device_type="bjt",
            device_category="npn",
            parameter="v[c,e]",
            rule_type=RuleType.VOLTAGE,
            severity=SeverityLevel.HIGH,
            constraints={
                "vhigh": Expression(
                    type=ConstraintType.CONDITIONAL,
                    expression="if (T > 85) then 10.0 else 12.0",
                    variables=[
                        Variable("T", "temperature"),
                        Variable("v[c,e]", "voltage", ["c", "e"])
                    ]
                )
            }
        ))
        
        return examples
    
    def generate_dsl_grammar(self):
        """Generate formal grammar for the DSL"""
        
        grammar = """
        # SOA DSL Grammar (EBNF-style)
        
        rule := rule_header constraint_block [tmaxfrac_block] [metadata_block]
        
        rule_header := 'rule' rule_id '{' 
                      'name:' string ','
                      'device:' device_spec ','
                      'parameter:' parameter_spec ','
                      'type:' rule_type ','
                      'severity:' severity_level
                      '}'
        
        constraint_block := 'constraints' '{' constraint_list '}'
        constraint_list := constraint (',' constraint)*
        constraint := constraint_name ':' expression
        
        tmaxfrac_block := 'tmaxfrac' '{' tmaxfrac_list '}'
        tmaxfrac_list := tmaxfrac_entry (',' tmaxfrac_entry)*
        tmaxfrac_entry := float_literal ':' expression
        
        expression := simple_expr | equation_expr | function_expr | conditional_expr
        
        simple_expr := number | range
        equation_expr := math_expression
        function_expr := function_name '(' argument_list ')'
        conditional_expr := 'if' condition 'then' expression 'else' expression
        
        math_expression := term (('+' | '-') term)*
        term := factor (('*' | '/') factor)*
        factor := number | variable | '(' math_expression ')'
        
        variable := voltage_var | current_var | temp_var | param_var
        voltage_var := 'v[' pin_list ']'
        current_var := 'i[' pin_list ']'
        temp_var := 'T' | 'temp'
        param_var := '$' identifier
        
        pin_list := identifier (',' identifier)*
        """
        
        return grammar
    
    def save_specification(self):
        """Save the complete DSL specification"""
        
        # Convert examples to dict format
        examples_dict = []
        for example in self.examples:
            example_dict = asdict(example)
            # Convert enums to strings
            example_dict['rule_type'] = example.rule_type.value
            example_dict['severity'] = example.severity.value
            for constraint_name, constraint in example_dict['constraints'].items():
                constraint['type'] = constraint['type'].value if hasattr(constraint['type'], 'value') else constraint['type']
            examples_dict.append(example_dict)
        
        complete_spec = {
            "specification": self.specification,
            "grammar": self.generate_dsl_grammar(),
            "examples": examples_dict,
            "implementation_notes": {
                "parser": "ANTLR4 or PLY (Python Lex-Yacc) recommended",
                "validation": "Type checking and constraint validation required",
                "code_generation": "Target languages: Python, C++, Verilog-A",
                "testing": "Automated test case generation from rules"
            }
        }
        
        with open('soa_dsl_specification.json', 'w') as f:
            json.dump(complete_spec, f, indent=2)
        
        print("✅ SOA DSL specification saved to soa_dsl_specification.json")
        return complete_spec

def main():
    """Generate the complete DSL specification"""
    
    print("🔧 DESIGNING SOA DSL SPECIFICATION")
    print("=" * 60)
    
    dsl = SOADSLSpecification()
    spec = dsl.save_specification()
    
    print(f"\n📋 DSL FEATURES:")
    print(f"   - Unified syntax for all rule types")
    print(f"   - Support for complex expressions and functions")
    print(f"   - tmaxfrac transient constraints")
    print(f"   - Multi-pin voltage/current references")
    print(f"   - Temperature and parameter dependencies")
    print(f"   - Conditional logic support")
    
    print(f"\n📊 EXAMPLE RULES CREATED: {len(dsl.examples)}")
    for i, example in enumerate(dsl.examples, 1):
        print(f"   {i}. {example.name}")
    
    print(f"\n✅ Complete DSL specification ready for implementation")

if __name__ == "__main__":
    main()