"""
Main Application Intelligence Platform orchestrator
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from src.parsers.base import AbstractParser
from src.parsers.infrastructure.dockerfile import DockerfileParser
from src.parsers.infrastructure.docker_compose import DockerComposeParser
from src.parsers.infrastructure.kubernetes import KubernetesParser
from src.parsers.cicd.github_actions import GitHubActionsParser
from src.parsers.config.properties import PropertiesParser
from src.parsers.config.yaml_config import YamlConfigParser
from src.analyzers.component_discovery import ComponentDiscoveryAnalyzer, ComponentInfo
from src.analyzers.documentation_analyzer import DocumentationAnalyzer, DocumentationInsights
from src.analyzers.git_history_analyzer import GitHistoryAnalyzer, GitHistoryInsights
from src.analyzers.comprehensive_llm_synthesizer import ComprehensiveLLMSynthesizer, ComprehensiveSynthesis
from src.semantic.semantic_engine import FactualExtractor
from src.security.security_scanner import SecurityScanner

@dataclass
class ApplicationIntelligence:
    """Complete application intelligence report"""
    repository_url: str
    analysis_timestamp: str
    summary: Dict[str, Any]
    components: Dict[str, ComponentInfo]
    documentation_insights: DocumentationInsights
    infrastructure: Dict[str, Any]
    ci_cd_pipelines: Dict[str, Any]
    configuration: Dict[str, Any]
    security_posture: Dict[str, Any]
    semantic_analysis: Dict[str, Any]
    git_history: Optional[GitHistoryInsights]
    comprehensive_synthesis: Optional[ComprehensiveSynthesis]
    architecture_insights: Dict[str, Any]
    recommendations: List[str]

class ApplicationIntelligencePlatform:
    """Main orchestrator for the enhanced Application Intelligence Platform"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        
        # Initialize parsers
        self.parsers: Dict[str, AbstractParser] = {
            'dockerfile': DockerfileParser(),
            'docker-compose': DockerComposeParser(),
            'kubernetes': KubernetesParser(),
            'github-actions': GitHubActionsParser(),
            'properties': PropertiesParser(),
            'yaml-config': YamlConfigParser()
        }
        
        # Initialize analyzers
        self.component_analyzer = ComponentDiscoveryAnalyzer()
        self.semantic_analyzer = FactualExtractor()
        self.security_scanner = SecurityScanner()
        self.git_history_analyzer = GitHistoryAnalyzer()
        
        if self.gemini_api_key:
            self.doc_analyzer = DocumentationAnalyzer(self.gemini_api_key)
            self.comprehensive_synthesizer = ComprehensiveLLMSynthesizer(self.gemini_api_key)
        else:
            self.doc_analyzer = None
            self.comprehensive_synthesizer = None
    
    def analyze_application(self, repo_path: str, repo_url: str = "") -> ApplicationIntelligence:
        """Perform comprehensive application analysis"""
        print("🔍 Starting Application Intelligence Analysis...")
        
        # 1. Component Discovery (FR-01)
        print("📦 Discovering components and architecture...")
        components = self.component_analyzer.discover_components(repo_path)
        
        # 2. Infrastructure Analysis
        print("🏗️ Analyzing infrastructure configurations...")
        infrastructure = self._analyze_infrastructure(repo_path)
        
        # 3. CI/CD Pipeline Analysis (FR-02)
        print("🚀 Analyzing CI/CD pipelines...")
        ci_cd_pipelines = self._analyze_ci_cd_pipelines(repo_path)
        
        # 4. Configuration Analysis (FR-03)
        print("⚙️ Analyzing configuration files...")
        configuration = self._analyze_configuration(repo_path)
        
        # 5. Documentation Analysis (FR-04)
        print("📚 Analyzing documentation...")
        documentation_insights = self._analyze_documentation(repo_path)
        
        # 6. Security Analysis (FR-05)
        print("🔒 Performing security analysis...")
        security_posture = self._analyze_security_posture(repo_path)
        
        # 7. Semantic Code Analysis (existing)
        print("🧠 Performing semantic code analysis...")
        semantic_analysis = self._perform_semantic_analysis(repo_path)
        
        # 8. Git History Analysis (NEW)
        print("📊 Analyzing git history and development patterns...")
        git_history = self._analyze_git_history(repo_path)
        
        # 9. Comprehensive LLM Synthesis (NEW)
        print("🤖 Generating comprehensive LLM synthesis...")
        comprehensive_synthesis = self._generate_comprehensive_synthesis(
            components, infrastructure, ci_cd_pipelines, configuration,
            security_posture, semantic_analysis, documentation_insights, git_history
        )
        
        # 10. Architecture Insights
        print("🏛️ Generating architecture insights...")
        architecture_insights = self._generate_architecture_insights(
            components, infrastructure, ci_cd_pipelines, configuration
        )
        
        # 11. Generate Recommendations
        print("💡 Generating recommendations...")
        recommendations = self._generate_recommendations(
            components, infrastructure, ci_cd_pipelines, security_posture, documentation_insights
        )
        
        # 12. Post-Analysis Correlation and Synthesis Engine
        print("🔗 Performing post-analysis correlation and synthesis...")
        self._perform_post_analysis_correlation(
            components, infrastructure, ci_cd_pipelines, configuration,
            security_posture, documentation_insights, git_history
        )
        
        # 13. Create Summary (after correlation fixes)
        summary = self._create_summary(
            components, infrastructure, ci_cd_pipelines, configuration, 
            security_posture, documentation_insights, git_history
        )
        
        print("✅ Analysis complete!")
        
        return ApplicationIntelligence(
            repository_url=repo_url,
            analysis_timestamp=datetime.now().isoformat(),
            summary=summary,
            components=components,
            documentation_insights=documentation_insights,
            infrastructure=infrastructure,
            ci_cd_pipelines=ci_cd_pipelines,
            configuration=configuration,
            security_posture=security_posture,
            semantic_analysis=semantic_analysis,
            git_history=git_history,
            comprehensive_synthesis=comprehensive_synthesis,
            architecture_insights=architecture_insights,
            recommendations=recommendations
        )
    
    def _analyze_infrastructure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze infrastructure configurations"""
        infrastructure = {
            'containerization': {},
            'orchestration': {},
            'deployment_configs': []
        }
        
        # Find and parse infrastructure files
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = Path(os.path.join(root, file))
                
                # Check each parser
                for parser_name, parser in self.parsers.items():
                    if parser_name in ['dockerfile', 'docker-compose', 'kubernetes']:
                        if parser.can_parse(file_path):
                            try:
                                result = parser.parse(file_path)
                                if result.success:
                                    if parser_name == 'dockerfile':
                                        infrastructure['containerization'][str(file_path)] = result.data
                                    elif parser_name == 'docker-compose':
                                        infrastructure['orchestration']['docker-compose'] = result.data
                                    elif parser_name == 'kubernetes':
                                        if 'kubernetes' not in infrastructure['orchestration']:
                                            infrastructure['orchestration']['kubernetes'] = []
                                        infrastructure['orchestration']['kubernetes'].append(result.data)
                            except Exception as e:
                                print(f"Error parsing {file_path}: {e}")
        
        return infrastructure
    
    def _analyze_ci_cd_pipelines(self, repo_path: str) -> Dict[str, Any]:
        """Analyze CI/CD pipeline configurations"""
        pipelines = {
            'github_actions': [],
            'jenkins': [],
            'azure_devops': [],
            'gitlab_ci': [],
            'quality_gates': [],
            'deployment_stages': []
        }
        
        # GitHub Actions
        github_workflows_path = os.path.join(repo_path, '.github', 'workflows')
        if os.path.exists(github_workflows_path):
            for file in os.listdir(github_workflows_path):
                if file.endswith(('.yml', '.yaml')):
                    file_path = Path(os.path.join(github_workflows_path, file))
                    try:
                        parser = self.parsers['github-actions']
                        result = parser.parse(file_path)
                        if result.success:
                            pipelines['github_actions'].append(result.data)
                            
                            # Extract quality gates
                            quality_gates = result.data.get('quality_gates', [])
                            pipelines['quality_gates'].extend(quality_gates)
                            
                            # Extract deployment stages
                            deployment_info = result.data.get('deployment_info', [])
                            pipelines['deployment_stages'].extend(deployment_info)
                    except Exception as e:
                        print(f"Error parsing GitHub Actions workflow {file}: {e}")
        
        # TODO: Add parsers for Jenkins, Azure DevOps, GitLab CI
        
        return pipelines
    
    def _analyze_configuration(self, repo_path: str) -> Dict[str, Any]:
        """Analyze configuration files"""
        configuration = {
            'properties_files': [],
            'yaml_configs': [],
            'environment_variables': {},
            'external_services': [],
            'datasources': [],
            'secrets_management': []
        }
        
        # Find and parse configuration files
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = Path(os.path.join(root, file))
                
                # Properties files
                if self.parsers['properties'].can_parse(file_path):
                    try:
                        result = self.parsers['properties'].parse(file_path)
                        if result.success:
                            configuration['properties_files'].append(result.data)
                            
                            # Aggregate external services
                            ext_services = result.data.get('external_services', [])
                            configuration['external_services'].extend(ext_services)
                            
                            # Aggregate datasources
                            datasources = result.data.get('datasources', [])
                            configuration['datasources'].extend(datasources)
                            
                            # Aggregate secrets
                            secrets = result.data.get('secrets_references', [])
                            configuration['secrets_management'].extend(secrets)
                    except Exception as e:
                        print(f"Error parsing properties file {file_path}: {e}")
                
                # YAML configuration files
                elif self.parsers['yaml-config'].can_parse(file_path):
                    try:
                        result = self.parsers['yaml-config'].parse(file_path)
                        if result.success:
                            configuration['yaml_configs'].append(result.data)
                            
                            # Aggregate data similar to properties
                            ext_services = result.data.get('external_services', [])
                            configuration['external_services'].extend(ext_services)
                            
                            datasources = result.data.get('datasources', [])
                            configuration['datasources'].extend(datasources)
                            
                            secrets = result.data.get('secrets_references', [])
                            configuration['secrets_management'].extend(secrets)
                    except Exception as e:
                        print(f"Error parsing YAML config {file_path}: {e}")
        
        return configuration
    
    def _analyze_documentation(self, repo_path: str) -> DocumentationInsights:
        """Analyze documentation for business context"""
        if self.doc_analyzer:
            return self.doc_analyzer.analyze_documentation(repo_path)
        else:
            # Return empty insights if no API key
            return DocumentationInsights(
                application_purpose="Documentation analysis requires API key",
                business_criticality="MEDIUM",
                compliance_requirements=[],
                security_considerations=[],
                technology_stack=[],
                deployment_model="Unknown",
                user_types=[],
                integration_points=[],
                performance_requirements=[],
                business_context_keywords=[],
                architecture_patterns=[]
            )
    
    def _analyze_security_posture(self, repo_path: str) -> Dict[str, Any]:
        """Analyze security posture"""
        return self.security_scanner.scan_repository(repo_path)
    
    def _perform_semantic_analysis(self, repo_path: str) -> Dict[str, Any]:
        """Perform semantic code analysis"""
        return self.semantic_analyzer.extract_repository_semantics(repo_path)
    
    def _analyze_git_history(self, repo_path: str) -> Optional[GitHistoryInsights]:
        """Analyze git history and development patterns"""
        try:
            return self.git_history_analyzer.analyze_git_history(repo_path)
        except Exception as e:
            print(f"Git history analysis failed: {e}")
            return None
    
    def _generate_comprehensive_synthesis(self, 
                                        components: Dict[str, ComponentInfo],
                                        infrastructure: Dict[str, Any],
                                        ci_cd_pipelines: Dict[str, Any],
                                        configuration: Dict[str, Any],
                                        security_posture: Dict[str, Any],
                                        semantic_analysis: Dict[str, Any],
                                        documentation_insights: DocumentationInsights,
                                        git_history: Optional[GitHistoryInsights]) -> Optional[ComprehensiveSynthesis]:
        """Generate comprehensive LLM synthesis from all data"""
        if not self.comprehensive_synthesizer:
            return None
        
        try:
            return self.comprehensive_synthesizer.synthesize_comprehensive_insights(
                components, infrastructure, ci_cd_pipelines, configuration,
                security_posture, semantic_analysis, documentation_insights, git_history
            )
        except Exception as e:
            print(f"Comprehensive synthesis failed: {e}")
            return None
    
    def _generate_architecture_insights(self, components: Dict[str, ComponentInfo], 
                                      infrastructure: Dict[str, Any],
                                      ci_cd: Dict[str, Any], 
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture insights"""
        insights = {
            'deployment_pattern': 'unknown',
            'architecture_style': 'unknown',
            'technology_diversity': 0,
            'containerization_level': 'none',
            'orchestration_platform': 'none',
            'ci_cd_maturity': 'basic',
            'configuration_management': 'basic',
            'service_mesh': False,
            'microservices_score': 0
        }
        
        # Determine deployment pattern
        if infrastructure.get('orchestration', {}).get('kubernetes'):
            insights['deployment_pattern'] = 'kubernetes'
            insights['orchestration_platform'] = 'kubernetes'
        elif infrastructure.get('orchestration', {}).get('docker-compose'):
            insights['deployment_pattern'] = 'docker-compose'
            insights['orchestration_platform'] = 'docker-compose'
        elif infrastructure.get('containerization'):
            insights['deployment_pattern'] = 'containerized'
        
        # Determine architecture style
        microservice_count = len([c for c in components.values() if c.type == 'microservice'])
        total_components = len(components)
        
        if microservice_count >= 3:
            insights['architecture_style'] = 'microservices'
            insights['microservices_score'] = min(10, microservice_count)
        elif microservice_count >= 1:
            insights['architecture_style'] = 'hybrid'
            insights['microservices_score'] = 5
        else:
            insights['architecture_style'] = 'monolithic'
            insights['microservices_score'] = 0
        
        # Technology diversity
        languages = set(c.language for c in components.values())
        insights['technology_diversity'] = len(languages)
        
        # Containerization level
        containerized_count = len([c for c in components.values() if c.packaging == 'docker'])
        if containerized_count == total_components:
            insights['containerization_level'] = 'full'
        elif containerized_count > 0:
            insights['containerization_level'] = 'partial'
        else:
            insights['containerization_level'] = 'none'
        
        # CI/CD maturity
        github_actions = ci_cd.get('github_actions', [])
        if github_actions:
            workflow = github_actions[0]  # Analyze first workflow
            quality_gates = len(workflow.get('quality_gates', []))
            security_scans = len(workflow.get('security_scans', []))
            deployment_stages = len(workflow.get('deployment_info', []))
            
            maturity_score = quality_gates + security_scans + deployment_stages
            if maturity_score >= 6:
                insights['ci_cd_maturity'] = 'advanced'
            elif maturity_score >= 3:
                insights['ci_cd_maturity'] = 'intermediate'
            else:
                insights['ci_cd_maturity'] = 'basic'
        
        return insights
    
    def _generate_recommendations(self, components: Dict[str, ComponentInfo],
                                infrastructure: Dict[str, Any],
                                ci_cd: Dict[str, Any],
                                security: Dict[str, Any],
                                documentation: DocumentationInsights) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Documentation recommendations
        if documentation.application_purpose == "Unknown - No documentation found":
            recommendations.append("📚 Add comprehensive README.md with application purpose and architecture overview")
        
        if documentation.business_criticality == "MEDIUM" and not documentation.compliance_requirements:
            recommendations.append("🔍 Consider documenting compliance requirements and security considerations")
        
        # Security recommendations
        total_secrets = sum(len(findings.hardcoded_secrets) for findings in security.values())
        if total_secrets > 0:
            recommendations.append(f"🔒 Found {total_secrets} hardcoded secrets - implement proper secrets management")
        
        # CI/CD recommendations
        if not ci_cd.get('github_actions') and not ci_cd.get('jenkins'):
            recommendations.append("🚀 Implement automated CI/CD pipeline for consistent deployments")
        
        quality_gates = ci_cd.get('quality_gates', [])
        if len(quality_gates) < 2:
            recommendations.append("✅ Add more quality gates (code coverage, static analysis, security scanning)")
        
        # Architecture recommendations
        containerized_count = len([c for c in components.values() if c.packaging == 'docker'])
        if containerized_count < len(components):
            recommendations.append("🐳 Consider containerizing all components for consistent deployment")
        
        # Microservices recommendations
        microservice_count = len([c for c in components.values() if c.type == 'microservice'])
        if microservice_count >= 3:
            recommendations.append("🕸️ Consider implementing service mesh for microservices communication")
            recommendations.append("📊 Implement distributed tracing and monitoring for microservices")
        
        # Infrastructure recommendations
        if not infrastructure.get('orchestration', {}).get('kubernetes'):
            recommendations.append("☸️ Consider Kubernetes for production-grade orchestration")
        
        return recommendations
    
    def _create_summary(self, components: Dict[str, ComponentInfo],
                       infrastructure: Dict[str, Any],
                       ci_cd: Dict[str, Any],
                       configuration: Dict[str, Any],
                       security: Dict[str, Any],
                       documentation: DocumentationInsights,
                       git_history: Optional[GitHistoryInsights]) -> Dict[str, Any]:
        """Create analysis summary"""
        summary = {
            'total_components': len(components),
            'component_types': {
                comp_type: len([c for c in components.values() if c.type == comp_type])
                for comp_type in set(c.type for c in components.values())
            },
            'languages': list(set(c.language for c in components.values())),
            'containerization_status': len([c for c in components.values() if c.packaging == 'docker']),
            'has_kubernetes': bool(infrastructure.get('orchestration', {}).get('kubernetes')),
            'has_docker_compose': bool(infrastructure.get('orchestration', {}).get('docker-compose')),
            'ci_cd_pipelines': len(ci_cd.get('github_actions', [])),
            'quality_gates': len(ci_cd.get('quality_gates', [])),
            'security_scans': len(ci_cd.get('security_scans', [])),
            'external_services': len(configuration.get('external_services', [])),
            'datasources': len(configuration.get('datasources', [])),
            'secrets_management': len(configuration.get('secrets_management', [])),
            'business_criticality': documentation.business_criticality,
            'compliance_requirements': documentation.compliance_requirements,
            'security_findings': {
                'hardcoded_secrets': sum(len(f.hardcoded_secrets) for f in security.values()),
                'vulnerabilities': sum(len(f.potential_vulnerabilities) for f in security.values())
            }
        }
        
        # Add git history summary if available
        if git_history:
            summary['git_history'] = {
                'total_commits': git_history.total_commits,
                'active_contributors': git_history.active_contributors,
                'code_stability': git_history.code_stability,
                'release_cadence': git_history.release_cadence,
                'hotspot_files_count': len(git_history.hotspot_files),
                'development_patterns': git_history.development_patterns
            }
        
        return summary
    
    def save_report(self, intelligence: ApplicationIntelligence, output_path: str):
        """Save intelligence report to file"""
        # Convert to dict for JSON serialization
        report_dict = asdict(intelligence)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"📋 Intelligence report saved to: {output_path}")
    
    def generate_markdown_report(self, intelligence: ApplicationIntelligence) -> str:
        """Generate human-readable markdown report"""
        report = f"""# Application Intelligence Report

**Repository:** {intelligence.repository_url}  
**Analysis Date:** {intelligence.analysis_timestamp}

## Executive Summary

- **Total Components:** {intelligence.summary['total_components']}
- **Business Criticality:** {intelligence.documentation_insights.business_criticality}
- **Architecture Style:** {intelligence.architecture_insights.get('architecture_style', 'Unknown')}
- **Languages:** {', '.join(intelligence.summary['languages'])}
- **Containerization:** {intelligence.summary['containerization_status']}/{intelligence.summary['total_components']} components

## Application Purpose

{intelligence.documentation_insights.application_purpose}

## Components

"""
        
        for name, component in intelligence.components.items():
            report += f"### {name}\n"
            report += f"- **Type:** {component.type}\n"
            report += f"- **Language:** {component.language}\n"
            report += f"- **Runtime:** {component.runtime}\n"
            report += f"- **Packaging:** {component.packaging}\n"
            if component.exposed_ports:
                report += f"- **Exposed Ports:** {', '.join(map(str, component.exposed_ports))}\n"
            report += "\n"
        
        report += f"""## Architecture Insights

- **Deployment Pattern:** {intelligence.architecture_insights.get('deployment_pattern', 'Unknown')}
- **Orchestration:** {intelligence.architecture_insights.get('orchestration_platform', 'None')}
- **CI/CD Maturity:** {intelligence.architecture_insights.get('ci_cd_maturity', 'Unknown')}
- **Microservices Score:** {intelligence.architecture_insights.get('microservices_score', 0)}/10

## Security Posture

- **Hardcoded Secrets:** {intelligence.summary['security_findings']['hardcoded_secrets']}
- **Vulnerabilities:** {intelligence.summary['security_findings']['vulnerabilities']}

## Development Patterns

"""
        
        # Add git history insights if available
        if intelligence.git_history:
            git_summary = intelligence.summary.get('git_history', {})
            report += f"""- **Total Commits:** {git_summary.get('total_commits', 0)}
- **Active Contributors:** {git_summary.get('active_contributors', 0)}
- **Code Stability:** {git_summary.get('code_stability', 'Unknown')}
- **Release Cadence:** {git_summary.get('release_cadence', 'Unknown')}
- **Hotspot Files:** {git_summary.get('hotspot_files_count', 0)} files frequently changed

### Development Patterns
"""
            patterns = git_summary.get('development_patterns', [])
            for pattern in patterns:
                report += f"- {pattern}\n"
        else:
            report += "- Git history analysis not available\n"
        
        report += f"""
## Compliance

**Requirements:** {', '.join(intelligence.documentation_insights.compliance_requirements) if intelligence.documentation_insights.compliance_requirements else 'None identified'}

## Comprehensive LLM Synthesis

"""
        
        # Add comprehensive synthesis if available
        if intelligence.comprehensive_synthesis:
            synthesis = intelligence.comprehensive_synthesis
            report += f"""
### Executive Summary
{synthesis.executive_summary}

### Architecture Assessment
{synthesis.architecture_assessment}

### Security Recommendations
{synthesis.security_recommendations}

### Migration Strategy
{synthesis.migration_strategy}

### Risk Assessment
{synthesis.risk_assessment}

"""
        else:
            report += "LLM synthesis not available (requires API key)\n"
        
        report += """## Recommendations

"""
        
        for rec in intelligence.recommendations:
            report += f"- {rec}\n"
        
        return report
    
    def _perform_post_analysis_correlation(self, components: Dict[str, ComponentInfo],
                                         infrastructure: Dict[str, Any],
                                         ci_cd: Dict[str, Any],
                                         configuration: Dict[str, Any],
                                         security: Dict[str, Any],
                                         documentation: DocumentationInsights,
                                         git_history: Optional[GitHistoryInsights]) -> None:
        """
        Post-Analysis Correlation and Synthesis Engine
        
        This method fixes the structured data (summary, components) to be as smart 
        as the LLM narrative by correlating all analysis results.
        """
        print("🔧 [CORRELATION] Fixing component names...")
        self._fix_component_names(components, infrastructure)
        
        print("🔍 [CORRELATION] Correlating languages from infrastructure...")
        self._correlate_languages_from_infrastructure(components, infrastructure)
        
        print("🐳 [CORRELATION] Fixing containerization status...")
        self._fix_containerization_status(components, infrastructure)
        
        print("💾 [CORRELATION] Extracting datasources...")
        self._extract_datasources_from_infrastructure(configuration, infrastructure)
        
        print("🔒 [CORRELATION] Fixing security findings...")
        self._fix_security_findings(security, components)
        
        print("📊 [CORRELATION] Fixing git history...")
        self._fix_git_history(git_history)
        
        print("✅ [CORRELATION] Post-analysis correlation complete!")
    
    def _fix_component_names(self, components: Dict[str, ComponentInfo], infrastructure: Dict[str, Any]):
        """Fix component names using deployment manifest names"""
        
        # Look for deployment configs to get proper names
        orchestration_data = infrastructure.get('orchestration', {}).get('kubernetes', [])
        
        component_name_mapping = {}
        
        # Handle different orchestration data structures
        for orchestration_item in orchestration_data:
            # Check if it's a list of resources or single resource
            resources = orchestration_item.get('resources', [orchestration_item])
            
            for config in resources:
                if config.get('kind') == 'DeploymentConfig':
                    config_name = config.get('name', '')
                    
                    # Map to existing components
                    for comp_name in components.keys():
                        if comp_name.lower() == 'src' and 'vote' in config_name.lower():
                            component_name_mapping[comp_name] = 'vote'
                        elif comp_name.lower() in config_name.lower():
                            component_name_mapping[comp_name] = config_name
                elif config.get('kind') == 'Service':
                    config_name = config.get('name', '')
                    
                    # Map to existing components
                    for comp_name in components.keys():
                        if comp_name.lower() == 'src' and 'vote' in config_name.lower():
                            component_name_mapping[comp_name] = 'vote'
                        elif comp_name.lower() in config_name.lower():
                            component_name_mapping[comp_name] = config_name
        
        # Apply name fixes
        for old_name, new_name in component_name_mapping.items():
            if old_name in components:
                components[old_name].name = new_name
                print(f"   - Fixed: {old_name} → {new_name}")
    
    def _correlate_languages_from_infrastructure(self, components: Dict[str, ComponentInfo], infrastructure: Dict[str, Any]):
        """Correlate component languages from Dockerfiles and base images"""
        
        # Base image to language mapping
        base_image_languages = {
            'node': 'nodejs',
            'nodejs': 'nodejs',
            'openjdk': 'java',
            'maven': 'java',
            'gradle': 'java',
            'python': 'python',
            'dotnet': 'csharp',
            'golang': 'go',
            'rust': 'rust',
            'ruby': 'ruby',
            'php': 'php'
        }
        
        # Get containerization data
        containerization_data = infrastructure.get('containerization', [])
        
        for dockerfile_info in containerization_data:
            # Handle different data structures
            if hasattr(dockerfile_info, 'data') and dockerfile_info.data:
                # Parse result format
                base_image = dockerfile_info.data.get('base_image', '')
                file_path = dockerfile_info.file_path or ''
            elif isinstance(dockerfile_info, dict):
                # Dictionary format
                base_image = dockerfile_info.get('base_image', '')
                file_path = dockerfile_info.get('file_path', '')
            else:
                # String format - skip
                continue
            
            if base_image:
                base_image = base_image.lower()
                
                # Extract component name from file path
                comp_name = self._extract_component_name_from_dockerfile_path(file_path)
                
                if comp_name and comp_name in components:
                    # Determine language from base image
                    for img_key, language in base_image_languages.items():
                        if img_key in base_image:
                            components[comp_name].language = language
                            components[comp_name].runtime = language
                            print(f"   - {comp_name}: {language} (from {base_image})")
                            break
    
    def _extract_component_name_from_dockerfile_path(self, file_path: str) -> str:
        """Extract component name from Dockerfile path"""
        if not file_path:
            return ''
        
        # Handle paths like "vote/Dockerfile" -> "vote"
        # Handle paths like "result/Dockerfile" -> "result"
        parts = file_path.replace('\\', '/').split('/')
        
        # Remove filename
        if parts and parts[-1].lower().startswith('dockerfile'):
            parts = parts[:-1]
        
        # Get the last directory name
        if parts:
            return parts[-1]
        
        return ''
    
    def _fix_containerization_status(self, components: Dict[str, ComponentInfo], infrastructure: Dict[str, Any]):
        """Fix containerization status count"""
        
        # Count actual Dockerfiles
        dockerfile_count = len(infrastructure.get('containerization', []))
        
        # Update component packaging based on Dockerfiles
        containerization_data = infrastructure.get('containerization', [])
        
        for dockerfile_info in containerization_data:
            # Handle different data structures
            if hasattr(dockerfile_info, 'file_path'):
                file_path = dockerfile_info.file_path or ''
            elif isinstance(dockerfile_info, dict):
                file_path = dockerfile_info.get('file_path', '')
            else:
                continue
                
            comp_name = self._extract_component_name_from_dockerfile_path(file_path)
            
            if comp_name and comp_name in components:
                components[comp_name].packaging = 'docker'
                print(f"   - {comp_name}: marked as containerized")
    
    def _extract_datasources_from_infrastructure(self, configuration: Dict[str, Any], infrastructure: Dict[str, Any]):
        """Extract datasources from infrastructure and orchestration data"""
        
        datasources = []
        
        # Look for templates and services that indicate datasources
        orchestration_data = infrastructure.get('orchestration', {}).get('kubernetes', [])
        
        datasource_indicators = {
            'postgresql': ['postgres', 'postgresql', 'psql'],
            'redis': ['redis', 'redis-server'],
            'mysql': ['mysql', 'mariadb'],
            'mongodb': ['mongo', 'mongodb'],
            'elasticsearch': ['elasticsearch', 'elastic']
        }
        
        # Handle different orchestration data structures
        for orchestration_item in orchestration_data:
            # Check if it's a list of resources or single resource
            resources = orchestration_item.get('resources', [orchestration_item])
            
            for config in resources:
                if config.get('kind') in ['Template', 'Service', 'DeploymentConfig']:
                    resource_name = config.get('name', '').lower()
                    
                    for ds_type, indicators in datasource_indicators.items():
                        if any(indicator in resource_name for indicator in indicators):
                            datasource_info = {
                                'type': ds_type,
                                'name': resource_name,
                                'deployment_type': 'ephemeral' if 'ephemeral' in resource_name else 'persistent'
                            }
                            if datasource_info not in datasources:
                                datasources.append(datasource_info)
                                print(f"   - Found datasource: {ds_type} ({resource_name})")
        
        # Update configuration
        if not configuration.get('datasources'):
            configuration['datasources'] = []
        configuration['datasources'].extend(datasources)
    
    def _fix_security_findings(self, security: Dict[str, Any], components: Dict[str, ComponentInfo]):
        """Fix security findings to show real vulnerabilities"""
        
        # Check for vulnerable base images
        vulnerable_base_images = {
            'node:10': 'Node.js 10 is EOL and contains numerous vulnerabilities',
            'node:12': 'Node.js 12 is EOL and contains vulnerabilities',
            'python:2': 'Python 2 is EOL and contains vulnerabilities',
            'openjdk:8': 'OpenJDK 8 contains known vulnerabilities',
            'maven:3.5': 'Maven 3.5 with JDK 8 contains vulnerabilities'
        }
        
        # Add base image vulnerabilities to security findings
        for comp_name, comp in components.items():
            if comp_name not in security:
                security[comp_name] = type('SecurityFindings', (), {
                    'hardcoded_secrets': [],
                    'potential_vulnerabilities': []
                })()
            
            # Check if component has vulnerable base images (from runtime info)
            if comp.runtime:
                for vuln_image, description in vulnerable_base_images.items():
                    if vuln_image in comp.runtime:
                        security[comp_name].potential_vulnerabilities.append({
                            'type': 'vulnerable_base_image',
                            'description': description,
                            'severity': 'HIGH',
                            'component': comp_name
                        })
                        print(f"   - {comp_name}: Added vulnerability for {vuln_image}")
    
    def _fix_git_history(self, git_history: Optional[GitHistoryInsights]):
        """Fix git history data if analysis failed"""
        
        if git_history and git_history.total_commits == 0:
            # Mark as failed rather than showing misleading 0
            git_history.code_stability = "analysis_failed"
            git_history.release_cadence = "Analysis failed - repository may be shallow clone"
            print("   - Git history marked as failed (not 0 commits)")
        elif git_history:
            print(f"   - Git history: {git_history.total_commits} commits, {git_history.active_contributors} contributors")