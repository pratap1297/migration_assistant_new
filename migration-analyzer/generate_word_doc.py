#!/usr/bin/env python3
"""
Standalone Word Document Generator for HLD Documents
Converts existing HLD markdown files to professional Word documents
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.synthesis.word_document_generator import WordDocumentGenerator
from src.core.models import RepositoryAnalysis

def create_dummy_analysis(markdown_content: str) -> RepositoryAnalysis:
    """Create a minimal RepositoryAnalysis object for Word generation"""
    # Extract repository name from markdown content
    repo_name = "Unknown Repository"
    lines = markdown_content.split('\n')
    for line in lines:
        if "High-Level Design -" in line:
            repo_name = line.split("High-Level Design -")[1].strip()
            break
    
    analysis = RepositoryAnalysis(
        repository_url=f"https://github.com/{repo_name}",
        analysis_date=datetime.now()
    )
    analysis.repo_name = repo_name
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description='Convert HLD Markdown to Word Document')
    parser.add_argument('--input', type=str, required=True,
                       help='Path to HLD markdown file')
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
    print(f"📖 Reading markdown file: {args.input}")
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
        filename = f"{base_name}_{timestamp}.docx"
    
    output_path = os.path.join(output_dir, filename)
    
    # Create dummy analysis object
    analysis = create_dummy_analysis(markdown_content)
    
    # Create dummy HLD content (not used for Word generation, but required by interface)
    from src.core.models import HLDContent
    hld_content = HLDContent(
        executive_summary="Generated from markdown file",
        scope={},
        target_architecture=None,
        azure_service_mappings=[],
        migration_phases=[],
        technical_decisions={},
        risk_mitigation={},
        cost_analysis={}
    )
    
    # Generate Word document
    print(f"📝 Generating Word document...")
    try:
        generator = WordDocumentGenerator()
        result_path = generator.generate_hld_word_document(
            analysis, hld_content, markdown_content, output_path
        )
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

if __name__ == '__main__':
    main() 