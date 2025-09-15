# Poetry Setup and Usage Guide

## 🚀 **Quick Start with Poetry**

### **1. Install Poetry (if not already installed)**

```bash
# On Linux/macOS/WSL
curl -sSL https://install.python-poetry.org | python3 -

# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Alternative: via pip (not recommended for production)
pip install poetry
```

### **2. Clone and Setup Project**

```bash
# Clone the repository
git clone <your-repo-url>
cd SOA-for-semi-conductor-devices

# Install dependencies in virtual environment
poetry install

# Activate the virtual environment
poetry shell
```

### **3. Verify Installation**

```bash
# Check environment info
poetry env info

# Run tests to verify everything works
poetry run pytest

# Run a quick demo
poetry run soa-demo
```

## 📦 **Project Structure with Poetry**

```
SOA-for-semi-conductor-devices/
├── pyproject.toml              # Poetry configuration & dependencies
├── poetry.lock                 # Locked dependency versions
├── src/soa_rules/             # Main package source code
│   ├── __init__.py
│   ├── soa_dsl_implementation.py
│   ├── complete_rule_extractor.py
│   └── ...
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_soa_dsl.py
├── Makefile                   # Convenient commands
└── README.md
```

## 🛠️ **Available Commands**

### **Using Poetry Directly**
```bash
# Install dependencies
poetry install

# Run any script
poetry run python src/soa_rules/complete_rule_extractor.py

# Run tests
poetry run pytest

# Add new dependency
poetry add requests

# Add development dependency
poetry add --group dev black

# Update dependencies
poetry update

# Build package
poetry build
```

### **Using Makefile (Recommended)**
```bash
# Show all available commands
make help

# Install for development
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Extract all SOA rules
make extract

# Run demonstration
make demo

# Validate extraction
make validate

# Format code
make format

# Clean up
make clean
```

## 🔧 **Development Workflow**

### **1. Setup Development Environment**
```bash
# Install with dev dependencies
make install-dev

# Activate shell (optional, commands work without it)
poetry shell
```

### **2. Run SOA Analysis**
```bash
# Extract all rules from Excel
make extract

# Run comprehensive demo
make demo

# Validate extraction completeness
make audit
```

### **3. Testing and Quality**
```bash
# Run tests
make test

# Run with coverage
make test-cov

# Check code formatting
make format-check

# Format code
make format

# Run linting
make lint
```

## 📊 **Key Features with Poetry**

### **Isolated Environment**
- ✅ **No system pollution** - All dependencies in virtual environment
- ✅ **Reproducible builds** - Locked dependency versions
- ✅ **Easy cleanup** - Just delete the project folder

### **Convenient Scripts**
```bash
# These commands are available after `poetry install`
soa-extract     # Extract all SOA rules
soa-demo        # Run demonstration
soa-validate    # Validate extraction
soa-audit       # Audit completeness
```

### **Package Management**
```bash
# Add runtime dependency
poetry add pandas

# Add development tool
poetry add --group dev pytest

# Remove dependency
poetry remove requests

# Show dependency tree
poetry show --tree
```

## 🎯 **Usage Examples**

### **Extract SOA Rules**
```bash
# Method 1: Using make
make extract

# Method 2: Using poetry script
poetry run soa-extract

# Method 3: Direct execution
poetry run python src/soa_rules/complete_rule_extractor.py
```

### **Run Demonstrations**
```bash
# Full feature demo
make demo

# Transient time validation demo
poetry run python src/soa_rules/corrected_tmaxfrac_analysis.py
```

### **Validate Results**
```bash
# Validate extraction against Excel
make validate

# Audit extraction completeness
make audit
```

## 🔍 **Troubleshooting**

### **Poetry Not Found**
```bash
# Add to PATH (Linux/macOS)
export PATH="$HOME/.local/bin:$PATH"

# Restart terminal or source profile
source ~/.bashrc  # or ~/.zshrc
```

### **Virtual Environment Issues**
```bash
# Show environment info
poetry env info

# Remove and recreate environment
poetry env remove python
poetry install
```

### **Dependency Conflicts**
```bash
# Update lock file
poetry lock --no-update

# Force update
poetry update

# Clear cache
poetry cache clear pypi --all
```

## 🚀 **Production Deployment**

### **Build Package**
```bash
# Build wheel and source distribution
poetry build

# Install built package
pip install dist/soa_semiconductor_rules-1.0.0-py3-none-any.whl
```

### **Export Requirements**
```bash
# Export for pip-based systems
poetry export -f requirements.txt --output requirements.txt

# Export with dev dependencies
poetry export -f requirements.txt --dev --output requirements-dev.txt
```

## ✅ **Benefits of Poetry Setup**

1. **🔒 Isolation** - No impact on system Python or other projects
2. **📦 Dependency Management** - Automatic resolution and locking
3. **🛠️ Development Tools** - Integrated testing, linting, formatting
4. **🚀 Easy Distribution** - Build and publish packages easily
5. **🔄 Reproducible** - Same environment across all machines
6. **🧹 Clean** - Easy to remove completely

**Your local machine stays clean** - all dependencies are contained within the project's virtual environment!