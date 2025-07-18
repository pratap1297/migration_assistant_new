#!/usr/bin/env python3
"""
Enhanced Sprint 1 - Application Intelligence Platform Runner
"""

import os
import sys
import tempfile
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    Repo = None

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.intelligence.application_intelligence import ApplicationIntelligencePlatform

def print_banner():
    """Print application banner"""
    print("=" * 80)
    print("🚀 APPLICATION INTELLIGENCE PLATFORM - Enhanced Sprint 1")
    print("=" * 80)
    print("FR-01: Component & Architecture Discovery")
    print("FR-02: CI/CD Pipeline Analysis")
    print("FR-03: Configuration & Dependency Mapping")
    print("FR-04: Documentation & Business Context Analysis")
    print("FR-05: Enhanced Security Posture Analysis")
    print("=" * 80)

def print_section(title: str, emoji: str = "🔍"):
    """Print formatted section header"""
    print(f"\n{emoji} {title}")
    print("-" * (len(title) + 4))

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Sprint 1 - Application Intelligence Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze GitHub repository
  python run_enhanced_sprint1.py --repo https://github.com/user/repo

  # Analyze local directory
  python run_enhanced_sprint1.py --local-path /path/to/project

  # With LLM analysis
  python run_enhanced_sprint1.py --repo https://github.com/user/repo --api-key YOUR_KEY

  # Save detailed report
  python run_enhanced_sprint1.py --repo https://github.com/user/repo --output-dir ./reports
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--repo', type=str, help='Git repository URL to analyze')
    input_group.add_argument('--local-path', type=str, help='Local directory path to analyze')
    
    # Configuration options
    parser.add_argument('--api-key', type=str, help='Gemini API key for LLM analysis')
    parser.add_argument('--output-dir', type=str, default='./intelligence_reports',
                       help='Output directory for reports (default: ./intelligence_reports)')
    parser.add_argument('--skip-clone', action='store_true',
                       help='Skip cloning if analyzing remote repo (use existing local copy)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Setup
    print_banner()
    
    # Get API key from environment if not provided
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  No API key provided. Documentation analysis will be skipped.")
        print("   Set GEMINI_API_KEY environment variable or use --api-key flag")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine analysis path
    if args.repo:
        repo_url = args.repo
        if args.skip_clone:
            # Assume local directory with same name as repo
            repo_name = args.repo.split('/')[-1].replace('.git', '')
            analysis_path = os.path.join(os.getcwd(), repo_name)
            if not os.path.exists(analysis_path):
                print(f"❌ Local directory {analysis_path} not found. Remove --skip-clone to clone.")
                sys.exit(1)
            temp_dir = None
        else:
            # Clone to temporary directory
            temp_dir = tempfile.mkdtemp(prefix='app_intelligence_')
            analysis_path = temp_dir
            print_section("Cloning Repository", "📥")
            print(f"Repository: {repo_url}")
            print(f"Target: {analysis_path}")
            
            if not GIT_AVAILABLE:
                print("❌ GitPython not available. Install with: pip install gitpython")
                sys.exit(1)
            
            try:
                repo = Repo.clone_from(repo_url, analysis_path)
                print("✅ Repository cloned successfully")
            except Exception as e:
                print(f"❌ Failed to clone repository: {e}")
                sys.exit(1)
    else:
        repo_url = f"file://{os.path.abspath(args.local_path)}"
        analysis_path = args.local_path
        temp_dir = None
        
        if not os.path.exists(analysis_path):
            print(f"❌ Local path {analysis_path} does not exist")
            sys.exit(1)
    
    try:
        # Initialize platform
        print_section("Initializing Application Intelligence Platform", "🤖")
        platform = ApplicationIntelligencePlatform(gemini_api_key=api_key)
        
        # Perform analysis
        print_section("Performing Comprehensive Analysis", "🔍")
        intelligence = platform.analyze_application(analysis_path, repo_url)
        
        # Generate timestamp for reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Save JSON report
        json_report_path = output_dir / f"{repo_name}_intelligence_{timestamp}.json"
        platform.save_report(intelligence, str(json_report_path))
        
        # Generate and save markdown report
        markdown_report = platform.generate_markdown_report(intelligence)
        md_report_path = output_dir / f"{repo_name}_intelligence_{timestamp}.md"
        with open(md_report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"📄 Markdown report saved to: {md_report_path}")
        
        # Print summary to console
        print_section("Analysis Summary", "📊")
        
        print(f"🏢 **Application:** {intelligence.documentation_insights.application_purpose}")
        print(f"🎯 **Business Criticality:** {intelligence.documentation_insights.business_criticality}")
        print(f"🏗️  **Architecture Style:** {intelligence.architecture_insights.get('architecture_style', 'Unknown')}")
        print(f"📦 **Total Components:** {intelligence.summary['total_components']}")
        
        # Component breakdown
        if intelligence.summary['component_types']:
            print(f"📋 **Component Types:**")
            for comp_type, count in intelligence.summary['component_types'].items():
                print(f"   - {comp_type}: {count}")
        
        print(f"💻 **Languages:** {', '.join(intelligence.summary['languages'])}")
        print(f"🐳 **Containerization:** {intelligence.summary['containerization_status']}/{intelligence.summary['total_components']} components")
        
        # Infrastructure
        infra_features = []
        if intelligence.summary['has_kubernetes']:
            infra_features.append("Kubernetes")
        if intelligence.summary['has_docker_compose']:
            infra_features.append("Docker Compose")
        if intelligence.summary['ci_cd_pipelines'] > 0:
            infra_features.append(f"CI/CD ({intelligence.summary['ci_cd_pipelines']} pipelines)")
        
        if infra_features:
            print(f"🏭 **Infrastructure:** {', '.join(infra_features)}")
        
        # Security
        security_findings = intelligence.summary['security_findings']
        print(f"🔒 **Security:** {security_findings['hardcoded_secrets']} secrets, {security_findings['vulnerabilities']} vulnerabilities")
        
        # Compliance
        if intelligence.documentation_insights.compliance_requirements:
            print(f"📋 **Compliance:** {', '.join(intelligence.documentation_insights.compliance_requirements)}")
        
        # External dependencies
        print(f"🔗 **External Services:** {intelligence.summary['external_services']}")
        print(f"💾 **Datasources:** {intelligence.summary['datasources']}")
        
        # Key recommendations
        print_section("Key Recommendations", "💡")
        for i, rec in enumerate(intelligence.recommendations[:5], 1):
            print(f"{i}. {rec}")
        
        if len(intelligence.recommendations) > 5:
            print(f"   ... and {len(intelligence.recommendations) - 5} more (see full report)")
        
        print_section("Analysis Complete", "✅")
        print(f"📁 Reports saved to: {output_dir}")
        print(f"🕐 Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Cleanup temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                # Handle Windows permission issues with git files
                def handle_remove_readonly(func, path, exc):
                    import stat
                    if os.path.exists(path):
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
                if args.verbose:
                    print(f"🧹 Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up temporary directory: {e}")
                print(f"Please manually delete: {temp_dir}")

if __name__ == '__main__':
    main()