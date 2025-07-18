#!/usr/bin/env python3
"""
Sprint 2 Runner - Complete Migration Analysis with Dependency Graphing and AS-IS Documentation
"""

import sys
import os
import argparse
import tempfile
import shutil
import stat
from datetime import datetime
from typing import Optional, Dict, List
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.models import RepositoryAnalysis, ComponentInfo
from semantic.semantic_engine import FactualExtractor
from security.security_scanner import SecurityScanner
from analysis.graph_analyzer import GraphAnalyzer
from analysis.criticality_analyzer import CriticalityAnalyzer
from analysis.enhanced_document_generator import EnhancedDocumentGenerator
from analysis.sprint2_word_generator import generate_sprint2_word_document
from analysis.graph_visualizer import GraphVisualizer
from synthesis.insight_synthesizer import InsightSynthesizer

def _generate_basic_migration_recommendations(criticality_assessments, dependencies):
    """Generate basic migration recommendations"""
    recommendations = []
    
    # Critical components first
    critical_components = [c for c in criticality_assessments if c.business_criticality == 'critical']
    if critical_components:
        recommendations.append(f"Prioritize migration of {len(critical_components)} critical components")
    
    # High complexity components
    high_complexity = [c for c in criticality_assessments if c.technical_complexity in ['high', 'critical']]
    if high_complexity:
        recommendations.append(f"Plan extra time for {len(high_complexity)} high-complexity components")
    
    # External dependencies
    external_deps = [d for d in dependencies if d.dependency_type == 'http' and '.' in d.target_component]
    if external_deps:
        recommendations.append(f"Review {len(external_deps)} external dependencies before migration")
    
    # Database dependencies
    db_deps = [d for d in dependencies if d.dependency_type == 'database']
    if db_deps:
        recommendations.append(f"Coordinate migration of {len(db_deps)} database-dependent components")
    
    return recommendations

def main():
    """Main entry point for Sprint 2 analysis"""
    parser = argparse.ArgumentParser(
        description="Sprint 2 - Complete Migration Analysis with Dependency Graphing and AS-IS Documentation"
    )
    
    # Repository source
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--repo", 
        help="Git repository URL to analyze"
    )
    source_group.add_argument(
        "--local-path", 
        help="Local directory path to analyze"
    )
    
    # AI integration
    parser.add_argument(
        "--api-key",
        help="Google Gemini API key for AI insights (or set GEMINI_API_KEY env var)"
    )
    
    # Output options
    parser.add_argument(
        "--output-dir",
        default="sprint2_output",
        help="Output directory for generated files (default: sprint2_output)"
    )
    
    parser.add_argument(
        "--skip-visualizations",
        action="store_true",
        help="Skip generating visualizations (faster analysis)"
    )
    
    parser.add_argument(
        "--skip-ai",
        action="store_true", 
        help="Skip AI-powered insights generation"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 80)
    print(" SPRINT 2 - COMPLETE MIGRATION ANALYSIS")
    print("=" * 80)
    print()
    
    # Initialize components
    factual_extractor = FactualExtractor()
    security_scanner = SecurityScanner()
    graph_analyzer = GraphAnalyzer()
    criticality_analyzer = CriticalityAnalyzer()
    document_generator = EnhancedDocumentGenerator()
    
    # Initialize visualizer if not skipped
    visualizer = None
    if not args.skip_visualizations:
        try:
            visualizer = GraphVisualizer(os.path.join(args.output_dir, "visualizations"))
            print("✅ Graph visualizer initialized")
        except ImportError as e:
            print(f"⚠️  Visualization libraries not available: {e}")
            print("   Install with: pip install matplotlib seaborn networkx")
            print("   Continuing without visualizations...")
            visualizer = None
    
    # Initialize AI synthesizer if not skipped
    ai_synthesizer = None
    if not args.skip_ai:
        api_key = args.api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                ai_synthesizer = InsightSynthesizer(api_key)
                print("✅ AI synthesizer initialized")
            except Exception as e:
                print(f"⚠️  AI synthesizer initialization failed: {e}")
        else:
            print("⚠️  No API key provided, skipping AI insights")
    
    # Determine analysis target
    if args.repo:
        repo_path = clone_repository(args.repo)
        repo_url = args.repo
        cleanup_needed = True
    else:
        repo_path = os.path.abspath(args.local_path)
        repo_url = f"file://{repo_path}"
        cleanup_needed = False
    
    try:
        # Phase 1: Semantic Analysis
        print("📊 Phase 1: Semantic Analysis")
        print("-" * 40)
        
        semantic_results = factual_extractor.extract_repository_semantics(repo_path)
        print(f"✅ Analyzed {len(semantic_results)} components")
        
        # Phase 2: Security Analysis
        print("\\n🔒 Phase 2: Security Analysis")
        print("-" * 40)
        
        security_results = security_scanner.scan_repository(repo_path)
        print(f"✅ Security scan completed for {len(security_results)} components")
        
        # Phase 3: Dependency Analysis
        print("\\n🔗 Phase 3: Dependency Analysis")
        print("-" * 40)
        
        dependencies = graph_analyzer.analyze_dependencies(semantic_results)
        dependency_graph = graph_analyzer.get_dependency_graph()
        component_info = graph_analyzer.get_component_info()
        
        print(f"✅ Identified {len(dependencies)} dependencies")
        if dependency_graph:
            print(f"✅ Built dependency graph with {dependency_graph.number_of_nodes()} nodes")
        else:
            print("⚠️  Dependency graph not available (NetworkX not installed)")
        
        # Phase 4: Criticality Analysis
        print("\\n⚡ Phase 4: Criticality Analysis")
        print("-" * 40)
        
        criticality_assessments = criticality_analyzer.analyze_criticality(
            semantic_results, security_results, dependencies, dependency_graph
        )
        
        print(f"✅ Assessed criticality for {len(criticality_assessments)} components")
        
        # Display criticality summary
        distribution = criticality_analyzer.get_criticality_distribution(criticality_assessments)
        print(f"   Critical: {distribution['critical']}, High: {distribution['high']}, Medium: {distribution['medium']}, Low: {distribution['low']}")
        
        # Phase 5: AI-Powered Insights
        architecture_insights = []
        migration_recommendations = []
        
        if ai_synthesizer:
            print("\\n🤖 Phase 5: AI-Powered Insights")
            print("-" * 40)
            
            try:
                # Generate flow narrative using existing method
                flow_narrative = ai_synthesizer.generate_flow_narrative(semantic_results)
                print(f"✅ Generated flow narrative")
                
                # Use flow narrative as architecture insights
                architecture_insights = [flow_narrative] if flow_narrative else []
                
                # Generate basic migration recommendations
                migration_recommendations = _generate_basic_migration_recommendations(
                    criticality_assessments, dependencies
                )
                print(f"✅ Generated {len(migration_recommendations)} migration recommendations")
                
            except Exception as e:
                print(f"⚠️  AI insight generation failed: {e}")
        
        # Phase 6: Create Repository Analysis Object
        print("\\n📋 Phase 6: Consolidating Analysis")
        print("-" * 40)
        
        # Convert component info to ComponentInfo objects with enhanced data
        enhanced_components = []
        for component_name, info in component_info.items():
            # Add criticality assessment
            criticality = next((c for c in criticality_assessments if c.component_name == component_name), None)
            info.criticality = criticality
            enhanced_components.append(info)
        
        # Create complete analysis object
        repository_analysis = RepositoryAnalysis(
            repository_url=repo_url,
            analysis_date=datetime.now(),
            components=enhanced_components,
            dependencies=dependencies,
            criticality_assessments=criticality_assessments,
            semantic_maps=semantic_results,
            security_findings=security_results,
            architecture_insights=architecture_insights,
            migration_recommendations=migration_recommendations
        )
        
        print(f"✅ Consolidated analysis for {len(enhanced_components)} components")
        
        # Phase 7: Generate Documentation
        print("\\n📄 Phase 7: Documentation Generation")
        print("-" * 40)
        
        # Generate AS-IS document
        as_is_doc_path = document_generator.generate_as_is_document(
            repository_analysis,
            os.path.join(args.output_dir, "AS-IS_Analysis.md")
        )
        print(f"✅ Generated AS-IS document: {as_is_doc_path}")
        
        # Generate JSON report
        json_report_path = document_generator.generate_json_report(
            repository_analysis,
            os.path.join(args.output_dir, "sprint2_analysis.json")
        )
        print(f"✅ Generated JSON report: {json_report_path}")
        
        # Generate Word document
        print("📝 Generating professional Word document...")
        try:
            word_doc_path = generate_sprint2_word_document(repository_analysis, args.output_dir)
            print(f"✅ Generated Word document: {word_doc_path}")
        except Exception as e:
            print(f"⚠️ Word document generation failed: {e}")
            print("  Make sure python-docx is installed: pip install python-docx")
        
        # Phase 8: Generate Visualizations
        if visualizer:
            print("\\n📊 Phase 8: Visualization Generation")
            print("-" * 40)
            
            try:
                visualization_files = visualizer.create_all_visualizations(repository_analysis)
                print(f"✅ Generated {len(visualization_files)} visualizations:")
                for viz_file in visualization_files:
                    print(f"   - {viz_file}")
            except Exception as e:
                print(f"⚠️  Visualization generation failed: {e}")
        
        # Phase 9: Display Results Summary
        print("\\n" + "=" * 80)
        print(" SPRINT 2 ANALYSIS COMPLETE")
        print("=" * 80)
        
        display_results_summary(repository_analysis)
        
        # Display output files
        print("\\n📁 Generated Files:")
        print(f"   - AS-IS Document (Markdown): {as_is_doc_path}")
        print(f"   - AS-IS Document (Word): {word_doc_path if 'word_doc_path' in locals() else 'Failed to generate'}")
        print(f"   - JSON Report: {json_report_path}")
        if visualizer and 'visualization_files' in locals():
            for viz_file in visualization_files:
                print(f"   - Visualization: {viz_file}")
        
        print(f"\\n🎉 All files saved to: {args.output_dir}")
        
    except Exception as e:
        print(f"\\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        if cleanup_needed:
            cleanup_temp_directory(repo_path)
    
    return 0

def clone_repository(repo_url: str) -> str:
    """Clone repository to temporary directory"""
    try:
        import git
        
        temp_dir = tempfile.mkdtemp()
        print(f"📥 Cloning repository to {temp_dir}")
        
        git.Repo.clone_from(repo_url, temp_dir)
        print("✅ Repository cloned successfully")
        
        return temp_dir
        
    except ImportError:
        print("❌ GitPython not available. Install with: pip install gitpython")
        print("   Or use --local-path for local analysis")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to clone repository: {e}")
        sys.exit(1)

def cleanup_temp_directory(temp_dir: str):
    """Clean up temporary directory with Windows compatibility"""
    try:
        if os.name == 'nt':  # Windows
            def remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(temp_dir, onerror=remove_readonly)
        else:
            shutil.rmtree(temp_dir)
        print(f"✅ Cleaned up temporary directory")
    except Exception as e:
        print(f"⚠️  Failed to cleanup {temp_dir}: {e}")

def display_results_summary(analysis: RepositoryAnalysis):
    """Display a summary of analysis results"""
    print("\\n📊 Analysis Summary:")
    print(f"   Repository: {analysis.repository_url}")
    print(f"   Components: {len(analysis.components)}")
    print(f"   Dependencies: {len(analysis.dependencies)}")
    print(f"   Security Findings: {len(analysis.security_findings)}")
    
    # Component breakdown
    print("\\n🏗️  Component Breakdown:")
    for component in sorted(analysis.components, key=lambda x: x.lines_of_code, reverse=True)[:5]:
        criticality = component.criticality.business_criticality if component.criticality else "unknown"
        print(f"   - {component.name}: {component.lines_of_code:,} LOC, {component.api_endpoints_count} endpoints ({criticality})")
    
    # Dependency breakdown
    dep_types = {}
    for dep in analysis.dependencies:
        dep_types[dep.dependency_type] = dep_types.get(dep.dependency_type, 0) + 1
    
    print("\\n🔗 Dependencies:")
    for dep_type, count in sorted(dep_types.items()):
        print(f"   - {dep_type}: {count}")
    
    # Top insights
    if analysis.architecture_insights:
        print("\\n🎯 Key Architecture Insights:")
        for insight in analysis.architecture_insights[:3]:
            print(f"   - {insight}")
    
    if analysis.migration_recommendations:
        print("\\n💡 Migration Recommendations:")
        for rec in analysis.migration_recommendations[:3]:
            print(f"   - {rec}")

if __name__ == "__main__":
    sys.exit(main())