#!/usr/bin/env python3
"""
Design organized directory structure for SOA project
"""

import json
from pathlib import Path

def design_directory_structure():
    """Design the new organized directory structure"""
    
    structure = {
        "docs/": {
            "description": "All documentation and reports",
            "subdirs": {
                "proposal/": "Business proposal and presentation materials",
                "reports/": "Analysis reports and summaries", 
                "guides/": "User guides and technical documentation"
            }
        },
        "src/": {
            "description": "Source code organized by functionality",
            "subdirs": {
                "extraction/": "SOA rule extraction tools and parsers",
                "dsl/": "DSL specification and implementation",
                "validation/": "Validation and testing tools",
                "automation/": "Automation and workflow tools"
            }
        },
        "data/": {
            "description": "All data files organized by type",
            "subdirs": {
                "source/": "Original Excel files and source data",
                "extracted/": "Extracted SOA rules and processed data",
                "mappings/": "Device mappings and pattern configurations",
                "results/": "Final results and generated outputs"
            }
        },
        "assets/": {
            "description": "Visual assets and media files",
            "subdirs": {
                "charts/": "Generated charts and visualizations",
                "diagrams/": "Architecture diagrams and flowcharts"
            }
        },
        "tests/": {
            "description": "Test files and test data",
            "subdirs": {
                "unit/": "Unit tests for individual components",
                "integration/": "Integration tests for workflows",
                "data/": "Test data and fixtures"
            }
        },
        "scripts/": {
            "description": "Utility scripts and automation",
            "subdirs": {
                "setup/": "Project setup and configuration scripts",
                "analysis/": "One-off analysis and debugging scripts"
            }
        },
        "config/": {
            "description": "Configuration files and settings",
            "subdirs": {}
        },
        "examples/": {
            "description": "Example usage and demonstrations",
            "subdirs": {
                "dsl/": "DSL usage examples",
                "extraction/": "Extraction workflow examples"
            }
        }
    }
    
    return structure

def create_file_mapping():
    """Create mapping of current files to new structure"""
    
    # Load the file analysis
    with open('project_file_analysis.json', 'r') as f:
        categories = json.load(f)
    
    file_mapping = {}
    
    # Map files to new structure
    for category, info in categories.items():
        for file_path in info["files"]:
            current_path = file_path
            
            # Determine new location based on file type and content
            if category == "extraction_tools":
                if any(keyword in file_path.lower() for keyword in ['report', 'summary']):
                    new_path = f"docs/reports/{Path(file_path).name}"
                elif file_path.endswith('.py'):
                    new_path = f"src/extraction/{Path(file_path).name}"
                elif file_path.endswith('.txt'):
                    new_path = f"data/results/{Path(file_path).name}"
                else:
                    new_path = f"src/extraction/{Path(file_path).name}"
            
            elif category == "dsl_implementation":
                if file_path.endswith('.md'):
                    new_path = f"docs/proposal/{Path(file_path).name}"
                elif 'test' in file_path:
                    new_path = f"tests/unit/{Path(file_path).name}"
                elif file_path.endswith('.py'):
                    new_path = f"src/dsl/{Path(file_path).name}"
                elif file_path.endswith('.json'):
                    new_path = f"data/results/{Path(file_path).name}"
                else:
                    new_path = f"src/dsl/{Path(file_path).name}"
            
            elif category == "proposal_documents":
                if file_path.endswith('.py'):
                    new_path = f"src/automation/{Path(file_path).name}"
                elif file_path.endswith('.json'):
                    new_path = f"data/results/{Path(file_path).name}"
                else:
                    new_path = f"docs/proposal/{Path(file_path).name}"
            
            elif category == "analysis_reports":
                if file_path.endswith('.py'):
                    new_path = f"scripts/analysis/{Path(file_path).name}"
                elif file_path.endswith('.md'):
                    new_path = f"docs/reports/{Path(file_path).name}"
                else:
                    new_path = f"docs/reports/{Path(file_path).name}"
            
            elif category == "extracted_data":
                if 'mapping' in file_path.lower() or 'pattern' in file_path.lower():
                    new_path = f"data/mappings/{Path(file_path).name}"
                elif any(keyword in file_path.lower() for keyword in ['final', 'enhanced', 'improved']):
                    new_path = f"data/results/{Path(file_path).name}"
                else:
                    new_path = f"data/extracted/{Path(file_path).name}"
            
            elif category == "validation_tools":
                if file_path.endswith('.py'):
                    new_path = f"src/validation/{Path(file_path).name}"
                elif file_path.endswith('.png'):
                    new_path = f"assets/charts/{Path(file_path).name}"
                else:
                    new_path = f"src/validation/{Path(file_path).name}"
            
            elif category == "visualization":
                new_path = f"assets/charts/{Path(file_path).name}"
            
            elif category == "source_data":
                new_path = f"data/source/{Path(file_path).name}"
            
            elif category == "configuration":
                if file_path.endswith('.md'):
                    new_path = f"docs/guides/{Path(file_path).name}"
                elif '__init__' in file_path:
                    # Keep __init__.py files in their current structure
                    new_path = file_path
                else:
                    new_path = f"config/{Path(file_path).name}"
            
            elif category == "documentation":
                new_path = f"docs/{Path(file_path).name}"
            
            elif category == "legacy_files":
                new_path = f"scripts/analysis/{Path(file_path).name}"
            
            else:
                # Default to scripts/analysis for uncategorized files
                new_path = f"scripts/analysis/{Path(file_path).name}"
            
            file_mapping[current_path] = new_path
    
    return file_mapping

def generate_organization_plan():
    """Generate complete organization plan"""
    
    structure = design_directory_structure()
    file_mapping = create_file_mapping()
    
    plan = {
        "directory_structure": structure,
        "file_mapping": file_mapping,
        "organization_steps": [
            "1. Create new directory structure",
            "2. Move files to appropriate locations", 
            "3. Update import statements and references",
            "4. Create index files and documentation",
            "5. Update README and project documentation",
            "6. Clean up empty directories",
            "7. Update configuration files"
        ],
        "benefits": [
            "Clear separation of concerns",
            "Easy navigation and file discovery",
            "Logical grouping of related files",
            "Scalable structure for future growth",
            "Standard project layout conventions",
            "Improved maintainability"
        ]
    }
    
    return plan

def print_organization_plan(plan):
    """Print the organization plan"""
    
    print("🏗️ PROJECT ORGANIZATION PLAN")
    print("=" * 60)
    
    print("\n📁 NEW DIRECTORY STRUCTURE:")
    for dir_name, dir_info in plan["directory_structure"].items():
        print(f"\n{dir_name}")
        print(f"  └── {dir_info['description']}")
        for subdir, subdesc in dir_info["subdirs"].items():
            print(f"      ├── {subdir} - {subdesc}")
    
    print(f"\n📊 FILE MOVEMENTS:")
    print(f"Total files to move: {len(plan['file_mapping'])}")
    
    # Group by target directory
    by_target = {}
    for source, target in plan["file_mapping"].items():
        target_dir = str(Path(target).parent)
        if target_dir not in by_target:
            by_target[target_dir] = []
        by_target[target_dir].append((source, target))
    
    for target_dir in sorted(by_target.keys()):
        files = by_target[target_dir]
        print(f"\n📂 {target_dir}/ ({len(files)} files)")
        for source, target in sorted(files)[:5]:  # Show first 5
            print(f"   • {Path(source).name}")
        if len(files) > 5:
            print(f"   ... and {len(files) - 5} more")
    
    print(f"\n🎯 BENEFITS:")
    for benefit in plan["benefits"]:
        print(f"   • {benefit}")

def save_organization_plan(plan):
    """Save the organization plan"""
    
    with open('project_organization_plan.json', 'w') as f:
        json.dump(plan, f, indent=2)
    
    print(f"\n✅ Organization plan saved to project_organization_plan.json")

def main():
    """Generate organization plan"""
    
    plan = generate_organization_plan()
    print_organization_plan(plan)
    save_organization_plan(plan)
    
    return plan

if __name__ == "__main__":
    main()