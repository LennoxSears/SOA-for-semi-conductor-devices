#!/usr/bin/env python3
"""
Analyze SOA rule complexity and current workflow problems
"""

import json
import re
from pathlib import Path

def analyze_rule_complexity():
    """Analyze the complexity and variety of SOA rules"""
    
    print("🔍 SOA RULE COMPLEXITY ANALYSIS")
    print("=" * 60)
    
    # Load final results
    with open('final_soa_device_rules.json', 'r') as f:
        data = json.load(f)
    
    rule_patterns = {
        'simple_numeric': [],
        'equations': [],
        'functions': [],
        'temperature_dependent': [],
        'multi_pin_voltage': [],
        'current_rules': [],
        'tmaxfrac_constraints': [],
        'complex_expressions': []
    }
    
    total_rules = 0
    
    # Analyze each device's parameters
    for device_key, device_data in data['soa_device_rules']['devices'].items():
        device_name = device_data['device_info']['name']
        
        for param in device_data['parameters']:
            total_rules += 1
            param_name = param['name']
            constraints = param['constraints']
            
            # Check for different rule types
            for constraint_key, constraint_value in constraints.items():
                value_str = str(constraint_value)
                
                # Simple numeric rules
                if re.match(r'^-?\d+\.?\d*$', value_str):
                    rule_patterns['simple_numeric'].append({
                        'device': device_name,
                        'parameter': param_name,
                        'constraint': f"{constraint_key}: {value_str}"
                    })
                
                # Equations with operators
                elif any(op in value_str for op in ['+', '-', '*', '/', '(', ')']):
                    if 'T-25' in value_str or 'temp' in value_str.lower():
                        rule_patterns['temperature_dependent'].append({
                            'device': device_name,
                            'parameter': param_name,
                            'constraint': f"{constraint_key}: {value_str}"
                        })
                    elif 'v[' in value_str.lower() or 'V[' in value_str:
                        rule_patterns['multi_pin_voltage'].append({
                            'device': device_name,
                            'parameter': param_name,
                            'constraint': f"{constraint_key}: {value_str}"
                        })
                    else:
                        rule_patterns['equations'].append({
                            'device': device_name,
                            'parameter': param_name,
                            'constraint': f"{constraint_key}: {value_str}"
                        })
                
                # Functions
                elif any(func in value_str for func in ['min(', 'max(', 'abs(', 'sqrt(']):
                    rule_patterns['functions'].append({
                        'device': device_name,
                        'parameter': param_name,
                        'constraint': f"{constraint_key}: {value_str}"
                    })
                
                # Current rules (very small numbers or specific patterns)
                elif 'e-' in value_str or (value_str.startswith('-0.000') and len(value_str) > 6):
                    rule_patterns['current_rules'].append({
                        'device': device_name,
                        'parameter': param_name,
                        'constraint': f"{constraint_key}: {value_str}"
                    })
                
                # Complex expressions with variables
                elif '$' in value_str or 'np' in value_str:
                    rule_patterns['complex_expressions'].append({
                        'device': device_name,
                        'parameter': param_name,
                        'constraint': f"{constraint_key}: {value_str}"
                    })
            
            # tmaxfrac constraints
            if param.get('tmaxfrac_constraints'):
                rule_patterns['tmaxfrac_constraints'].append({
                    'device': device_name,
                    'parameter': param_name,
                    'constraint': f"tmaxfrac: {param['tmaxfrac_constraints']}"
                })
    
    # Print analysis results
    print(f"📊 TOTAL RULES ANALYZED: {total_rules}")
    print()
    
    for pattern_type, rules in rule_patterns.items():
        if rules:
            print(f"🔸 {pattern_type.replace('_', ' ').title()}: {len(rules)} rules")
            for i, rule in enumerate(rules[:3]):  # Show first 3 examples
                print(f"   {i+1}. {rule['device']} - {rule['parameter']}: {rule['constraint']}")
            if len(rules) > 3:
                print(f"   ... and {len(rules) - 3} more")
            print()
    
    return rule_patterns, total_rules

def identify_workflow_problems():
    """Identify current workflow problems"""
    
    problems = {
        'manual_implementation': {
            'description': 'Each rule must be manually implemented in model code',
            'impact': 'Time-consuming, error-prone, inconsistent implementation',
            'frequency': 'Every new SOA rule set (monthly/quarterly)'
        },
        'no_unified_format': {
            'description': 'Rules come in arbitrary Excel formats with no standardization',
            'impact': 'Requires manual parsing and interpretation each time',
            'frequency': 'Every Excel delivery'
        },
        'manual_qa_testing': {
            'description': 'Each rule must be individually tested through simulation',
            'impact': 'Extensive simulation time, potential for missed edge cases',
            'frequency': 'Every rule implementation'
        },
        'rule_complexity_variety': {
            'description': 'Rules range from simple numbers to complex equations with functions',
            'impact': 'Different implementation approaches needed for each type',
            'frequency': 'Continuous'
        },
        'dependency_management': {
            'description': 'Rules depend on voltages, currents, temperature, device parameters',
            'impact': 'Complex dependency tracking and validation required',
            'frequency': 'Most rules'
        },
        'version_control': {
            'description': 'No systematic way to track rule changes and versions',
            'impact': 'Difficult to maintain consistency across updates',
            'frequency': 'Every update cycle'
        }
    }
    
    print("⚠️ CURRENT WORKFLOW PROBLEMS")
    print("=" * 60)
    
    for problem_id, problem_info in problems.items():
        print(f"🔸 {problem_id.replace('_', ' ').title()}")
        print(f"   Description: {problem_info['description']}")
        print(f"   Impact: {problem_info['impact']}")
        print(f"   Frequency: {problem_info['frequency']}")
        print()
    
    return problems

def calculate_current_costs():
    """Calculate current workflow costs"""
    
    # Estimated time costs (in hours)
    costs = {
        'rule_parsing': {
            'time_per_rule': 0.5,  # 30 minutes to understand and parse each rule
            'description': 'Manual parsing and interpretation of Excel rules'
        },
        'implementation': {
            'time_per_rule': 2.0,  # 2 hours to implement each rule in model
            'description': 'Manual coding of rule logic in simulation model'
        },
        'testing': {
            'time_per_rule': 1.0,  # 1 hour to test each rule
            'description': 'Individual simulation testing and validation'
        },
        'debugging': {
            'time_per_rule': 0.5,  # 30 minutes average for debugging issues
            'description': 'Fixing implementation errors and edge cases'
        }
    }
    
    # Based on our analysis - 277 rules extracted
    total_rules = 277
    
    print("💰 CURRENT WORKFLOW COSTS")
    print("=" * 60)
    
    total_time = 0
    for cost_type, cost_info in costs.items():
        time_cost = total_rules * cost_info['time_per_rule']
        total_time += time_cost
        
        print(f"🔸 {cost_type.replace('_', ' ').title()}")
        print(f"   Time per rule: {cost_info['time_per_rule']} hours")
        print(f"   Total time ({total_rules} rules): {time_cost} hours")
        print(f"   Description: {cost_info['description']}")
        print()
    
    print(f"📊 TOTAL ESTIMATED TIME: {total_time} hours ({total_time/8:.1f} working days)")
    print(f"📊 COST PER RULE SET: ~{total_time/8:.0f} days of engineering time")
    print()
    
    return total_time

def main():
    """Main analysis function"""
    
    rule_patterns, total_rules = analyze_rule_complexity()
    problems = identify_workflow_problems()
    total_cost = calculate_current_costs()
    
    # Save analysis results
    analysis_results = {
        'rule_patterns': {k: len(v) for k, v in rule_patterns.items()},
        'total_rules': total_rules,
        'problems': problems,
        'estimated_cost_hours': total_cost,
        'estimated_cost_days': total_cost / 8
    }
    
    with open('workflow_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print("✅ Analysis complete. Results saved to workflow_analysis.json")

if __name__ == "__main__":
    main()