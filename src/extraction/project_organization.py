#!/usr/bin/env python3
"""
Analyze and categorize all project files for reorganization
"""

import os
from pathlib import Path
import json

def analyze_project_files():
    """Analyze all files in the project and categorize them"""
    
    project_root = Path(".")
    
    # File categories
    categories = {
        "extraction_tools": {
            "description": "Tools for extracting SOA rules from Excel",
            "files": []
        },
        "dsl_implementation": {
            "description": "DSL specification and implementation",
            "files": []
        },
        "proposal_documents": {
            "description": "Business proposal and presentation materials",
            "files": []
        },
        "analysis_reports": {
            "description": "Analysis reports and summaries",
            "files": []
        },
        "extracted_data": {
            "description": "Extracted SOA rules and device data",
            "files": []
        },
        "validation_tools": {
            "description": "Validation and comparison tools",
            "files": []
        },
        "visualization": {
            "description": "Charts and visual assets",
            "files": []
        },
        "source_data": {
            "description": "Original Excel files and source data",
            "files": []
        },
        "configuration": {
            "description": "Project configuration and setup files",
            "files": []
        },
        "documentation": {
            "description": "Documentation and README files",
            "files": []
        },
        "legacy_files": {
            "description": "Old or superseded files",
            "files": []
        }
    }
    
    # Scan all files
    all_files = []
    for file_path in project_root.rglob("*"):
        if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
            if file_path.suffix in ['.py', '.json', '.md', '.txt', '.xlsx', '.png'] and '__pycache__' not in str(file_path):
                all_files.append(file_path)
    
    # Categorize files
    for file_path in all_files:
        filename = file_path.name.lower()
        
        # Extraction tools
        if any(keyword in filename for keyword in ['extract', 'mapper', 'parser', 'excel']):
            categories["extraction_tools"]["files"].append(str(file_path))
        
        # DSL implementation
        elif any(keyword in filename for keyword in ['dsl', 'demo_soa']):
            categories["dsl_implementation"]["files"].append(str(file_path))
        
        # Proposal documents
        elif any(keyword in filename for keyword in ['proposal', 'presentation', 'automation_benefits', 'implementation_architecture', 'workflow_analysis']):
            categories["proposal_documents"]["files"].append(str(file_path))
        
        # Analysis reports
        elif any(keyword in filename for keyword in ['analysis', 'report', 'summary', 'audit']) and not any(keyword in filename for keyword in ['automation', 'workflow']):
            categories["analysis_reports"]["files"].append(str(file_path))
        
        # Extracted data
        elif filename.endswith('.json') and any(keyword in filename for keyword in ['rules', 'device', 'mapping', 'pattern']):
            categories["extracted_data"]["files"].append(str(file_path))
        
        # Validation tools
        elif any(keyword in filename for keyword in ['validation', 'comparison', 'test']):
            categories["validation_tools"]["files"].append(str(file_path))
        
        # Visualization
        elif filename.endswith('.png'):
            categories["visualization"]["files"].append(str(file_path))
        
        # Source data
        elif filename.endswith('.xlsx'):
            categories["source_data"]["files"].append(str(file_path))
        
        # Configuration
        elif any(keyword in filename for keyword in ['pyproject', 'devcontainer', '__init__', 'poetry']):
            categories["configuration"]["files"].append(str(file_path))
        
        # Documentation
        elif filename.endswith('.md') and not any(keyword in filename for keyword in ['proposal', 'presentation']):
            categories["documentation"]["files"].append(str(file_path))
        
        # Legacy files (old analysis, debug files, etc.)
        elif any(keyword in filename for keyword in ['debug', 'precise', 'corrected', 'complete_extraction_audit', 'detailed_analysis']):
            categories["legacy_files"]["files"].append(str(file_path))
        
        # Catch remaining files
        else:
            # Try to categorize by content or put in appropriate category
            if filename.endswith('.py'):
                categories["extraction_tools"]["files"].append(str(file_path))
            elif filename.endswith('.json'):
                categories["extracted_data"]["files"].append(str(file_path))
            elif filename.endswith('.txt'):
                categories["analysis_reports"]["files"].append(str(file_path))
            else:
                categories["legacy_files"]["files"].append(str(file_path))
    
    return categories

def print_analysis(categories):
    """Print the file categorization analysis"""
    
    print("📁 PROJECT FILE ANALYSIS")
    print("=" * 60)
    
    total_files = sum(len(cat["files"]) for cat in categories.values())
    print(f"Total files analyzed: {total_files}")
    print()
    
    for category_name, category_info in categories.items():
        if category_info["files"]:
            print(f"📂 {category_name.replace('_', ' ').title()} ({len(category_info['files'])} files)")
            print(f"   {category_info['description']}")
            for file_path in sorted(category_info["files"]):
                print(f"   • {file_path}")
            print()
    
    return categories

def save_analysis(categories):
    """Save the analysis to a file"""
    
    with open('project_file_analysis.json', 'w') as f:
        json.dump(categories, f, indent=2)
    
    print("✅ Analysis saved to project_file_analysis.json")

def main():
    """Main analysis function"""
    
    categories = analyze_project_files()
    print_analysis(categories)
    save_analysis(categories)
    
    return categories

if __name__ == "__main__":
    main()