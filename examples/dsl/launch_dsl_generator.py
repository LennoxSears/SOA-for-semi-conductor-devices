#!/usr/bin/env python3
"""
Launch the SOA DSL Generator in browser
"""

import webbrowser
import os
from pathlib import Path

def launch_dsl_generator():
    """Launch the DSL generator HTML file in browser"""
    
    # Get the path to the HTML file
    html_file = Path(__file__).parent / "dsl_generator.html"
    
    if html_file.exists():
        # Convert to file URL
        file_url = f"file://{html_file.absolute()}"
        
        print("🚀 Launching SOA DSL Generator...")
        print(f"📄 Opening: {file_url}")
        
        # Open in default browser
        webbrowser.open(file_url)
        
        print("✅ DSL Generator opened in browser!")
        print("\n🔧 Features:")
        print("   • Interactive form for all DSL parameters")
        print("   • Example templates (NMOS, PMOS, BJT, Diode)")
        print("   • Real-time DSL generation")
        print("   • Syntax highlighting")
        print("   • Copy to clipboard functionality")
        print("   • tmaxfrac constraint support")
        
    else:
        print(f"❌ HTML file not found: {html_file}")

if __name__ == "__main__":
    launch_dsl_generator()