#!/usr/bin/env python3
"""
Enhanced Application Intelligence Platform Runner
Uses all the enhanced analyzers to provide accurate, evidence-based analysis
"""
import os
import sys
import argparse
import tempfile
import shutil
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from intelligence.enhanced_application_intelligence import EnhancedApplicationIntelligencePlatform

def load_api_key():
    """Load API key from environment or .env file"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        # Try to load from .env file
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
    
    return api_key

def clone_repository(repo_url: str, target_dir: str) -> str:
    """Clone repository to target directory"""
    import subprocess
    
    print(f"CLONE Cloning repository: {repo_url}")
    print(f"TARGET Target: {target_dir}")
    
    try:
        # Clean up existing directory
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # Clone repository
        result = subprocess.run([
            'git', 'clone', repo_url, target_dir
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"ERROR Failed to clone repository: {result.stderr}")
            return None
        
        print(f"OK Repository cloned successfully")
        return target_dir
        
    except subprocess.TimeoutExpired:
        print(f"ERROR Repository clone timed out")
        return None
    except Exception as e:
        print(f"ERROR Error cloning repository: {e}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Enhanced Application Intelligence Platform')
    parser.add_argument('--repo', help='Repository URL to analyze')
    parser.add_argument('--local-path', help='Local path to analyze')
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--word-report', action='store_true', help='Generate professional Word document report')
    parser.add_argument('--word-template', help='Path to custom Word template file')
    parser.add_argument('--word-config', help='Path to Word template configuration JSON file')
    
    args = parser.parse_args()
    
    if not args.repo and not args.local_path:
        print("ERROR Please provide either --repo or --local-path")
        return 1
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("WARNING No GEMINI_API_KEY found. LLM analysis will be limited.")
    
    # Initialize the enhanced platform
    platform = EnhancedApplicationIntelligencePlatform(gemini_api_key=api_key)
    
    # Determine source path
    if args.repo:
        # Clone repository
        temp_dir = tempfile.mkdtemp(prefix='enhanced_app_intelligence_')
        repo_path = clone_repository(args.repo, temp_dir)
        if not repo_path:
            return 1
        repo_url = args.repo
    else:
        # Use local path
        repo_path = args.local_path
        repo_url = f"file://{os.path.abspath(repo_path)}"
    
    try:
        print(f"\nINIT Initializing Enhanced Application Intelligence Platform")
        print(f"--------------------------------------------------")
        
        # Perform enhanced analysis
        print(f"\nANALYSIS Performing Enhanced Comprehensive Analysis")
        print(f"-------------------------------------")
        
        intelligence = platform.analyze_application(repo_path, repo_url)
        
        # Save reports
        print(f"\nSAVING Saving Enhanced Intelligence Reports")
        print(f"---------------------------------------")
        
        json_path, md_path = platform.save_intelligence_report(intelligence, args.output_dir)
        
        print(f"REPORT Enhanced intelligence report saved to: {json_path}")
        print(f"REPORT Enhanced markdown report saved to: {md_path}")
        
        # Generate Word report if requested
        if args.word_report:
            print(f"\nWORD Generating Professional Word Report")
            print(f"-------------------------------------")
            
            try:
                from analysis.professional_word_generator import ProfessionalWordGenerator
                import json
                
                # Load template configuration if provided
                template_config = None
                if args.word_config and os.path.exists(args.word_config):
                    with open(args.word_config, 'r') as f:
                        template_config = json.load(f)
                
                # Initialize Word generator
                word_generator = ProfessionalWordGenerator(template_path=args.word_template)
                
                # Generate output path
                timestamp = intelligence.analysis_timestamp.replace(':', '').replace('-', '').replace('T', '_')[:15]
                word_output_path = os.path.join(args.output_dir, f"application_intelligence_report_{timestamp}.docx")
                
                # Convert intelligence to dict for Word generator
                intelligence_dict = intelligence.to_dict()
                
                # Generate Word report
                word_path = word_generator.generate_professional_report(
                    intelligence_dict, 
                    word_output_path, 
                    template_config
                )
                
                print(f"WORD Professional Word report saved to: {word_path}")
                
            except ImportError as e:
                print(f"WARNING Word report generation requires additional dependencies: {e}")
                print("   Install with: pip install python-docx matplotlib")
            except Exception as e:
                print(f"ERROR Error generating Word report: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
        
        # Display enhanced summary
        print(f"\nSUMMARY Enhanced Analysis Summary")
        print(f"--------------------")
        
        summary = intelligence.summary
        print(f"APPLICATION **Application:** {summary.get('application_name', 'Unknown')}")
        print(f"ARCHITECTURE **Architecture Style:** {summary.get('architecture_style', 'Unknown')}")
        print(f"BUSINESS **Business Criticality:** {summary.get('business_criticality', 'Unknown')}")
        print(f"COMPONENTS **Total Components:** {summary.get('total_components', 0)}")
        
        # Component breakdown
        print(f"LANGUAGES **Component Languages:**")
        languages = summary.get('languages', [])
        if isinstance(languages, list):
            for lang in languages:
                print(f"   - {lang}")
        else:
            for lang, count in languages.items():
                print(f"   - {lang}: {count}")
        
        print(f"CONTAINERS **Containerization:** {summary.get('containerization_rate', 'Unknown')}")
        
        # Git activity
        git_activity = summary.get('git_activity', {})
        print(f"GIT **Git Activity:**")
        print(f"   - Total Commits: {git_activity.get('total_commits', 0)}")
        print(f"   - Active Contributors: {git_activity.get('active_contributors', 0)}")
        print(f"   - Recent Activity: {git_activity.get('recent_activity', 'unknown')}")
        
        # Vulnerability summary
        vuln_summary = summary.get('vulnerability_summary', {})
        print(f"SECURITY **Security Assessment:**")
        print(f"   - Scan Tool: {vuln_summary.get('scan_tool', 'unknown')}")
        print(f"   - Total Findings: {vuln_summary.get('total_findings', 0)}")
        print(f"   - Base Image Risks: {vuln_summary.get('base_image_risks', 0)}")
        
        # Confidence summary
        print(f"CONFIDENCE **Overall Confidence:** {summary.get('overall_confidence', 'Unknown')}")
        
        # Key recommendations
        print(f"\nRECOMMENDATIONS Enhanced Key Recommendations")
        print(f"-----------------------")
        for i, rec in enumerate(intelligence.recommendations[:5], 1):
            print(f"{i}. {rec}")
        
        if len(intelligence.recommendations) > 5:
            print(f"   ... and {len(intelligence.recommendations) - 5} more recommendations")
        
        print(f"\nOK Enhanced Analysis Complete")
        print(f"---------------------")
        print(f"REPORTS Reports saved to: {args.output_dir}")
        print(f"TIME Analysis completed: {intelligence.analysis_timestamp}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    finally:
        # Clean up temporary directory
        if args.repo and 'temp_dir' in locals():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"WARNING Warning: Could not clean up temporary directory: {e}")

if __name__ == '__main__':
    sys.exit(main())