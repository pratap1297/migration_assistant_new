#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprint 1 Runner - Demonstrates complete semantic and security analysis
"""

import os
import sys
import json
import shutil
import tempfile
import argparse
from typing import Dict
from datetime import datetime

try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.semantic.semantic_engine import FactualExtractor
from src.security.security_scanner import SecurityScanner
from src.synthesis.insight_synthesizer import InsightSynthesizer
from src.core.models import SemanticCodeMap, SecurityFindings

def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")

def print_semantic_map(component: str, maps: list):
    """Pretty print semantic code maps"""
    print(f"\n### Component: {component}")
    
    for code_map in maps:
        print(f"\n  File: {code_map.file_path}")
        print(f"  Language: {code_map.language}")
        
        if code_map.api_endpoints:
            print(f"  API Endpoints ({len(code_map.api_endpoints)}):")
            for ep in code_map.api_endpoints[:3]:  # First 3
                print(f"    - {ep.methods} {ep.path}")
            if len(code_map.api_endpoints) > 3:
                print(f"    ... and {len(code_map.api_endpoints) - 3} more")
                
        if code_map.database_interactions:
            print(f"  Database Operations ({len(code_map.database_interactions)}):")
            for db in code_map.database_interactions[:3]:
                print(f"    - {db.operation} at line {db.line_number}")
            if len(code_map.database_interactions) > 3:
                print(f"    ... and {len(code_map.database_interactions) - 3} more")
                
        if code_map.outbound_http_calls:
            print(f"  HTTP Calls ({len(code_map.outbound_http_calls)}):")
            for call in code_map.outbound_http_calls[:3]:
                print(f"    - {call.method} {call.url}")
            if len(code_map.outbound_http_calls) > 3:
                print(f"    ... and {len(code_map.outbound_http_calls) - 3} more")
                
        if code_map.functions:
            print(f"  Functions: {len(code_map.functions)} defined")
            
        if code_map.classes:
            print(f"  Classes: {len(code_map.classes)} defined")
            
        if code_map.notes:
            print(f"  Notes: {'; '.join(code_map.notes)}")

def print_security_findings(findings: Dict[str, SecurityFindings]):
    """Pretty print security findings"""
    for component, finding in findings.items():
        print(f"\n### Component: {component}")
        
        if finding.authentication_mechanisms:
            print(f"  Authentication: {', '.join(set(finding.authentication_mechanisms))}")
        else:
            print("  Authentication: None detected")
            
        if finding.authorization_patterns:
            print(f"  Authorization: {', '.join(set(finding.authorization_patterns))}")
        else:
            print("  Authorization: None detected")
            
        if finding.encryption_usage:
            print(f"  Encryption: {', '.join(set(finding.encryption_usage))}")
        else:
            print("  Encryption: None detected")
            
        if finding.hardcoded_secrets:
            print(f"  ⚠️  Hardcoded Secrets: {len(finding.hardcoded_secrets)} found")
            for secret in finding.hardcoded_secrets[:2]:
                print(f"    - {secret['type']} in {secret['file']}:{secret['line']}")
            if len(finding.hardcoded_secrets) > 2:
                print(f"    ... and {len(finding.hardcoded_secrets) - 2} more")
                
        if finding.potential_vulnerabilities:
            print(f"  ⚠️  Vulnerabilities: {len(finding.potential_vulnerabilities)} found")
            for vuln in finding.potential_vulnerabilities[:2]:
                print(f"    - {vuln['type']}: {vuln['description']}")

def main():
    parser = argparse.ArgumentParser(description='Sprint 1 - Repository Analysis')
    parser.add_argument('--repo', type=str, 
                       default='https://github.com/end-of-game/openshift-voting-app',
                       help='Git repository URL to analyze')
    parser.add_argument('--local-path', type=str, 
                       help='Local path to analyze (instead of cloning)')
    parser.add_argument('--api-key', type=str, 
                       help='Gemini API key (or set GEMINI_API_KEY env var)')
    args = parser.parse_args()
    
    # Header
    print_section("SPRINT 1 - REPOSITORY SEMANTIC AND SECURITY ANALYSIS")
    if args.local_path:
        print(f"Local Path: {args.local_path}")
    else:
        print(f"Repository: {args.repo}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Determine analysis path
    if args.local_path:
        analysis_path = args.local_path
        temp_dir = None
    else:
        if not GIT_AVAILABLE:
            print("❌ GitPython not available. Install with: pip install gitpython")
            print("   Or use --local-path to analyze local directory")
            return
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='repo_analysis_')
        analysis_path = temp_dir
    
    try:
        # Step 1: Clone repository (if needed)
        if not args.local_path:
            print_section("Step 1: Cloning Repository")
            print(f"Cloning to: {temp_dir}")
            repo = Repo.clone_from(args.repo, temp_dir)
            print("✓ Repository cloned successfully")
        else:
            print_section("Step 1: Using Local Path")
            print(f"Analyzing: {analysis_path}")
        
        # Step 2: Semantic Analysis
        print_section("Step 2: Semantic Code Analysis")
        extractor = FactualExtractor()
        semantic_results = extractor.extract_repository_semantics(analysis_path)
        
        print(f"Found {len(semantic_results)} components")
        for component, maps in semantic_results.items():
            total_files = len(maps)
            total_endpoints = sum(len(m.api_endpoints) for m in maps)
            total_db_ops = sum(len(m.database_interactions) for m in maps)
            print(f"  - {component}: {total_files} files, {total_endpoints} endpoints, {total_db_ops} DB operations")
        
        # Print detailed semantic maps
        for component, maps in semantic_results.items():
            print_semantic_map(component, maps)
        
        # Step 3: Security Analysis
        print_section("Step 3: Security Analysis")
        scanner = SecurityScanner()
        security_results = scanner.scan_repository(analysis_path)
        
        print(f"Scanned {len(security_results)} components for security issues")
        
        # Count total issues
        total_secrets = sum(len(f.hardcoded_secrets) for f in security_results.values())
        total_vulns = sum(len(f.potential_vulnerabilities) for f in security_results.values())
        
        if total_secrets > 0:
            print(f"⚠️  Found {total_secrets} hardcoded secrets")
        if total_vulns > 0:
            print(f"⚠️  Found {total_vulns} potential vulnerabilities")
            
        # Print detailed findings
        print_security_findings(security_results)
        
        # Step 4: LLM Synthesis (if API key provided)
        if args.api_key or os.getenv('GEMINI_API_KEY'):
            print_section("Step 4: AI-Powered Flow Synthesis")
            
            try:
                synthesizer = InsightSynthesizer(args.api_key)
                narrative = synthesizer.generate_flow_narrative(semantic_results)
                
                print("Generated End-to-End Flow Narrative:")
                print("-" * 40)
                print(narrative)
                print("-" * 40)
            except Exception as e:
                print(f"⚠️  Could not generate AI narrative: {str(e)}")
                print("Tip: Make sure GEMINI_API_KEY is set correctly")
        else:
            print_section("Step 4: AI Synthesis Skipped")
            print("No API key provided. Set GEMINI_API_KEY or use --api-key flag")
        
        # Summary
        print_section("Analysis Summary")
        print(f"✓ Semantic analysis complete: {sum(len(maps) for maps in semantic_results.values())} files analyzed")
        print(f"✓ Security scan complete: {len(security_results)} components scanned")
        
        # Save results
        results_file = f"sprint1_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results = {
            'repository': args.repo if not args.local_path else args.local_path,
            'analysis_date': datetime.now().isoformat(),
            'semantic_summary': {
                component: {
                    'files_analyzed': len(maps),
                    'total_endpoints': sum(len(m.api_endpoints) for m in maps),
                    'total_db_operations': sum(len(m.database_interactions) for m in maps),
                    'total_http_calls': sum(len(m.outbound_http_calls) for m in maps),
                }
                for component, maps in semantic_results.items()
            },
            'security_summary': {
                component: {
                    'auth_mechanisms': list(set(f.authentication_mechanisms)),
                    'encryption': list(set(f.encryption_usage)),
                    'hardcoded_secrets_count': len(f.hardcoded_secrets),
                    'vulnerabilities_count': len(f.potential_vulnerabilities),
                }
                for component, f in security_results.items()
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if temp_dir:
            print_section("Cleanup")
            if os.path.exists(temp_dir):
                try:
                    # Windows-specific cleanup for git files
                    if os.name == 'nt':  # Windows
                        import stat
                        def remove_readonly(func, path, _):
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                        shutil.rmtree(temp_dir, onerror=remove_readonly)
                    else:
                        shutil.rmtree(temp_dir)
                    print("✓ Temporary files cleaned up")
                except Exception as e:
                    print(f"⚠️ Could not clean up temp directory: {temp_dir}")
                    print(f"   Error: {str(e)}")
                    print("   You may need to manually delete this directory")
            
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()