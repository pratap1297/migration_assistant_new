"""
Enhanced Application Intelligence Platform orchestrator with all improvements integrated
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from src.parsers.base import AbstractParser
from src.parsers.infrastructure.dockerfile import DockerfileParser
from src.parsers.infrastructure.docker_compose import DockerComposeParser
from src.parsers.infrastructure.kubernetes import KubernetesParser
from src.parsers.cicd.github_actions import GitHubActionsParser
from src.parsers.config.properties import PropertiesParser
from src.parsers.config.yaml_config import YamlConfigParser

# Enhanced analyzers
from src.analyzers.enhanced_component_discovery import EnhancedComponentDiscoveryAnalyzer, EnhancedComponentInfo
from src.analyzers.documentation_analyzer import DocumentationAnalyzer, DocumentationInsights
from src.analyzers.enhanced_git_history_analyzer import EnhancedGitHistoryAnalyzer, GitHistoryInsights
from src.analyzers.vulnerability_analyzer import VulnerabilityAnalyzer, VulnerabilityAssessment
from src.analyzers.enhanced_synthesis_engine import EnhancedSynthesisEngine, ArchitectureAssessment, BusinessCriticalityAssessment
from src.analyzers.comprehensive_llm_synthesizer import ComprehensiveLLMSynthesizer, ComprehensiveSynthesis
from src.analyzers.cross_artifact_correlator import CrossArtifactCorrelator
from src.analyzers.directory_structure_analyzer import DirectoryStructureAnalyzer
from src.analyzers.unified_correlation_engine import UnifiedCorrelationEngine

from src.semantic.semantic_engine import FactualExtractor
from src.security.security_scanner import SecurityScanner

@dataclass
class EnhancedApplicationIntelligence:
    """Complete enhanced application intelligence report"""
    repository_url: str
    analysis_timestamp: str
    summary: Dict[str, Any]
    components: Dict[str, Any]  # Changed to Any to support UnifiedComponent
    documentation_insights: DocumentationInsights
    infrastructure: Dict[str, Any]
    ci_cd_pipelines: Dict[str, Any]
    configuration: Dict[str, Any]
    security_posture: Dict[str, Any]
    vulnerability_assessment: VulnerabilityAssessment
    semantic_analysis: Dict[str, Any]
    git_history: Optional[GitHistoryInsights]
    architecture_assessment: ArchitectureAssessment
    business_criticality: BusinessCriticalityAssessment
    comprehensive_synthesis: Optional[ComprehensiveSynthesis]
    confidence_summary: Dict[str, Any]
    recommendations: List[str]
    orchestration_by_component: Optional[Dict[str, Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

class EnhancedApplicationIntelligencePlatform:
    """Enhanced orchestrator with all improvements integrated"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        
        # Initialize parsers
        self.parsers: Dict[str, AbstractParser] = {
            'dockerfile': DockerfileParser(),
            'docker-compose': DockerComposeParser(),
            'kubernetes': KubernetesParser(),
            'github-actions': GitHubActionsParser(),
            'properties': PropertiesParser(),
            'yaml': YamlConfigParser()
        }
        
        # Initialize enhanced analyzers
        self.component_discovery = EnhancedComponentDiscoveryAnalyzer()
        self.documentation_analyzer = DocumentationAnalyzer(gemini_api_key or '')
        self.git_analyzer = EnhancedGitHistoryAnalyzer()
        self.vulnerability_analyzer = VulnerabilityAnalyzer()
        self.synthesis_engine = EnhancedSynthesisEngine()
        self.llm_synthesizer = ComprehensiveLLMSynthesizer(gemini_api_key or '')
        self.cross_correlator = CrossArtifactCorrelator()
        self.directory_analyzer = DirectoryStructureAnalyzer()
        self.unified_correlator = UnifiedCorrelationEngine()
        
        # Legacy analyzers for compatibility
        self.semantic_extractor = FactualExtractor()
        self.security_scanner = SecurityScanner()
    
    def analyze_application(self, repo_path: str, repo_url: str = "") -> EnhancedApplicationIntelligence:
        """Perform comprehensive enhanced application intelligence analysis"""
        
        print(f"ENHANCED-AI Starting Enhanced Application Intelligence Analysis")
        print(f"REPO Repository: {repo_url or repo_path}")
        print(f"TIMESTAMP Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Step 1: Enhanced Component Discovery
        print("ENHANCED-AI Performing enhanced component discovery...")
        components = self.component_discovery.discover_components(repo_path)
        print(f"ENHANCED-AI Found {len(components)} components with enhanced correlation")
        
        # Step 2: Infrastructure Analysis
        print("ENHANCED-AI Analyzing infrastructure configurations...")
        infrastructure = self._analyze_infrastructure(repo_path)
        print(f"ENHANCED-AI Analyzed {len(infrastructure)} infrastructure components")
        
        # Step 3: CI/CD Pipeline Analysis
        print("CICD [ENHANCED-AI] Analyzing CI/CD pipelines...")
        ci_cd_pipelines = self._analyze_ci_cd_pipelines(repo_path)
        print(f"ENHANCED-AI Analyzed {len(ci_cd_pipelines)} CI/CD pipelines")
        
        # Step 4: Configuration Analysis
        print("CONFIG [ENHANCED-AI] Analyzing configuration files...")
        configuration = self._analyze_configuration(repo_path)
        print(f"ENHANCED-AI Analyzed configuration files")
        
        # Step 5: Documentation Analysis
        print("DOCS [ENHANCED-AI] Analyzing documentation with LLM...")
        documentation_insights = self.documentation_analyzer.analyze_documentation(repo_path)
        print(f"ENHANCED-AI Documentation analysis complete")
        
        # Step 6: Enhanced Git History Analysis
        print("ENHANCED-AI Performing enhanced git history analysis...")
        git_history = self.git_analyzer.analyze_git_history(repo_path)
        print(f"ENHANCED-AI Git analysis complete: {git_history.total_commits} commits, {git_history.active_contributors} contributors")
        
        # Step 7: Enhanced Vulnerability Assessment
        print("ENHANCED-AI Performing enhanced vulnerability assessment...")
        vulnerability_assessment = self.vulnerability_analyzer.analyze_vulnerabilities(repo_path, components)
        print(f"ENHANCED-AI Vulnerability assessment complete: {len(vulnerability_assessment.findings)} findings")
        
        # Step 8: Semantic Analysis (legacy)
        print("SEMANTIC [ENHANCED-AI] Performing semantic code analysis...")
        semantic_analysis = self._perform_semantic_analysis(repo_path, components)
        print(f"ENHANCED-AI Semantic analysis complete")
        
        # Step 9: Security Analysis (legacy)
        print("SECURITY [ENHANCED-AI] Performing security analysis...")
        security_posture = self._analyze_security_posture(repo_path, components)
        print(f"ENHANCED-AI Security analysis complete")
        
        # Step 10: Enhanced Architecture Assessment
        print("ARCHITECTURE [ENHANCED-AI] Performing enhanced architecture assessment...")
        architecture_assessment = self.synthesis_engine.assess_architecture(
            components, infrastructure, self._get_deployment_configs(repo_path)
        )
        print(f"ENHANCED-AI Architecture assessment complete: {architecture_assessment.style.value} ({architecture_assessment.style.confidence.value})")
        
        # Step 11: Enhanced Business Criticality Assessment
        print("ENHANCED-AI Assessing business criticality...")
        repository_context = {'name': os.path.basename(repo_path), 'url': repo_url}
        business_criticality = self.synthesis_engine.assess_business_criticality(
            components, documentation_insights, repository_context
        )
        print(f"ENHANCED-AI Business criticality: {business_criticality.level.value} ({business_criticality.level.confidence.value})")
        
        # Step 12: Comprehensive LLM Synthesis
        print("ENHANCED-AI Generating comprehensive LLM synthesis...")
        comprehensive_synthesis = self.llm_synthesizer.synthesize_comprehensive_insights(
            components, infrastructure, ci_cd_pipelines, configuration,
            security_posture, semantic_analysis, documentation_insights, git_history
        )
        print(f"ENHANCED-AI LLM synthesis complete")
        
        # Step 13: Unified Correlation (Fix Data Consistency)
        print("CORRELATION [ENHANCED-AI] Performing unified correlation to fix data consistency...")
        unified_analysis = self.unified_correlator.correlate_analysis(
            components, infrastructure, documentation_insights, git_history,
            semantic_analysis, security_posture
        )
        print(f"ENHANCED-AI Unified correlation completed")
        
        # Step 14: Generate Corrected Summary
        print("ENHANCED-AI Generating corrected summary...")
        corrected_summary = self.unified_correlator.create_corrected_summary(
            unified_analysis, git_history
        )
        print(f"ENHANCED-AI Corrected summary generated")
        
        # Step 15: Generate Confidence Summary
        print("ENHANCED-AI Generating confidence summary...")
        confidence_summary = self.synthesis_engine.generate_confidence_summary(
            architecture_assessment, business_criticality
        )
        print(f"ENHANCED-AI Confidence summary generated")
        
        # Step 16: Generate Enhanced Recommendations
        print("ENHANCED-AI Generating enhanced recommendations...")
        recommendations = self._generate_enhanced_recommendations(
            unified_analysis.components, architecture_assessment, business_criticality, 
            vulnerability_assessment, git_history
        )
        print(f"ENHANCED-AI Generated {len(recommendations)} recommendations")
        
        # Use corrected summary instead of old summary
        summary = corrected_summary
        print(f"ENHANCED-AI Using corrected summary")
        
        # Create final intelligence report with unified components
        intelligence = EnhancedApplicationIntelligence(
            repository_url=repo_url,
            analysis_timestamp=datetime.now().isoformat(),
            summary=summary,
            components=unified_analysis.components,
            documentation_insights=documentation_insights,
            infrastructure=infrastructure,
            ci_cd_pipelines=ci_cd_pipelines,
            configuration=configuration,
            security_posture=security_posture,
            vulnerability_assessment=vulnerability_assessment,
            semantic_analysis=semantic_analysis,
            git_history=git_history,
            architecture_assessment=architecture_assessment,
            business_criticality=business_criticality,
            comprehensive_synthesis=comprehensive_synthesis,
            confidence_summary=confidence_summary,
            recommendations=recommendations,
            orchestration_by_component=unified_analysis.orchestration_by_component
        )
        
        print("COMPLETE [ENHANCED-AI] Enhanced Analysis Complete!")
        print("=" * 60)
        
        return intelligence
    
    def _analyze_infrastructure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze infrastructure configurations"""
        infrastructure = {}
        
        # Parse Dockerfiles
        for parser_name, parser in self.parsers.items():
            if parser_name in ['dockerfile', 'docker-compose', 'kubernetes']:
                results = []
                for root, dirs, files in os.walk(repo_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for file in files:
                        file_path = os.path.join(root, file)
                        if parser.can_parse(Path(file_path)):
                            result = parser.parse(file_path)
                            if result.success:
                                results.append(result)
                
                if results:
                    infrastructure[parser_name] = results
        
        return infrastructure
    
    def _analyze_ci_cd_pipelines(self, repo_path: str) -> Dict[str, Any]:
        """Analyze CI/CD pipelines"""
        ci_cd_pipelines = {}
        
        parser = self.parsers['github-actions']
        results = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                file_path = os.path.join(root, file)
                if parser.can_parse(Path(file_path)):
                    result = parser.parse(file_path)
                    if result.success:
                        results.append(result)
        
        if results:
            ci_cd_pipelines['github-actions'] = results
        
        return ci_cd_pipelines
    
    def _analyze_configuration(self, repo_path: str) -> Dict[str, Any]:
        """Analyze configuration files"""
        configuration = {
            'external_services': [],
            'datasources': [],
            'secrets_management': []
        }
        
        # Parse configuration files
        for parser_name in ['properties', 'yaml']:
            parser = self.parsers[parser_name]
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    file_path = os.path.join(root, file)
                    if parser.can_parse(Path(file_path)):
                        result = parser.parse(file_path)
                        if result.success and result.data:
                            # Extract configuration insights
                            self._extract_configuration_insights(result.data, configuration)
        
        return configuration
    
    def _extract_configuration_insights(self, data: Dict[str, Any], config: Dict[str, Any]):
        """Extract insights from configuration data"""
        # Look for external services
        for key, value in data.items():
            if isinstance(value, str):
                if 'http://' in value or 'https://' in value:
                    config['external_services'].append({
                        'key': key,
                        'url': value,
                        'type': 'http_service'
                    })
                elif 'jdbc:' in value:
                    config['datasources'].append({
                        'key': key,
                        'connection_string': value,
                        'type': 'database'
                    })
    
    def _perform_semantic_analysis(self, repo_path: str, components: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic analysis on source code"""
        semantic_analysis = {}
        
        for component_name, component in components.items():
            if hasattr(component, 'path') and component.path:
                try:
                    factual_maps = self.semantic_extractor.extract_component_semantics(component.path)
                    semantic_analysis[component_name] = factual_maps
                except Exception as e:
                    print(f"WARNING [ENHANCED-AI] Error in semantic analysis for {component_name}: {e}")
                    semantic_analysis[component_name] = []
        
        return semantic_analysis
    
    def _analyze_security_posture(self, repo_path: str, components: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security posture"""
        security_posture = {
            'authentication_mechanisms': [],
            'authorization_framework': 'unknown',
            'security_protocols': [],
            'encryption_standards': [],
            'compliance_frameworks': [],
            'access_controls': [],
            'audit_logging': False,
            'vulnerability_management': 'basic',
            'component_findings': {}
        }
        
        for component_name, component in components.items():
            if hasattr(component, 'path') and component.path:
                try:
                    findings = self.security_scanner._scan_component(component.path, component_name)
                    security_posture['component_findings'][component_name] = findings
                except Exception as e:
                    print(f"WARNING [ENHANCED-AI] Error in security analysis for {component_name}: {e}")
                    security_posture['component_findings'][component_name] = None
        
        return security_posture
    
    def _get_deployment_configs(self, repo_path: str) -> Dict[str, Any]:
        """Get deployment configurations for architecture assessment"""
        deployment_configs = {}
        
        # Look for deployment-related files
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if any(keyword in content for keyword in ['kind: Deployment', 'kind: Service', 'kind: DeploymentConfig']):
                                relative_path = os.path.relpath(file_path, repo_path)
                                deployment_configs[relative_path] = content
                    except Exception:
                        pass
        
        return deployment_configs
    
    def _generate_enhanced_recommendations(self, components: Dict[str, Any],
                                         architecture: ArchitectureAssessment,
                                         criticality: BusinessCriticalityAssessment,
                                         vulnerabilities: VulnerabilityAssessment,
                                         git_history: GitHistoryInsights) -> List[str]:
        """Generate enhanced recommendations based on analysis"""
        recommendations = []
        
        # Architecture recommendations
        if architecture.style.confidence.value != 'HIGH':
            recommendations.append(f"ARCHITECTURE Architecture Assessment: {architecture.style.value} detected with {architecture.style.confidence.value} confidence. Consider documenting architecture decisions for clarity.")
        
        # Component recommendations
        unknown_language_count = sum(1 for comp in components.values() 
                                   if hasattr(comp, 'language') and comp.language == 'unknown')
        if unknown_language_count > 0:
            recommendations.append(f"COMPONENT Component Analysis: {unknown_language_count} components have unknown languages. Review build configurations and source code structure.")
        
        # Git recommendations
        if git_history.total_commits > 0:
            if git_history.recent_activity == 'inactive':
                recommendations.append("DEVELOPMENT Development Activity: Low recent activity detected. Consider reviewing development processes and team capacity.")
            
            if len(git_history.hotspot_files) > 5:
                recommendations.append(f"HOTSPOTS Code Hotspots: {len(git_history.hotspot_files)} files change frequently. Consider refactoring for better maintainability.")
        
        # Vulnerability recommendations
        if vulnerabilities.findings:
            critical_high = sum(1 for f in vulnerabilities.findings if f.severity in ['CRITICAL', 'HIGH'])
            if critical_high > 0:
                recommendations.append(f"SECURITY Security: {critical_high} critical/high severity vulnerabilities found. Prioritize security remediation.")
        
        if vulnerabilities.base_image_risks:
            recommendations.append(f"🐳 Base Images: {len(vulnerabilities.base_image_risks)} base images have known risks. Update to more recent versions.")
        
        # Business criticality recommendations
        if criticality.level.confidence.value == 'INFERRED':
            recommendations.append("💼 Business Criticality: Assessment is inferred from technical indicators. Validate with business stakeholders.")
        
        return recommendations
    
    def _create_enhanced_summary(self, components: Dict[str, Any],
                               architecture: ArchitectureAssessment,
                               criticality: BusinessCriticalityAssessment,
                               vulnerabilities: VulnerabilityAssessment,
                               git_history: GitHistoryInsights,
                               confidence: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced summary with confidence indicators"""
        
        # Component statistics
        languages = {}
        packaging_types = {}
        for comp_name, comp in components.items():
            if hasattr(comp, 'language'):
                languages[comp.language] = languages.get(comp.language, 0) + 1
            if hasattr(comp, 'packaging'):
                packaging_types[comp.packaging] = packaging_types.get(comp.packaging, 0) + 1
        
        # Vulnerability summary
        vuln_summary = self.vulnerability_analyzer.get_vulnerability_summary(vulnerabilities)
        
        return {
            'application_name': os.path.basename(components[list(components.keys())[0]].path if components else 'unknown'),
            'architecture_style': f"{architecture.style.value} ({architecture.style.confidence.value} confidence)",
            'business_criticality': f"{criticality.level.value} ({criticality.level.confidence.value})",
            'total_components': len(components),
            'languages': languages,
            'packaging_types': packaging_types,
            'containerization_rate': f"{packaging_types.get('docker', 0)}/{len(components)} components",
            'git_activity': {
                'total_commits': git_history.total_commits,
                'active_contributors': git_history.active_contributors,
                'recent_activity': git_history.recent_activity
            },
            'vulnerability_summary': vuln_summary,
            'overall_confidence': confidence.get('overall_confidence', 'UNKNOWN')
        }
    
    def save_intelligence_report(self, intelligence: EnhancedApplicationIntelligence, 
                                output_dir: str = "reports") -> Tuple[str, str]:
        """Save enhanced intelligence report"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        repo_name = intelligence.repository_url.split('/')[-1] if intelligence.repository_url else 'unknown'
        json_filename = f"{repo_name}_enhanced_intelligence_{timestamp}.json"
        md_filename = f"{repo_name}_enhanced_intelligence_{timestamp}.md"
        
        json_path = os.path.join(output_dir, json_filename)
        md_path = os.path.join(output_dir, md_filename)
        
        # Save JSON report
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self._serialize_intelligence(intelligence), f, indent=2, ensure_ascii=False)
        
        # Save Markdown report
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(intelligence))
        
        return json_path, md_path
    
    def _serialize_intelligence(self, intelligence: EnhancedApplicationIntelligence) -> Dict[str, Any]:
        """Serialize intelligence report for JSON output"""
        return {
            'repository_url': intelligence.repository_url,
            'analysis_timestamp': intelligence.analysis_timestamp,
            'summary': intelligence.summary,
            'components': {name: self._serialize_component(comp) for name, comp in intelligence.components.items()},
            'architecture_assessment': self._serialize_architecture_assessment(intelligence.architecture_assessment),
            'business_criticality': self._serialize_business_criticality(intelligence.business_criticality),
            'vulnerability_assessment': self._serialize_vulnerability_assessment(intelligence.vulnerability_assessment),
            'git_history': asdict(intelligence.git_history) if intelligence.git_history else None,
            'confidence_summary': intelligence.confidence_summary,
            'recommendations': intelligence.recommendations,
            'orchestration_by_component': intelligence.orchestration_by_component
        }
    
    def _serialize_component(self, component: Any) -> Dict[str, Any]:
        """Serialize component info (works with both EnhancedComponentInfo and UnifiedComponent)"""
        if hasattr(component, 'actual_name'):
            # UnifiedComponent
            return {
                'name': component.actual_name,
                'original_name': component.name,
                'path': component.path,
                'language': component.language,
                'language_confidence': component.language_confidence,
                'language_evidence': component.language_evidence,
                'runtime': component.runtime,
                'build_tool': component.build_tool,
                'packaging': component.packaging,
                'base_images': component.base_images,
                'exposed_ports': component.exposed_ports,
                'environment_variables': component.environment_variables,
                'dockerfile_path': component.dockerfile_path,
                'deployment_configs': component.deployment_configs,
                'build_configs': component.build_configs,
                'service_configs': component.service_configs,
                'route_configs': component.route_configs,
                'is_containerized': component.is_containerized,
                'datasource_connections': component.datasource_connections,
                'vulnerability_indicators': component.vulnerability_indicators,
                'dependencies': component.dependencies,
                'external_dependencies': component.external_dependencies,
                'notes': component.notes,
                'type': 'unified_component'  # Add type for UnifiedComponent
            }
        else:
            # EnhancedComponentInfo
            return {
                'name': component.name,
                'path': component.path,
                'type': getattr(component, 'type', 'unknown'),
                'language': component.language,
                'language_confidence': getattr(component, 'language_confidence', {}),
                'runtime': component.runtime,
                'build_tool': component.build_tool,
                'packaging': component.packaging,
                'exposed_ports': getattr(component, 'exposed_ports', []),
                'docker_files': getattr(component, 'docker_files', []),
                'base_images': getattr(component, 'base_images', []),
                's2i_images': getattr(component, 's2i_images', []),
                'has_deployment_config': getattr(component, 'has_deployment_config', False),
                'has_build_config': getattr(component, 'has_build_config', False),
                'source_files_found': getattr(component, 'source_files_found', 0)
            }
    
    def _serialize_architecture_assessment(self, assessment: ArchitectureAssessment) -> Dict[str, Any]:
        """Serialize architecture assessment"""
        return {
            'style': {
                'value': assessment.style.value,
                'confidence': assessment.style.confidence.value,
                'evidence': assessment.style.evidence,
                'reasoning': assessment.style.reasoning,
                'limitations': assessment.style.limitations
            },
            'complexity': {
                'value': assessment.complexity.value,
                'confidence': assessment.complexity.confidence.value,
                'evidence': assessment.complexity.evidence,
                'reasoning': assessment.complexity.reasoning
            },
            'maturity': {
                'value': assessment.maturity.value,
                'confidence': assessment.maturity.confidence.value,
                'evidence': assessment.maturity.evidence,
                'reasoning': assessment.maturity.reasoning
            }
        }
    
    def _serialize_business_criticality(self, criticality: BusinessCriticalityAssessment) -> Dict[str, Any]:
        """Serialize business criticality assessment"""
        return {
            'level': {
                'value': criticality.level.value,
                'confidence': criticality.level.confidence.value,
                'evidence': criticality.level.evidence,
                'reasoning': criticality.level.reasoning,
                'limitations': criticality.level.limitations
            },
            'confidence_notes': criticality.confidence_notes
        }
    
    def _serialize_vulnerability_assessment(self, assessment: VulnerabilityAssessment) -> Dict[str, Any]:
        """Serialize vulnerability assessment"""
        return {
            'scan_performed': assessment.scan_performed,
            'scan_tool': assessment.scan_tool,
            'findings_count': len(assessment.findings),
            'base_image_risks': len(assessment.base_image_risks),
            'outdated_dependencies': len(assessment.outdated_dependencies),
            'assessment_notes': assessment.assessment_notes
        }
    
    def _generate_markdown_report(self, intelligence: EnhancedApplicationIntelligence) -> str:
        """Generate enhanced markdown report"""
        
        md = f"""# Enhanced Application Intelligence Report

## Repository Information
- **URL:** {intelligence.repository_url}
- **Analysis Time:** {intelligence.analysis_timestamp}
- **Overall Confidence:** {intelligence.confidence_summary.get('overall_confidence', 'UNKNOWN')}

## Executive Summary

### Application Overview
- **Architecture Style:** {intelligence.architecture_assessment.style.value} ({intelligence.architecture_assessment.style.confidence.value} confidence)
- **Business Criticality:** {intelligence.business_criticality.level.value} ({intelligence.business_criticality.level.confidence.value})
- **Total Components:** {len(intelligence.components)}

### Key Findings
"""
        
        # Add architecture findings
        md += f"\n#### Architecture Assessment\n"
        md += f"- **Style:** {intelligence.architecture_assessment.style.value}\n"
        md += f"- **Confidence:** {intelligence.architecture_assessment.style.confidence.value}\n"
        md += f"- **Evidence:** {', '.join(intelligence.architecture_assessment.style.evidence)}\n"
        md += f"- **Reasoning:** {intelligence.architecture_assessment.style.reasoning}\n"
        
        # Add component details
        md += f"\n## Component Analysis\n\n"
        for name, component in intelligence.components.items():
            # Handle both UnifiedComponent and EnhancedComponentInfo
            display_name = getattr(component, 'actual_name', name)
            md += f"### {display_name}\n"
            md += f"- **Language:** {component.language}"
            
            # Handle confidence differently for UnifiedComponent vs EnhancedComponentInfo
            if hasattr(component, 'language_confidence') and component.language_confidence:
                if isinstance(component.language_confidence, dict):
                    max_confidence = max(component.language_confidence.items(), key=lambda x: x[1])
                    md += f" (Confidence: {max_confidence[1]:.1f})"
                else:
                    md += f" (Confidence: {component.language_confidence:.1f})"
            md += f"\n"
            
            # Type handling
            component_type = getattr(component, 'type', 'unified_component')
            md += f"- **Type:** {component_type}\n"
            md += f"- **Runtime:** {component.runtime}\n"
            md += f"- **Build Tool:** {component.build_tool}\n"
            md += f"- **Packaging:** {component.packaging}\n"
            if component.exposed_ports:
                md += f"- **Exposed Ports:** {', '.join(map(str, component.exposed_ports))}\n"
            if component.base_images:
                md += f"- **Base Images:** {', '.join(component.base_images)}\n"
            
            # Source files found - handle different attribute names
            source_files = getattr(component, 'source_files_found', 0)
            md += f"- **Source Files Found:** {source_files}\n"
            
            # Deployment config - handle different attribute names
            has_deployment = getattr(component, 'has_deployment_config', False)
            if hasattr(component, 'deployment_configs'):
                has_deployment = len(component.deployment_configs) > 0
            md += f"- **Has Deployment Config:** {'Yes' if has_deployment else 'No'}\n"
            
            # Add notes if available
            if hasattr(component, 'notes') and component.notes:
                md += f"- **Notes:**\n"
                for note in component.notes:
                    md += f"  - {note}\n"
            
            md += f"\n"
        
        # Add git analysis
        if intelligence.git_history:
            md += f"\n## Git History Analysis\n\n"
            md += f"- **Total Commits:** {intelligence.git_history.total_commits}\n"
            md += f"- **Active Contributors:** {intelligence.git_history.active_contributors}\n"
            md += f"- **Recent Activity:** {intelligence.git_history.recent_activity}\n"
            md += f"- **Team Velocity:** {intelligence.git_history.team_velocity}\n"
            md += f"- **Code Stability:** {intelligence.git_history.code_stability}\n"
            
            if intelligence.git_history.hotspot_files:
                md += f"\n### File Hotspots\n"
                for hotspot in intelligence.git_history.hotspot_files[:5]:
                    md += f"- **{hotspot.path}:** {hotspot.change_frequency} changes\n"
        
        # Add vulnerability assessment
        md += f"\n## Security & Vulnerability Assessment\n\n"
        vuln_summary = self.vulnerability_analyzer.get_vulnerability_summary(intelligence.vulnerability_assessment)
        md += f"- **Scan Tool:** {vuln_summary['scan_tool']}\n"
        md += f"- **Total Findings:** {vuln_summary['total_findings']}\n"
        md += f"- **Base Image Risks:** {vuln_summary['base_image_risks']}\n"
        md += f"- **Outdated Dependencies:** {vuln_summary['outdated_dependencies']}\n"
        
        if intelligence.vulnerability_assessment.assessment_notes:
            md += f"\n### Assessment Notes\n"
            for note in intelligence.vulnerability_assessment.assessment_notes:
                md += f"- {note}\n"
        
        # Add recommendations
        md += f"\n## Enhanced Recommendations\n\n"
        for i, rec in enumerate(intelligence.recommendations, 1):
            md += f"{i}. {rec}\n"
        
        # Add confidence summary
        md += f"\n## Confidence Summary\n\n"
        md += f"- **Overall Confidence:** {intelligence.confidence_summary.get('overall_confidence', 'UNKNOWN')}\n"
        md += f"- **Architecture Style:** {intelligence.confidence_summary.get('architecture_style', {}).get('confidence', 'UNKNOWN')}\n"
        md += f"- **Business Criticality:** {intelligence.confidence_summary.get('business_criticality', {}).get('confidence', 'UNKNOWN')}\n"
        
        if intelligence.business_criticality.level.confidence.value == 'INFERRED':
            md += f"\n### Important Notes\n"
            md += f"- Business criticality is **inferred** from technical indicators\n"
            md += f"- Validation with business stakeholders is recommended\n"
        
        return md