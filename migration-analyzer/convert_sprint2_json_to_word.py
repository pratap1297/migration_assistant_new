#!/usr/bin/env python3
"""
Convert Sprint 2 JSON analysis to a professional Word document
"""
import os
import sys
import argparse
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.markdown_to_word_converter import convert_markdown_to_word
from src.core.models import RepositoryAnalysis, ComponentInfo, ServiceDependency, ServiceCriticality, SecurityFindings

def load_analysis_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Parse metadata
    metadata = data.get('metadata', {})
    repo_url = metadata.get('repository_url', 'Unknown')
    analysis_date = metadata.get('analysis_date', datetime.now().isoformat())
    try:
        analysis_date = datetime.fromisoformat(analysis_date)
    except Exception:
        analysis_date = datetime.now()

    # Parse components
    components = []
    for comp in data.get('components', []):
        components.append(ComponentInfo(
            name=comp.get('name'),
            path=comp.get('path'),
            language=comp.get('language'),
            files_count=comp.get('files_count', 0),
            lines_of_code=comp.get('lines_of_code', 0),
            api_endpoints_count=comp.get('api_endpoints_count', 0),
            database_operations_count=comp.get('database_operations_count', 0),
            http_calls_count=comp.get('http_calls_count', 0),
            criticality=None  # Will be set later
        ))

    # Parse dependencies
    dependencies = []
    for dep in data.get('dependencies', []):
        dependencies.append(ServiceDependency(
            source_component=dep.get('source_component'),
            target_component=dep.get('target_component'),
            dependency_type=dep.get('dependency_type'),
            endpoint=dep.get('endpoint', None)
        ))

    # Parse criticality assessments
    criticality_assessments = []
    for crit in data.get('criticality_assessments', []):
        criticality_assessments.append(ServiceCriticality(
            component_name=crit.get('component_name'),
            business_criticality=crit.get('business_criticality'),
            technical_complexity=crit.get('technical_complexity'),
            user_impact=crit.get('user_impact'),
            data_sensitivity=crit.get('data_sensitivity'),
            reasoning=crit.get('reasoning'),
            score=crit.get('score', 0.0)
        ))

    # Attach criticality to components
    crit_map = {c.component_name: c for c in criticality_assessments}
    for comp in components:
        if comp.name in crit_map:
            comp.criticality = crit_map[comp.name]

    # Parse security findings
    security_findings = []
    for finding in data.get('security_findings', []):
        security_findings.append(SecurityFindings(
            component_name=finding.get('component_name'),
            issue_type=finding.get('issue_type'),
            severity=finding.get('severity'),
            description=finding.get('description')
        ))

    # Other fields
    semantic_maps = data.get('semantic_maps', [])
    architecture_insights = data.get('architecture_insights', [])
    migration_recommendations = data.get('migration_recommendations', [])

    # Build RepositoryAnalysis
    analysis = RepositoryAnalysis(
        repository_url=repo_url,
        analysis_date=analysis_date,
        components=components,
        dependencies=dependencies,
        criticality_assessments=criticality_assessments,
        semantic_maps=semantic_maps,
        security_findings=security_findings,
        architecture_insights=architecture_insights,
        migration_recommendations=migration_recommendations
    )
    return analysis

def main():
    parser = argparse.ArgumentParser(description='Convert Sprint 2 JSON analysis to Word document')
    parser.add_argument('--input', type=str, required=True, help='Path to sprint2_analysis.json')
    parser.add_argument('--output', type=str, help='Output directory for Word document (default: same as input)')
    parser.add_argument('--output-name', type=str, help='Custom output filename (without extension)')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'❌ Input file not found: {args.input}')
        return

    print(f'📖 Loading Sprint 2 analysis JSON: {args.input}')
    analysis = load_analysis_from_json(args.input)

    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.dirname(args.input)
    os.makedirs(output_dir, exist_ok=True)

    # Determine output filename
    if args.output_name:
        filename = f'{args.output_name}.docx'
    else:
        repo_name = getattr(analysis, 'repo_name', None)
        if not repo_name and hasattr(analysis, 'repository_url'):
            url_parts = analysis.repository_url.rstrip('/').split('/')
            repo_name = url_parts[-1] if url_parts else 'Unknown'
        if not repo_name:
            repo_name = 'Unknown_Repository'
        repo_name = repo_name[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ASIS_Analysis_{repo_name}_{timestamp}.docx'
    output_path = os.path.join(output_dir, filename)

    print(f'📝 Generating professional Word document...')
    try:
        # First, generate the markdown content using the enhanced document generator
        from src.analysis.enhanced_document_generator import EnhancedDocumentGenerator
        
        doc_generator = EnhancedDocumentGenerator()
        markdown_content = doc_generator._generate_document_content(analysis)
        
        # Convert markdown to Word
        result_path = convert_markdown_to_word(markdown_content, output_path, f"AS-IS Analysis - {getattr(analysis, 'repo_name', 'Unknown Repository')}")
        
        print(f'✅ Word document generated successfully!')
        print(f'📄 Output file: {result_path}')
        print(f'📊 File size: {os.path.getsize(result_path) / 1024:.1f} KB')
    except Exception as e:
        print(f'❌ Error generating Word document: {e}')
        print('Make sure python-docx is installed: pip install python-docx')
        return
    print(f'\n🎉 Conversion complete!')
    print(f'   Input:  {args.input}')
    print(f'   Output: {result_path}')

if __name__ == '__main__':
    main() 