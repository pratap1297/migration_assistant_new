#!/usr/bin/env python3
"""
Sprint 3 HLD Generation Runner - Simplified Version
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List
import pickle

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.models import RepositoryAnalysis
from src.synthesis.azure_mapper import AzureServiceMapper
from src.synthesis.hld_synthesizer import HLDSynthesizer
from src.synthesis.hld_document_generator import HLDDocumentGenerator
from src.synthesis.word_document_generator import generate_hld_word_document

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def load_sprint2_data(file_path: str) -> RepositoryAnalysis:
    """Load Sprint 2 analysis data"""
    if file_path.endswith('.pkl'):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    elif file_path.endswith('.json'):
        # Load from JSON and convert to RepositoryAnalysis
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Create a simplified RepositoryAnalysis from JSON data
        from src.core.models import ComponentInfo, ServiceCriticality
        
        analysis = RepositoryAnalysis(
            repository_url=data['metadata']['repository_url'],
            analysis_date=datetime.fromisoformat(data['metadata']['analysis_date'])
        )
        
        # Convert components
        components = {}
        for comp_data in data['components']:
            # Create criticality if available
            criticality = None
            for crit_data in data['criticality_assessments']:
                if crit_data['component_name'] == comp_data['name']:
                    criticality = ServiceCriticality(
                        component_name=crit_data['component_name'],
                        business_criticality=crit_data['business_criticality'],
                        technical_complexity=crit_data['technical_complexity'],
                        user_impact=crit_data['user_impact'],
                        data_sensitivity=crit_data['data_sensitivity'],
                        reasoning=crit_data['reasoning'],
                        score=crit_data['score']
                    )
                    break
            
            # Create component
            component = ComponentInfo(
                name=comp_data['name'],
                path=comp_data['path'],
                language=comp_data['language'],
                files_count=comp_data['files_count'],
                lines_of_code=comp_data['lines_of_code'],
                api_endpoints_count=comp_data['api_endpoints_count'],
                database_operations_count=comp_data['database_operations_count'],
                http_calls_count=comp_data['http_calls_count'],
                criticality=criticality
            )
            components[comp_data['name']] = component
        
        analysis.components = components
        analysis.architecture_insights = data.get('architecture_insights', [])
        analysis.migration_recommendations = data.get('migration_recommendations', [])
        
        return analysis
    else:
        raise ValueError("Unsupported file format. Please provide .pkl or .json file")

def save_hld_data(hld_content, service_mappings, output_path: str):
    """Save HLD data for future use"""
    hld_summary = {
        'generation_date': datetime.now().isoformat(),
        'service_mappings': [
            {
                'component': m.component_name,
                'current_tech': m.current_technology,
                'target_service': m.target_azure_service,
                'tier': m.azure_service_tier,
                'complexity': m.migration_complexity,
                'cost': m.estimated_cost_range
            }
            for m in service_mappings
        ],
        'migration_phases': [
            {
                'phase': p.phase_number,
                'name': p.phase_name,
                'duration': p.duration,
                'components': p.components
            }
            for p in hld_content.migration_phases
        ],
        'total_cost': hld_content.cost_analysis['total_monthly'],
        'architecture': {
            'compute': list(hld_content.target_architecture.compute_services.values()),
            'data': list(hld_content.target_architecture.data_services.values())
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(hld_summary, f, indent=2)

def print_service_mappings(mappings: List):
    """Pretty print service mappings"""
    print("\n| Component | Current | Target Azure Service | Complexity |")
    print("|-----------|---------|---------------------|------------|")
    
    for mapping in mappings:
        print(f"| {mapping.component_name} | {mapping.current_technology} | "
              f"{mapping.target_azure_service} | {mapping.migration_complexity} |")

def main():
    parser = argparse.ArgumentParser(description='Sprint 3 - HLD Generation (Simplified)')
    parser.add_argument('--sprint2-data', type=str, 
                       default='sprint2_output/sprint2_analysis.json',
                       help='Path to Sprint 2 analysis data (.pkl or .json file)')
    parser.add_argument('--api-key', type=str,
                       help='Gemini API key for synthesis (optional)')
    parser.add_argument('--output-dir', type=str, default='sprint3_output',
                       help='Output directory for HLD documents')
    args = parser.parse_args()
    
    # Header
    print_section("SPRINT 3 - HIGH-LEVEL DESIGN GENERATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Step 1: Load Sprint 2 Analysis
    print_section("Step 1: Loading Sprint 2 Analysis")
    
    try:
        analysis = load_sprint2_data(args.sprint2_data)
        print(f"✓ Loaded analysis for: {getattr(analysis, 'repository_url', 'Unknown Repository')}")
        print(f"  - Components: {len(analysis.components)}")
        if hasattr(analysis, 'dependency_graph') and analysis.dependency_graph:
            print(f"  - Dependency graph nodes: {analysis.dependency_graph.number_of_nodes()}")
        
        # Print criticality summary
        critical_count = sum(1 for c in analysis.components.values() 
                           if c.criticality and c.criticality.score > 0.5)
        print(f"  - Critical services: {critical_count}")
        
    except Exception as e:
        print(f"❌ Error loading Sprint 2 data: {e}")
        print("Please ensure you have run Sprint 2 and saved the analysis data")
        print(f"Expected file: {args.sprint2_data}")
        return
    
    # Step 2: Map Services to Azure
    print_section("Step 2: Mapping Services to Azure")
    
    mapper = AzureServiceMapper()
    
    # Map application components
    service_mappings = []
    for comp_name, comp_info in analysis.components.items():
        try:
            mapping = mapper.map_component_to_azure(comp_info, analysis)
            service_mappings.append(mapping)
            print(f"✓ Mapped {comp_name} -> {mapping.target_azure_service}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to map {comp_name}: {e}")
            # Create a basic mapping as fallback
            from src.core.models import AzureServiceMapping
            fallback_mapping = AzureServiceMapping(
                component_name=comp_name,
                current_technology=comp_info.language,
                target_azure_service="Azure App Service",
                azure_service_tier="Basic",
                migration_complexity="Medium",
                estimated_cost_range="$50-$150",
                justification="Fallback mapping due to mapping error"
            )
            service_mappings.append(fallback_mapping)
    
    # Map data services
    try:
        data_mappings = mapper.map_data_services(analysis)
        for data_name, mapping in data_mappings.items():
            service_mappings.append(mapping)
            print(f"✓ Mapped {data_name} -> {mapping.target_azure_service}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to map data services: {e}")
    
    # Print mapping summary
    print_service_mappings(service_mappings)
    
    # Calculate total estimated cost
    total_min = 0
    total_max = 0
    for mapping in service_mappings:
        # Parse cost range
        import re
        numbers = re.findall(r'\d+', mapping.estimated_cost_range)
        if len(numbers) >= 2:
            total_min += int(numbers[0])
            total_max += int(numbers[1])
    
    print(f"\n💰 Estimated Monthly Cost Range: ${total_min} - ${total_max}")
    
    # Step 3: Generate HLD Content
    print_section("Step 3: Generating HLD Content")
    
    if args.api_key or os.getenv('GEMINI_API_KEY'):
        try:
            synthesizer = HLDSynthesizer(args.api_key)
            hld_content = synthesizer.synthesize_hld(analysis, service_mappings)
            print("✓ HLD content synthesized with AI assistance")
            
            # Print executive summary preview
            print("\nExecutive Summary Preview:")
            print("-" * 50)
            print(hld_content.executive_summary[:500] + "...")
            print("-" * 50)
            
        except Exception as e:
            print(f"⚠️ AI synthesis failed: {e}")
            print("Falling back to template-based generation")
            # Create fallback HLD content
            synthesizer = HLDSynthesizer()
            hld_content = synthesizer.synthesize_hld(analysis, service_mappings)
    else:
        print("⚠️ No API key provided - using template-based generation")
        # Use template-based generation
        synthesizer = HLDSynthesizer()
        hld_content = synthesizer.synthesize_hld(analysis, service_mappings)
    
    print(f"✓ Generated {len(hld_content.migration_phases)} migration phases")
    print(f"✓ Identified {len(hld_content.technical_decisions)} technical decisions")
    
    # Step 4: Generate HLD Document
    print_section("Step 4: Generating HLD Document")
    
    doc_generator = HLDDocumentGenerator()
    hld_document = doc_generator.generate_hld_document(analysis, hld_content)
    
    # Save HLD document
    hld_md_path = os.path.join(args.output_dir, "High_Level_Design.md")
    with open(hld_md_path, 'w', encoding='utf-8') as f:
        f.write(hld_document)
    print(f"✓ HLD document saved to: {hld_md_path}")
    
    # Save HLD data
    hld_data_path = os.path.join(args.output_dir, "hld_data.json")
    save_hld_data(hld_content, service_mappings, hld_data_path)
    print(f"✓ HLD data saved to: {hld_data_path}")
    
    # Step 5: Generate Word Document
    print_section("Step 5: Generating Word Document")
    
    try:
        word_doc_path = generate_hld_word_document(
            analysis, hld_content, hld_document, args.output_dir
        )
        print(f"✓ Word document saved to: {word_doc_path}")
    except Exception as e:
        print(f"⚠️ Word document generation failed: {e}")
        print("  Make sure python-docx is installed: pip install python-docx")
    
    # Generate architecture diagram (placeholder for actual diagram generation)
    print("\n📊 Architecture Diagrams:")
    print("  - Logical architecture: [Would be generated with diagramming library]")
    print("  - Network topology: [Would be generated with diagramming library]")
    print("  - Data flow: [Would be generated with diagramming library]")
    
    # Summary
    print_section("Sprint 3 Summary")
    
    print("✅ HLD Generation Complete!")
    print(f"\nKey Outcomes:")
    print(f"  - Services mapped to Azure: {len(service_mappings)}")
    print(f"  - Migration phases defined: {len(hld_content.migration_phases)}")
    print(f"  - Estimated monthly cost: ${hld_content.cost_analysis['total_monthly']:,.0f}")
    
    # Calculate timeline
    timeline_weeks = 0
    for phase in hld_content.migration_phases:
        try:
            weeks = int(phase.duration.split('-')[0])
            timeline_weeks += weeks
        except:
            timeline_weeks += 2  # Default 2 weeks per phase
    
    print(f"  - Migration timeline: {timeline_weeks} weeks")
    
    print(f"\nGenerated Documents:")
    print(f"  - High-Level Design (Markdown): {hld_md_path}")
    print(f"  - High-Level Design (Word): {word_doc_path if 'word_doc_path' in locals() else 'Failed to generate'}")
    print(f"  - HLD Data: {hld_data_path}")
    
    print(f"\nNext Steps:")
    print("  1. Review and validate HLD with stakeholders")
    print("  2. Get sign-off on technical decisions")
    print("  3. Proceed to Sprint 4 for Low-Level Design")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main() 