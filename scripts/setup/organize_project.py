#!/usr/bin/env python3
"""
Organize the project by creating directories and moving files
"""

import json
import shutil
from pathlib import Path
import os

def load_organization_plan():
    """Load the organization plan"""
    with open('project_organization_plan.json', 'r') as f:
        return json.load(f)

def create_directory_structure(structure):
    """Create the new directory structure"""
    
    print("📁 Creating directory structure...")
    
    created_dirs = []
    
    for dir_name, dir_info in structure.items():
        # Create main directory
        main_dir = Path(dir_name)
        main_dir.mkdir(exist_ok=True)
        created_dirs.append(str(main_dir))
        
        # Create subdirectories
        for subdir_name in dir_info["subdirs"].keys():
            sub_dir = main_dir / subdir_name
            sub_dir.mkdir(exist_ok=True)
            created_dirs.append(str(sub_dir))
    
    print(f"✅ Created {len(created_dirs)} directories")
    return created_dirs

def move_files(file_mapping):
    """Move files according to the mapping"""
    
    print("\n📦 Moving files to new locations...")
    
    moved_files = []
    errors = []
    
    for source_path, target_path in file_mapping.items():
        try:
            source = Path(source_path)
            target = Path(target_path)
            
            # Skip if source doesn't exist
            if not source.exists():
                continue
            
            # Skip if it's the same location
            if source.resolve() == target.resolve():
                continue
            
            # Create target directory if it doesn't exist
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            if target.exists():
                # If target exists, backup the original
                backup_path = target.with_suffix(target.suffix + '.backup')
                if backup_path.exists():
                    backup_path.unlink()
                target.rename(backup_path)
                print(f"   ⚠️ Backed up existing {target} to {backup_path}")
            
            shutil.move(str(source), str(target))
            moved_files.append((str(source), str(target)))
            
        except Exception as e:
            errors.append((source_path, target_path, str(e)))
            print(f"   ❌ Error moving {source_path}: {e}")
    
    print(f"✅ Moved {len(moved_files)} files")
    if errors:
        print(f"⚠️ {len(errors)} errors occurred")
    
    return moved_files, errors

def create_init_files():
    """Create __init__.py files for Python packages"""
    
    print("\n🐍 Creating __init__.py files...")
    
    python_dirs = [
        "src",
        "src/extraction", 
        "src/dsl",
        "src/validation",
        "src/automation",
        "tests",
        "tests/unit",
        "tests/integration"
    ]
    
    created_inits = []
    
    for dir_path in python_dirs:
        init_file = Path(dir_path) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            created_inits.append(str(init_file))
    
    print(f"✅ Created {len(created_inits)} __init__.py files")
    return created_inits

def create_directory_readme_files():
    """Create README files for each major directory"""
    
    print("\n📝 Creating directory README files...")
    
    readme_content = {
        "docs": """# Documentation

This directory contains all project documentation.

## Structure

- `proposal/` - Business proposal and presentation materials
- `reports/` - Analysis reports and summaries  
- `guides/` - User guides and technical documentation

## Files

- `README.md` - Main project documentation
""",
        "src": """# Source Code

This directory contains all source code organized by functionality.

## Structure

- `extraction/` - SOA rule extraction tools and parsers
- `dsl/` - DSL specification and implementation
- `validation/` - Validation and testing tools
- `automation/` - Automation and workflow tools

## Usage

Import modules using the package structure:
```python
from src.extraction import enhanced_extractor
from src.dsl import soa_dsl_implementation
```
""",
        "data": """# Data Files

This directory contains all data files organized by type.

## Structure

- `source/` - Original Excel files and source data
- `extracted/` - Extracted SOA rules and processed data
- `mappings/` - Device mappings and pattern configurations
- `results/` - Final results and generated outputs

## File Types

- `.xlsx` - Original Excel SOA rule files
- `.json` - Extracted and processed rule data
- `.txt` - Log files and summaries
""",
        "assets": """# Assets

This directory contains visual assets and media files.

## Structure

- `charts/` - Generated charts and visualizations
- `diagrams/` - Architecture diagrams and flowcharts

## File Types

- `.png` - Chart images and visualizations
- `.svg` - Vector graphics and diagrams
""",
        "tests": """# Tests

This directory contains test files and test data.

## Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for workflows
- `data/` - Test data and fixtures

## Running Tests

```bash
python -m pytest tests/
```
""",
        "scripts": """# Scripts

This directory contains utility scripts and automation.

## Structure

- `setup/` - Project setup and configuration scripts
- `analysis/` - One-off analysis and debugging scripts

## Usage

Run scripts from the project root:
```bash
python scripts/setup/setup_environment.py
```
""",
        "config": """# Configuration

This directory contains configuration files and settings.

## Files

Configuration files for various tools and environments.
""",
        "examples": """# Examples

This directory contains example usage and demonstrations.

## Structure

- `dsl/` - DSL usage examples
- `extraction/` - Extraction workflow examples

## Usage

Run examples to understand how to use the tools:
```bash
python examples/dsl/basic_usage.py
```
"""
    }
    
    created_readmes = []
    
    for dir_name, content in readme_content.items():
        readme_path = Path(dir_name) / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(content)
            created_readmes.append(str(readme_path))
    
    print(f"✅ Created {len(created_readmes)} README files")
    return created_readmes

def clean_empty_directories():
    """Remove empty directories from the old structure"""
    
    print("\n🧹 Cleaning up empty directories...")
    
    # Don't remove these important directories
    keep_dirs = {'.git', '.devcontainer', 'src', 'tests', 'docs', 'data', 'assets', 'scripts', 'config', 'examples'}
    
    removed_dirs = []
    
    # Find empty directories
    for item in Path('.').iterdir():
        if item.is_dir() and item.name not in keep_dirs:
            try:
                # Check if directory is empty
                if not any(item.iterdir()):
                    item.rmdir()
                    removed_dirs.append(str(item))
            except OSError:
                # Directory not empty or permission error
                pass
    
    print(f"✅ Removed {len(removed_dirs)} empty directories")
    return removed_dirs

def generate_organization_summary(moved_files, created_dirs, created_inits, created_readmes):
    """Generate a summary of the organization process"""
    
    summary = {
        "organization_date": "2025-09-15",
        "statistics": {
            "directories_created": len(created_dirs),
            "files_moved": len(moved_files),
            "init_files_created": len(created_inits),
            "readme_files_created": len(created_readmes)
        },
        "new_structure": {
            "docs/": "Documentation and reports",
            "src/": "Source code by functionality", 
            "data/": "Data files by type",
            "assets/": "Visual assets and media",
            "tests/": "Test files and data",
            "scripts/": "Utility scripts",
            "config/": "Configuration files",
            "examples/": "Usage examples"
        },
        "benefits_achieved": [
            "Clear separation of concerns",
            "Logical file grouping",
            "Easy navigation",
            "Standard project layout",
            "Improved maintainability"
        ]
    }
    
    with open('organization_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def main():
    """Main organization function"""
    
    print("🏗️ ORGANIZING SOA PROJECT")
    print("=" * 60)
    
    # Load the organization plan
    plan = load_organization_plan()
    
    # Create directory structure
    created_dirs = create_directory_structure(plan["directory_structure"])
    
    # Move files
    moved_files, errors = move_files(plan["file_mapping"])
    
    # Create __init__.py files
    created_inits = create_init_files()
    
    # Create README files
    created_readmes = create_directory_readme_files()
    
    # Clean up empty directories
    removed_dirs = clean_empty_directories()
    
    # Generate summary
    summary = generate_organization_summary(moved_files, created_dirs, created_inits, created_readmes)
    
    print(f"\n🎯 ORGANIZATION COMPLETE!")
    print("=" * 60)
    print(f"📁 Directories created: {summary['statistics']['directories_created']}")
    print(f"📦 Files moved: {summary['statistics']['files_moved']}")
    print(f"🐍 Init files created: {summary['statistics']['init_files_created']}")
    print(f"📝 README files created: {summary['statistics']['readme_files_created']}")
    
    if errors:
        print(f"\n⚠️ {len(errors)} errors occurred during file moves")
        for source, target, error in errors:
            print(f"   • {source} → {target}: {error}")
    
    print(f"\n✅ Project successfully organized!")
    print(f"📄 Summary saved to organization_summary.json")

if __name__ == "__main__":
    main()