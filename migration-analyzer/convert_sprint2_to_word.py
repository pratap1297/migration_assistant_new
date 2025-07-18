#!/usr/bin/env python3
"""
Standalone Sprint 2 Word Document Converter
Converts existing Sprint 2 AS-IS markdown files to professional Word documents
"""

import os
import sys
import argparse
import re
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.sprint2_word_generator import Sprint2WordGenerator
from src.core.models import RepositoryAnalysis

def create_dummy_analysis_from_markdown(markdown_content: str) -> RepositoryAnalysis:
    """Create a minimal RepositoryAnalysis object from markdown content"""
    
    # Extract repository information from markdown
    repo_url = "Unknown Repository"
    analysis_date = datetime.now()
    
    lines = markdown_content.split('\n')
    for line in lines:
        if "**Repository**: " in line:
            repo_url = line.split("**Repository**: ")[1].strip()
        elif "**Analysis Date**: " in line:
            date_str = line.split("**Analysis Date**: ")[1].strip()
            try:
                analysis_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except:
                pass
    
    analysis = RepositoryAnalysis(
        repository_url=repo_url,
        analysis_date=analysis_date
    )
    
    # Extract repo name from URL
    if repo_url and repo_url != "Unknown Repository":
        url_parts = repo_url.rstrip('/').split('/')
        analysis.repo_name = url_parts[-1] if url_parts else 'Unknown'
    else:
        analysis.repo_name = 'Unknown_Repository'
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description='Convert Sprint 2 AS-IS Markdown to Word Document')
    parser.add_argument('--input', type=str, required=True,
                       help='Path to Sprint 2 AS-IS markdown file')
    parser.add_argument('--output', type=str,
                       help='Output directory for Word document (default: same as input)')
    parser.add_argument('--output-name', type=str,
                       help='Custom output filename (without extension)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return
    
    # Read markdown content
    print(f"📖 Reading Sprint 2 AS-IS markdown file: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.dirname(args.input)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine output filename
    if args.output_name:
        filename = f"{args.output_name}.docx"
    else:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_Word_{timestamp}.docx"
    
    output_path = os.path.join(output_dir, filename)
    
    # Create dummy analysis object
    analysis = create_dummy_analysis_from_markdown(markdown_content)
    
    # Generate Word document
    print(f"📝 Generating professional Word document...")
    try:
        generator = Sprint2WordGenerator()
        result_path = generator.generate_as_is_word_document(analysis, output_path)
        print(f"✅ Word document generated successfully!")
        print(f"📄 Output file: {result_path}")
        print(f"📊 File size: {os.path.getsize(result_path) / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error generating Word document: {e}")
        print("Make sure python-docx is installed: pip install python-docx")
        return
    
    print(f"\n🎉 Conversion complete!")
    print(f"   Input:  {args.input}")
    print(f"   Output: {result_path}")
    print(f"\n📋 Document includes:")
    print(f"   - Professional title page")
    print(f"   - Executive summary")
    print(f"   - System overview")
    print(f"   - Component analysis")
    print(f"   - Dependency analysis")
    print(f"   - Criticality assessment")
    print(f"   - Security analysis")
    print(f"   - Architecture insights")
    print(f"   - Migration recommendations")
    print(f"   - Appendices")

if __name__ == '__main__':
    main() 