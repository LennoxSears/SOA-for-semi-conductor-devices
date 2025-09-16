#!/usr/bin/env python3
"""
Generate PDF files for all proposal materials
"""

import os
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime

class PDFGenerator:
    """Generate PDFs from markdown files using system tools"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "pdfs"
        self.output_dir.mkdir(exist_ok=True)
        
    def check_dependencies(self):
        """Check if required tools are available"""
        
        tools = {
            'pandoc': 'pandoc --version',
            'wkhtmltopdf': 'wkhtmltopdf --version'
        }
        
        available_tools = {}
        
        for tool, check_cmd in tools.items():
            try:
                result = subprocess.run(check_cmd.split(), 
                                      capture_output=True, text=True)
                available_tools[tool] = result.returncode == 0
            except FileNotFoundError:
                available_tools[tool] = False
        
        return available_tools
    
    def create_html_from_markdown(self, md_file, output_file):
        """Convert markdown to HTML with styling"""
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create HTML with CSS styling
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SOA Automation Proposal</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #2980b9;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            font-style: italic;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }}
        .page-break {{
            page-break-before: always;
        }}
        @media print {{
            body {{
                margin: 0;
                padding: 15px;
            }}
            .page-break {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body>
"""
        
        # Simple markdown to HTML conversion
        html_body = self.markdown_to_html(content)
        html_content += html_body + "\n</body>\n</html>"
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def markdown_to_html(self, content):
        """Simple markdown to HTML conversion"""
        
        lines = content.split('\n')
        html_lines = []
        in_code_block = False
        in_table = False
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append('</pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre><code>')
                    in_code_block = True
                continue
            
            if in_code_block:
                html_lines.append(line)
                continue
            
            # Handle headers
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('#### '):
                html_lines.append(f'<h4>{line[5:]}</h4>')
            
            # Handle tables
            elif '|' in line and line.strip():
                if not in_table:
                    html_lines.append('<table>')
                    in_table = True
                
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if all(cell.replace('-', '').replace(' ', '') == '' for cell in cells):
                    # Table separator row, skip
                    continue
                
                row_html = '<tr>'
                for cell in cells:
                    if cell.startswith('**') and cell.endswith('**'):
                        row_html += f'<th>{cell[2:-2]}</th>'
                    else:
                        row_html += f'<td>{cell}</td>'
                row_html += '</tr>'
                html_lines.append(row_html)
            
            # Handle lists
            elif line.strip().startswith('- '):
                if not html_lines or not html_lines[-1].startswith('<ul>'):
                    html_lines.append('<ul>')
                html_lines.append(f'<li>{line.strip()[2:]}</li>')
            elif line.strip().startswith('* '):
                if not html_lines or not html_lines[-1].startswith('<ul>'):
                    html_lines.append('<ul>')
                html_lines.append(f'<li>{line.strip()[2:]}</li>')
            
            # Handle bold text
            elif '**' in line:
                line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                html_lines.append(f'<p>{line}</p>')
            
            # Handle regular paragraphs
            elif line.strip():
                if in_table:
                    html_lines.append('</table>')
                    in_table = False
                html_lines.append(f'<p>{line}</p>')
            
            # Handle empty lines
            else:
                if in_table:
                    html_lines.append('</table>')
                    in_table = False
                if html_lines and html_lines[-1].startswith('<ul>'):
                    html_lines.append('</ul>')
                html_lines.append('<br>')
        
        # Close any open tags
        if in_table:
            html_lines.append('</table>')
        if html_lines and html_lines[-1].startswith('<ul>'):
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    def html_to_pdf_chrome(self, html_file, pdf_file):
        """Convert HTML to PDF using Chrome/Chromium headless"""
        
        try:
            # Try different Chrome/Chromium commands
            chrome_commands = [
                'google-chrome',
                'chromium-browser', 
                'chromium',
                'chrome'
            ]
            
            for chrome_cmd in chrome_commands:
                try:
                    cmd = [
                        chrome_cmd,
                        '--headless',
                        '--disable-gpu',
                        '--print-to-pdf=' + str(pdf_file),
                        '--print-to-pdf-no-header',
                        '--no-margins',
                        str(html_file)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                        
                except FileNotFoundError:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Error with Chrome PDF generation: {e}")
            return False
    
    def html_to_pdf_wkhtmltopdf(self, html_file, pdf_file):
        """Convert HTML to PDF using wkhtmltopdf"""
        
        try:
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '0.75in',
                '--margin-right', '0.75in',
                '--margin-bottom', '0.75in',
                '--margin-left', '0.75in',
                '--encoding', 'UTF-8',
                '--print-media-type',
                str(html_file),
                str(pdf_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error with wkhtmltopdf: {e}")
            return False
    
    def generate_pdf_from_markdown(self, md_file, pdf_name):
        """Generate PDF from markdown file"""
        
        print(f"📄 Generating PDF: {pdf_name}")
        
        # Create HTML file
        html_file = self.output_dir / f"{pdf_name}.html"
        self.create_html_from_markdown(md_file, html_file)
        
        # Create PDF file
        pdf_file = self.output_dir / f"{pdf_name}.pdf"
        
        # Try different PDF generation methods
        success = False
        
        # Method 1: Chrome headless
        if self.html_to_pdf_chrome(html_file, pdf_file):
            success = True
            print(f"   ✅ Generated using Chrome: {pdf_file}")
        
        # Method 2: wkhtmltopdf
        elif self.html_to_pdf_wkhtmltopdf(html_file, pdf_file):
            success = True
            print(f"   ✅ Generated using wkhtmltopdf: {pdf_file}")
        
        # Method 3: Keep HTML as fallback
        else:
            print(f"   ⚠️ PDF generation failed, HTML available: {html_file}")
            success = False
        
        # Clean up HTML file if PDF was successful
        if success and html_file.exists():
            html_file.unlink()
        
        return success
    
    def create_presentation_package(self):
        """Create a complete presentation package"""
        
        print("📦 Creating presentation package...")
        
        # Create package directory
        package_dir = self.output_dir / "presentation_package"
        package_dir.mkdir(exist_ok=True)
        
        # Copy key files
        files_to_copy = [
            ("docs/proposal/SOA_DSL_Presentation.md", "Executive_Presentation.md"),
            ("docs/proposal/SOA_DSL_Proposal.md", "Detailed_Proposal.md"),
            ("QUICK_START.md", "Quick_Start_Guide.md"),
            ("PROJECT_INDEX.md", "Project_Navigation.md"),
            ("assets/charts/soa_roi_timeline.png", "ROI_Timeline_Chart.png"),
            ("assets/charts/soa_automation_comparison.png", "Automation_Comparison_Chart.png"),
            ("data/results/final_soa_device_rules.json", "Extracted_SOA_Rules.json")
        ]
        
        for source, dest in files_to_copy:
            source_path = self.project_root / source
            dest_path = package_dir / dest
            
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"   📄 Copied: {dest}")
        
        # Create package README
        package_readme = package_dir / "README.md"
        with open(package_readme, 'w') as f:
            f.write(self.create_package_readme())
        
        print(f"   ✅ Package created: {package_dir}")
        return package_dir
    
    def create_package_readme(self):
        """Create README for presentation package"""
        
        return f"""# SOA Automation Proposal - Presentation Package

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Package Contents

### 📊 Executive Materials
- **Executive_Presentation.pdf** - 20-slide executive presentation
- **ROI_Timeline_Chart.png** - 5-year ROI projection
- **Automation_Comparison_Chart.png** - Current vs automated workflow

### 📖 Detailed Documentation  
- **Detailed_Proposal.pdf** - Complete 20-page technical proposal
- **Quick_Start_Guide.pdf** - 5-minute overview
- **Project_Navigation.pdf** - Complete project index

### 📊 Supporting Data
- **Extracted_SOA_Rules.json** - 277 extracted parameters (vs 34 original)

## 🎯 Presentation Flow

### For Executive Briefing (15 minutes)
1. **Executive_Presentation.pdf** - Main presentation
2. **ROI_Timeline_Chart.png** - Visual ROI impact
3. **Quick_Start_Guide.pdf** - Implementation overview

### For Technical Deep Dive (45 minutes)
1. **Detailed_Proposal.pdf** - Complete technical case
2. **Extracted_SOA_Rules.json** - Demonstration of results
3. **Project_Navigation.pdf** - Implementation roadmap

## 💰 Key Business Points

- **98% Time Reduction**: 1,228 hours → 25 hours per rule set
- **$485K Annual Savings**: Reduced engineering overhead  
- **4.7-Month Payback**: Rapid return on investment
- **8.1x Parameter Coverage**: 277 vs 34 parameters extracted

## 🔧 Technical Highlights

- **Unified DSL**: Single language for all SOA rule types
- **Automated Toolchain**: Excel → DSL → Simulation code
- **6 Device Types**: Comprehensive semiconductor coverage
- **Pattern Recognition**: Handles arbitrary Excel formats

## 📞 Next Steps

1. **Executive Approval**: Present business case
2. **Technical Review**: Detailed architecture discussion
3. **Pilot Planning**: Select initial device type
4. **Implementation**: 3-phase rollout over 12 months

---

*This package contains everything needed to present the SOA automation business case and secure approval for implementation.*
"""

def main():
    """Main PDF generation function"""
    
    print("🎯 SOA PROPOSAL PDF GENERATION")
    print("=" * 60)
    
    generator = PDFGenerator()
    
    # Check available tools
    tools = generator.check_dependencies()
    print("🔧 Available tools:")
    for tool, available in tools.items():
        status = "✅" if available else "❌"
        print(f"   {status} {tool}")
    
    # Generate PDFs for key documents
    documents = [
        ("docs/proposal/SOA_DSL_Presentation.md", "Executive_Presentation"),
        ("docs/proposal/SOA_DSL_Proposal.md", "Detailed_Proposal"), 
        ("QUICK_START.md", "Quick_Start_Guide"),
        ("PROJECT_INDEX.md", "Project_Navigation"),
        ("CHANGELOG.md", "Project_History")
    ]
    
    generated_pdfs = []
    
    for md_file, pdf_name in documents:
        md_path = generator.project_root / md_file
        if md_path.exists():
            if generator.generate_pdf_from_markdown(md_path, pdf_name):
                generated_pdfs.append(pdf_name)
        else:
            print(f"   ❌ File not found: {md_file}")
    
    # Create presentation package
    package_dir = generator.create_presentation_package()
    
    print(f"\n🎯 PDF GENERATION COMPLETE")
    print("=" * 60)
    print(f"📁 Output directory: {generator.output_dir}")
    print(f"📦 Presentation package: {package_dir}")
    print(f"📄 Generated PDFs: {len(generated_pdfs)}")
    
    for pdf in generated_pdfs:
        print(f"   • {pdf}.pdf")
    
    print(f"\n✅ Ready for presentation!")
    print(f"   Use files in: {package_dir}")

if __name__ == "__main__":
    main()