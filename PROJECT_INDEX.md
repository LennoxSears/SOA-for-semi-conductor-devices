# SOA Project Index

Complete navigation guide for the SOA Rules for Semiconductor Devices project.

## 📁 Directory Structure

### 📚 Documentation (`docs/`)
- **[Main README](docs/README.md)** - Project overview and quick start
- **[Business Proposal](docs/proposal/SOA_DSL_Proposal.md)** - Complete 20-page technical and business proposal
- **[Executive Presentation](docs/proposal/SOA_DSL_Presentation.md)** - 20-slide PowerPoint-style presentation
- **[Analysis Reports](docs/reports/)** - Detailed extraction and validation reports
- **[Setup Guide](docs/guides/POETRY_SETUP.md)** - Environment setup instructions

### 💻 Source Code (`src/`)

#### Extraction Tools (`src/extraction/`)
- **[Enhanced Extractor](src/extraction/enhanced_extractor.py)** - Main extraction tool (277 parameters)
- **[Improved tmaxfrac Extractor](src/extraction/improved_tmaxfrac_extractor.py)** - Focused tmaxfrac extraction
- **[Simple Device Mapper](src/extraction/simple_device_mapper.py)** - Device mapping generator
- **[Excel to DSL Converter](src/extraction/excel_to_dsl_converter.py)** - Convert Excel to DSL format
- **[Final Results Generator](src/extraction/final_results_generator.py)** - Generate final organized results

#### DSL Implementation (`src/dsl/`)
- **[DSL Specification](src/dsl/soa_dsl_specification.py)** - Complete DSL language specification
- **[DSL Implementation](src/dsl/soa_dsl_implementation.py)** - Core DSL engine and validation
- **[DSL Demo](src/dsl/demo_soa_dsl.py)** - Demonstration of DSL capabilities

#### Validation Tools (`src/validation/`)
- **[Validation Comparison](src/validation/validation_comparison.py)** - Compare extraction methods
- **[Test Single Sheet](src/validation/test_single_sheet.py)** - Debug individual sheet extraction

#### Automation Tools (`src/automation/`)
- **[Automation Benefits Analysis](src/automation/automation_benefits_analysis.py)** - ROI and benefits calculation
- **[Implementation Architecture](src/automation/implementation_architecture.py)** - Toolchain architecture design
- **[Workflow Analysis](src/automation/workflow_analysis.py)** - Current workflow analysis

### 📊 Data Files (`data/`)

#### Source Data (`data/source/`)
- **[SMOS10HV Excel File](data/source/SMOS10HV_SOA_Multi_PlusSmoke_Update_EngrRel_v3.17ER_06122025\ \ 2.xlsx)** - Original SOA rules Excel file

#### Extracted Data (`data/extracted/`)
- **[Complete SOA Rules](data/extracted/complete_soa_rules.json)** - All 744 extracted parameters
- **[Device Grouped Rules](data/extracted/device_grouped_soa_rules.json)** - Original 34-parameter extraction
- **[SOA Rules](data/extracted/soa_rules.json)** - Basic rule extraction

#### Mappings (`data/mappings/`)
- **[Simple Device Mapping](data/mappings/simple_device_mapping.json)** - Device type mappings
- **[Pattern Mapping](data/mappings/pattern_mapping.json)** - Excel pattern configurations

#### Results (`data/results/`)
- **[Final SOA Device Rules](data/results/final_soa_device_rules.json)** - Final organized results (277 parameters)
- **[Enhanced Device Rules](data/results/enhanced_device_grouped_rules.json)** - Enhanced extraction results
- **[DSL Specification](data/results/soa_dsl_specification.json)** - Complete DSL specification
- **[Toolchain Architecture](data/results/soa_toolchain_architecture.json)** - Implementation architecture
- **[Automation Analysis](data/results/soa_automation_analysis.json)** - ROI and benefits analysis

### 📈 Visual Assets (`assets/`)
- **[Automation Comparison Chart](assets/charts/soa_automation_comparison.png)** - Current vs automated workflow
- **[ROI Timeline Chart](assets/charts/soa_roi_timeline.png)** - 5-year ROI projection

### 🧪 Tests (`tests/`)
- **[DSL Tests](tests/unit/test_soa_dsl.py)** - Unit tests for DSL implementation

### 🔧 Scripts (`scripts/`)
- **[Setup Scripts](scripts/setup/)** - Project organization and setup tools
- **[Analysis Scripts](scripts/analysis/)** - One-off analysis and debugging tools

## 🎯 Key Entry Points

### For Business Stakeholders
1. **[Executive Summary](docs/proposal/SOA_DSL_Presentation.md)** - Start here for business case
2. **[ROI Analysis](assets/charts/soa_roi_timeline.png)** - Visual ROI projection
3. **[Business Proposal](docs/proposal/SOA_DSL_Proposal.md)** - Complete business case

### For Technical Teams
1. **[Main README](docs/README.md)** - Technical overview and quick start
2. **[Enhanced Extractor](src/extraction/enhanced_extractor.py)** - Main extraction tool
3. **[DSL Implementation](src/dsl/soa_dsl_implementation.py)** - Core DSL engine
4. **[Final Results](data/results/final_soa_device_rules.json)** - Complete extracted data

### For Implementation Planning
1. **[Implementation Architecture](src/automation/implementation_architecture.py)** - Technical architecture
2. **[Automation Benefits](src/automation/automation_benefits_analysis.py)** - ROI calculations
3. **[Workflow Analysis](src/automation/workflow_analysis.py)** - Current state analysis

## 📊 Project Metrics

### Extraction Performance
- **Original Method**: 34 parameters from 4 devices
- **Enhanced Method**: 277 parameters from 13 devices
- **Improvement**: 8.1x parameter increase, 714.7% coverage improvement

### Business Impact
- **Time Reduction**: 98% (1,228 hours → 25 hours per rule set)
- **Annual Savings**: $485,200
- **Payback Period**: 4.7 months
- **3-Year ROI**: 656%

### Technical Coverage
- **Device Types**: 6 (MOS, BJT, Diodes, Capacitors, Substrate, Oxide)
- **Rule Types**: Simple numeric, equations, functions, tmaxfrac, conditional
- **Validation**: Comprehensive error checking and validation

## 🚀 Quick Navigation

### Want to understand the business case?
→ [Executive Presentation](docs/proposal/SOA_DSL_Presentation.md)

### Want to see the technical solution?
→ [DSL Implementation](src/dsl/soa_dsl_implementation.py)

### Want to run the extraction?
→ [Enhanced Extractor](src/extraction/enhanced_extractor.py)

### Want to see the results?
→ [Final Results](data/results/final_soa_device_rules.json)

### Want to understand the ROI?
→ [Automation Benefits Analysis](src/automation/automation_benefits_analysis.py)

### Want to implement the solution?
→ [Implementation Architecture](src/automation/implementation_architecture.py)

## 📞 Getting Help

1. **Technical Questions**: Check the source code documentation
2. **Business Questions**: Review the proposal documents
3. **Implementation Questions**: Consult the architecture documents
4. **Data Questions**: Examine the results and analysis files

---

*This index provides complete navigation for all aspects of the SOA automation project, from business case to technical implementation.*