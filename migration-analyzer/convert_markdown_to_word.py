#!/usr/bin/env python3
"""
Simple Markdown to Word Converter
Converts any markdown file to a professional Word document
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.markdown_to_word_converter import convert_markdown_to_word

def main():
    parser = argparse.ArgumentParser(description='Convert any markdown file to Word document')
    parser.add_argument('--input', type=str, required=True,
                       help='Path to markdown file')
    parser.add_argument('--output', type=str,
                       help='Output directory for Word document (default: same as input)')
    parser.add_argument('--output-name', type=str,
                       help='Custom output filename (without extension)')
    parser.add_argument('--title', type=str,
                       help='Document title (default: extracted from markdown)')
    
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
        filename = f"{base_name}_Word_{timestamp}.docx"
    
    output_path = os.path.join(output_dir, filename)
    
    # Determine document title
    title = args.title
    if not title:
        # Try to extract title from first heading
        lines = markdown_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        if not title:
            title = f"Document - {os.path.basename(args.input)}"
    
    # Generate Word document
    print(f"📝 Converting markdown to Word document...")
    try:
        result_path = convert_markdown_to_word(markdown_content, output_path, title)
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
    print(f"   Title:  {title}")

if __name__ == '__main__':
    main() 