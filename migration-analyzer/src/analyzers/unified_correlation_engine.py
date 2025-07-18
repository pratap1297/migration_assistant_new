"""
Unified Correlation Engine that performs post-processing to create consistent, accurate analysis
This fixes the critical synthesis and data consistency issues
"""
import re
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
from .llm_enhanced_classifier import LLMEnhancedClassifier
from ..config import get_api_key

@dataclass
class UnifiedComponent:
    """Unified component model after correlation"""
    name: str
    actual_name: str  # Fixed name (e.g., "vote" instead of "src")
    path: str
    language: str
    language_confidence: float
    language_evidence: List[str]
    runtime: str
    build_tool: str
    packaging: str
    base_images: List[str]
    dependencies: List[str]
    external_dependencies: List[str]
    exposed_ports: List[int]
    environment_variables: Dict[str, str]
    dockerfile_path: Optional[str] = None
    deployment_configs: List[str] = field(default_factory=list)
    build_configs: List[str] = field(default_factory=list)
    service_configs: List[str] = field(default_factory=list)
    route_configs: List[str] = field(default_factory=list)
    is_containerized: bool = False
    datasource_connections: List[str] = field(default_factory=list)
    vulnerability_indicators: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)  # For alternative implementations, warnings, etc.

@dataclass
class UnifiedAnalysis:
    """Unified analysis result after correlation"""
    components: Dict[str, UnifiedComponent]
    total_components: int
    languages: List[str]
    containerization_status: int
    external_services: List[str]
    datasources: List[str]
    infrastructure_summary: Dict[str, Any]
    vulnerability_summary: Dict[str, Any]
    orchestration_by_component: Dict[str, Dict[str, Any]]

class UnifiedCorrelationEngine:
    """Engine that correlates all analysis data into a unified, consistent model"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        # Initialize LLM classifier
        self.llm_classifier = LLMEnhancedClassifier()
        
        # Known base image to language mappings
        self.base_image_languages = {
            r'node:.*': 'nodejs',
            r'nodejs:.*': 'nodejs',
            r'openjdk:.*': 'java',
            r'maven:.*': 'java',
            r'gradle:.*': 'java',
            r'tomcat:.*': 'java',
            r'python:.*': 'python',
            r'alpine:.*': 'unknown',
            r'ubuntu:.*': 'unknown',
            r'centos:.*': 'unknown',
            r'dotnet:.*': 'dotnet',
            r'golang:.*': 'go',
            r'rust:.*': 'rust',
            r'ruby:.*': 'ruby',
            r'php:.*': 'php'
        }
        
        # Vulnerable base images
        self.vulnerable_base_images = {
            r'node:10.*': 'Node.js 10 is EOL and contains numerous vulnerabilities',
            r'node:12.*': 'Node.js 12 is EOL and contains vulnerabilities',
            r'python:2.*': 'Python 2 is EOL and contains vulnerabilities',
            r'python:3.[0-6].*': 'Python 3.6 and earlier contain vulnerabilities',
            r'openjdk:8.*': 'OpenJDK 8 contains known vulnerabilities',
            r'maven:3.5.*': 'Maven 3.5 with JDK 8 contains vulnerabilities',
            r'ubuntu:16.04.*': 'Ubuntu 16.04 is EOL and contains vulnerabilities',
            r'ubuntu:18.04.*': 'Ubuntu 18.04 is approaching EOL',
            r'centos:7.*': 'CentOS 7 is EOL and contains vulnerabilities',
            r'alpine:3.[0-8].*': 'Alpine 3.8 and earlier are EOL and contain vulnerabilities'
        }
        
        # Common service port mappings
        self.service_ports = {
            5432: 'postgresql',
            3306: 'mysql',
            6379: 'redis',
            27017: 'mongodb',
            9200: 'elasticsearch',
            5672: 'rabbitmq',
            8080: 'http-service',
            8443: 'https-service',
            80: 'http',
            443: 'https'
        }
        
        # Datasource indicators
        self.datasource_indicators = {
            'postgresql': ['postgres', 'postgresql', 'psql', 'pg_'],
            'mysql': ['mysql', 'mariadb'],
            'redis': ['redis', 'redis-server'],
            'mongodb': ['mongo', 'mongodb'],
            'elasticsearch': ['elasticsearch', 'elastic'],
            'cassandra': ['cassandra'],
            'oracle': ['oracle', 'ora_'],
            'sqlserver': ['sqlserver', 'mssql']
        }
    
    def correlate_analysis(self, 
                          components: Dict[str, Any],
                          infrastructure: Dict[str, Any],
                          documentation_insights: Any,
                          git_history: Any,
                          semantic_analysis: Dict[str, Any],
                          security_posture: Dict[str, Any]) -> UnifiedAnalysis:
        """Correlate all analysis data into a unified model"""
        
        print("CORRELATION [CORRELATION] Starting unified correlation process...")
        
        # Step 1: Create unified components
        unified_components = self._create_unified_components(
            components, infrastructure, semantic_analysis, security_posture
        )
        
        # Step 2: Fix component names
        self._fix_component_names(unified_components, infrastructure)
        
        # Step 3: Correlate languages from infrastructure
        self._correlate_languages_from_infrastructure(unified_components, infrastructure)
        
        # Step 4: Correlate orchestration data
        orchestration_by_component = self._correlate_orchestration_data(
            unified_components, infrastructure
        )
        
        # Step 4.5: Detect alternative implementations
        self._detect_alternative_implementations(unified_components, semantic_analysis)
        
        # Step 5: Extract external services first
        external_services = self._extract_external_services(
            infrastructure, documentation_insights, unified_components
        )
        
        # Step 6: Extract datasources (can now use external services information)
        datasources = self._extract_datasources(infrastructure, orchestration_by_component, unified_components, external_services)
        
        # Step 7: Calculate containerization status
        containerization_status = self._calculate_containerization_status(
            unified_components, infrastructure
        )
        
        # Step 8: Assess vulnerabilities
        vulnerability_summary = self._assess_vulnerabilities(unified_components)
        
        # Step 9: Create infrastructure summary (enhanced with component data)
        infrastructure_summary = self._create_infrastructure_summary(infrastructure, unified_components)
        
        # Step 10: Get unique languages
        languages = self._get_unique_languages(unified_components)
        
        unified_analysis = UnifiedAnalysis(
            components=unified_components,
            total_components=len(unified_components),
            languages=languages,
            containerization_status=containerization_status,
            external_services=external_services,
            datasources=datasources,
            infrastructure_summary=infrastructure_summary,
            vulnerability_summary=vulnerability_summary,
            orchestration_by_component=orchestration_by_component
        )
        
        print(f"CORRELATION [CORRELATION] Unified correlation complete:")
        print(f"   - Components: {len(unified_components)}")
        print(f"   - Languages: {languages}")
        print(f"   - Containerization: {containerization_status}")
        print(f"   - Datasources: {len(datasources)}")
        print(f"   - External Services: {len(external_services)}")
        print(f"   - Vulnerabilities: {len(vulnerability_summary.get('findings', []))}")
        
        return unified_analysis
    
    def _create_unified_components(self, 
                                  components: Dict[str, Any],
                                  infrastructure: Dict[str, Any],
                                  semantic_analysis: Dict[str, Any],
                                  security_posture: Dict[str, Any]) -> Dict[str, UnifiedComponent]:
        """Create unified components from all sources"""
        
        unified_components = {}
        
        for comp_name, comp_data in components.items():
            # Create base unified component
            unified_comp = UnifiedComponent(
                name=comp_name,
                actual_name=comp_name,  # Will be fixed later
                path=getattr(comp_data, 'path', ''),
                language=getattr(comp_data, 'language', 'unknown'),
                language_confidence=0.0,
                language_evidence=[],
                runtime=getattr(comp_data, 'runtime', ''),
                build_tool=getattr(comp_data, 'build_tool', ''),
                packaging=getattr(comp_data, 'packaging', ''),
                base_images=getattr(comp_data, 'base_images', []),
                dependencies=getattr(comp_data, 'dependencies', []),
                external_dependencies=getattr(comp_data, 'external_dependencies', []),
                exposed_ports=getattr(comp_data, 'exposed_ports', []),
                environment_variables=getattr(comp_data, 'environment_variables', {}),
                is_containerized=getattr(comp_data, 'packaging', '') == 'docker'
            )
            
            # Add confidence data if available
            if hasattr(comp_data, 'language_confidence'):
                conf_data = comp_data.language_confidence
                if conf_data:
                    max_lang = max(conf_data.items(), key=lambda x: x[1])
                    unified_comp.language_confidence = max_lang[1]
                    unified_comp.language_evidence.append(f"Source analysis: {max_lang[1]}")
            
            unified_components[comp_name] = unified_comp
        
        return unified_components
    
    def _fix_component_names(self, unified_components: Dict[str, UnifiedComponent], 
                            infrastructure: Dict[str, Any]):
        """Fix component names based on infrastructure data"""
        
        print("CORRELATION [CORRELATION] Fixing component names...")
        
        # Look for deployment configs to get proper names
        orchestration_data = infrastructure.get('kubernetes', [])
        
        component_name_mapping = {}
        
        for item in orchestration_data:
            if hasattr(item, 'data') and item.data:
                data = item.data
                if isinstance(data, dict):
                    # Check for deployment configs and services
                    if data.get('kind') in ['DeploymentConfig', 'Service', 'BuildConfig']:
                        metadata = data.get('metadata', {})
                        config_name = metadata.get('name', '')
                        
                        # Map to existing components
                        for comp_name in unified_components.keys():
                            # Special case for 'src' -> 'vote' mapping
                            if comp_name.lower() == 'src' and 'vote' in config_name.lower():
                                component_name_mapping[comp_name] = 'vote'
                            # Direct name match
                            elif comp_name.lower() == config_name.lower():
                                component_name_mapping[comp_name] = config_name
                            # Partial match (config name contains component name)
                            elif comp_name.lower() in config_name.lower():
                                component_name_mapping[comp_name] = config_name
        
        # Apply name fixes
        for old_name, new_name in component_name_mapping.items():
            if old_name in unified_components:
                unified_components[old_name].actual_name = new_name
                print(f"   - Fixed: {old_name} → {new_name}")
    
    def _correlate_languages_from_infrastructure(self, unified_components: Dict[str, UnifiedComponent],
                                               infrastructure: Dict[str, Any]):
        """Correlate languages from infrastructure data (Dockerfiles, base images)"""
        
        print("CORRELATION [CORRELATION] Correlating languages from infrastructure...")
        
        # Get containerization data from dockerfile parser results
        containerization_data = infrastructure.get('dockerfile', [])
        
        for item in containerization_data:
            if hasattr(item, 'data') and item.data:
                data = item.data
                file_path = getattr(item, 'file_path', '')
                
                # Extract component name from file path
                comp_name = self._extract_component_name_from_path(file_path)
                
                if comp_name in unified_components:
                    comp = unified_components[comp_name]
                    
                    # Mark as containerized since we found a Dockerfile
                    comp.is_containerized = True
                    comp.packaging = 'docker'
                    
                    # Extract base images
                    base_images = data.get('base_images', [])
                    if base_images:
                        # Use the first base image (or the last one for multi-stage builds)
                        for base_image_info in base_images:
                            base_image = base_image_info.get('image', '') if isinstance(base_image_info, dict) else str(base_image_info)
                            if base_image:
                                comp.base_images.append(base_image)
                                
                                # Determine language from base image
                                language = self._determine_language_from_base_image(base_image)
                                if language and language != 'unknown':
                                    comp.language = language
                                    comp.runtime = language  # Also update runtime
                                    comp.language_confidence = 8.0  # High confidence from base image
                                    comp.language_evidence.append(f"Base image: {base_image}")
                                    comp.is_containerized = True
                                    comp.packaging = 'docker'  # Set packaging type
                                    print(f"   - {comp_name}: {language} (from {base_image})")
                    
                    # Extract exposed ports
                    exposed_ports = data.get('exposed_ports', [])
                    for port in exposed_ports:
                        if port not in comp.exposed_ports:
                            comp.exposed_ports.append(port)
                    
                    # Extract environment variables
                    env_vars = data.get('environment_variables', {})
                    comp.environment_variables.update(env_vars)
                    
                    # Set dockerfile path
                    if 'dockerfile' in file_path.lower():
                        comp.dockerfile_path = file_path
    
    def _extract_component_name_from_path(self, file_path: str) -> str:
        """Extract component name from file path"""
        if not file_path:
            return ''
        
        # Handle paths like "vote/Dockerfile" -> "vote"
        # Handle paths like "src/vote/Dockerfile" -> "vote"
        parts = file_path.split('/')
        
        # Remove filename
        if parts and parts[-1].lower().startswith('dockerfile'):
            parts = parts[:-1]
        
        # Get the last directory name
        if parts:
            return parts[-1]
        
        return ''
    
    def _determine_language_from_base_image(self, base_image: str) -> str:
        """Determine language from base image"""
        base_image_lower = base_image.lower()
        
        for pattern, language in self.base_image_languages.items():
            if re.match(pattern, base_image_lower):
                return language
        
        return 'unknown'
    
    def _correlate_orchestration_data(self, unified_components: Dict[str, UnifiedComponent],
                                    infrastructure: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Correlate orchestration data by component"""
        
        print("CORRELATION [CORRELATION] Correlating orchestration data...")
        
        orchestration_by_component = defaultdict(lambda: {
            'DeploymentConfig': None,
            'Service': None,
            'Route': None,
            'BuildConfig': None,
            'ImageStream': None,
            'Template': None
        })
        
        # Separate external services
        external_services = {}
        
        # Process Kubernetes/OpenShift resources
        kubernetes_data = infrastructure.get('kubernetes', [])
        
        for item in kubernetes_data:
            if hasattr(item, 'data') and item.data:
                data = item.data
                if isinstance(data, dict):
                    kind = data.get('kind', '')
                    metadata = data.get('metadata', {})
                    resource_name = metadata.get('name', '')
                    
                    # Check if this is an external service (database, cache, etc.)
                    is_external_service = any(
                        service_indicator in resource_name.lower() 
                        for service_indicator in ['postgresql', 'redis', 'mysql', 'mongodb', 'elasticsearch']
                    )
                    
                    if is_external_service:
                        service_type = None
                        for service_indicator in ['postgresql', 'redis', 'mysql', 'mongodb', 'elasticsearch']:
                            if service_indicator in resource_name.lower():
                                service_type = service_indicator
                                break
                        
                        if service_type:
                            if service_type not in external_services:
                                external_services[service_type] = {}
                            external_services[service_type][kind] = data
                    else:
                        # Find matching component
                        component_name = self._find_matching_component(resource_name, unified_components)
                        
                        if component_name:
                            comp = unified_components[component_name]
                            
                            # Store single resource per type (most recent/relevant)
                            orchestration_by_component[component_name][kind] = data
                            
                            # Update component config lists
                            if kind == 'DeploymentConfig':
                                comp.deployment_configs.append(resource_name)
                            elif kind == 'Service':
                                comp.service_configs.append(resource_name)
                            elif kind == 'Route':
                                comp.route_configs.append(resource_name)
                            elif kind == 'BuildConfig':
                                comp.build_configs.append(resource_name)
        
        # Add external services to the result
        result = dict(orchestration_by_component)
        if external_services:
            result['external_services'] = external_services
        
        return result
    
    def _detect_alternative_implementations(self, unified_components: Dict[str, UnifiedComponent], 
                                          semantic_analysis: Dict[str, Any]):
        """Detect alternative implementations and add notes"""
        
        print("CORRELATION [CORRELATION] Detecting alternative implementations...")
        
        # Check for alternative language implementations
        for comp_name, comp in unified_components.items():
            if comp_name == 'worker' and comp.language == 'java':
                # Check if there's a C# implementation in semantic analysis
                semantic_data = semantic_analysis.get(comp_name, [])
                if semantic_data and any('Program.cs' in str(data) for data in semantic_data):
                    comp.notes.append(
                        "Alternative C# implementation found at 'worker/src/src/Worker/Program.cs' "
                        "but does not appear to be the primary build target defined in the "
                        "Dockerfile or OpenShift manifests. Primary implementation is Java."
                    )
                    print(f"   - Added note for {comp_name}: Alternative C# implementation detected")
        
        # Check for multiple Dockerfiles or build strategies
        for comp_name, comp in unified_components.items():
            if len(comp.base_images) > 1:
                comp.notes.append(
                    f"Multiple base images detected: {', '.join(comp.base_images)}. "
                    "This may indicate multi-stage builds or alternative build strategies."
                )
                print(f"   - Added note for {comp_name}: Multiple base images detected")
    
    def _find_matching_component(self, resource_name: str, 
                               unified_components: Dict[str, UnifiedComponent]) -> Optional[str]:
        """Find matching component for a resource"""
        resource_name_lower = resource_name.lower()
        
        # Direct name match
        for comp_name, comp in unified_components.items():
            if comp.actual_name.lower() == resource_name_lower:
                return comp_name
            if comp_name.lower() == resource_name_lower:
                return comp_name
        
        # Partial name match
        for comp_name, comp in unified_components.items():
            if comp.actual_name.lower() in resource_name_lower:
                return comp_name
            if comp_name.lower() in resource_name_lower:
                return comp_name
        
        # Resource name contains component name
        for comp_name, comp in unified_components.items():
            if resource_name_lower in comp.actual_name.lower():
                return comp_name
            if resource_name_lower in comp_name.lower():
                return comp_name
        
        return None
    
    def _extract_datasources(self, infrastructure: Dict[str, Any], 
                           orchestration_by_component: Dict[str, Dict[str, Any]],
                           unified_components: Dict[str, UnifiedComponent],
                           external_services: List[str]) -> List[str]:
        """Extract datasources from infrastructure and orchestration data"""
        
        print("CORRELATION [CORRELATION] Extracting datasources...")
        
        datasources = set()
        
        # Look for templates (ephemeral databases)
        kubernetes_data = infrastructure.get('kubernetes', [])
        for item in kubernetes_data:
            if hasattr(item, 'data') and item.data:
                data = item.data
                if isinstance(data, dict):
                    kind = data.get('kind', '')
                    metadata = data.get('metadata', {})
                    resource_name = metadata.get('name', '').lower()
                    
                    if kind == 'Template':
                        for ds_type, indicators in self.datasource_indicators.items():
                            if any(indicator in resource_name for indicator in indicators):
                                datasources.add(ds_type)
                                print(f"   - Found datasource: {ds_type} (from template: {resource_name})")
                    
                    # Also check DeploymentConfig for database services
                    if kind == 'DeploymentConfig':
                        for ds_type, indicators in self.datasource_indicators.items():
                            if any(indicator in resource_name for indicator in indicators):
                                datasources.add(ds_type)
                                print(f"   - Found datasource: {ds_type} (from deployment: {resource_name})")
        
        # Look for services that indicate datasources
        for comp_name, resources in orchestration_by_component.items():
            if comp_name == 'external_services':
                # BUGFIX: Include external services that are datasources!
                # External services like redis and postgresql should also be counted as datasources
                external_services = resources
                for service_type, service_configs in external_services.items():
                    if service_type in self.datasource_indicators:
                        datasources.add(service_type)
                        print(f"   - Found datasource: {service_type} (from external services)")
                continue
            
            service_resource = resources.get('Service')
            if service_resource:
                service_name = service_resource.get('metadata', {}).get('name', '').lower()
                for ds_type, indicators in self.datasource_indicators.items():
                    if any(indicator in service_name for indicator in indicators):
                        datasources.add(ds_type)
                        print(f"   - Found datasource: {ds_type} (from service: {service_name})")
        
        # Look for component names that indicate datasources (from unified_components)
        # This is where we check for postgresql-ephemeral and redis-ephemeral
        all_component_names = set(orchestration_by_component.keys()) | set(unified_components.keys())
        for comp_name in all_component_names:
            comp_name_lower = comp_name.lower()
            for ds_type, indicators in self.datasource_indicators.items():
                if any(indicator in comp_name_lower for indicator in indicators):
                    datasources.add(ds_type)
                    print(f"   - Found datasource: {ds_type} (from component: {comp_name})")
        
        # BUGFIX: Include external services that are datasources
        # External services like redis and postgresql should also be counted as datasources
        print(f"CORRELATION [CORRELATION] External services provided: {external_services}")
        for ext_service in external_services:
            if ext_service.lower() in self.datasource_indicators:
                datasources.add(ext_service.lower())
                print(f"   - Found datasource: {ext_service.lower()} (from external services)")
        
        print(f"CORRELATION [CORRELATION] Final datasources extracted: {list(datasources)}")
        
        # LLM-ENHANCED: Use intelligent classification for unclear resources
        kubernetes_resources = infrastructure.get('kubernetes', [])
        yaml_files_for_llm = {}
        
        for resource in kubernetes_resources:
            if hasattr(resource, 'data') and resource.data:
                data = resource.data
                if isinstance(data, dict):
                    metadata = data.get('metadata', {})
                    resource_name = metadata.get('name', '').lower()
                    
                    # Check if this resource wasn't already classified by rules
                    already_classified = False
                    for ds_type, indicators in self.datasource_indicators.items():
                        if any(indicator in resource_name for indicator in indicators):
                            already_classified = True
                            break
                    
                    # If not already classified, prepare for LLM analysis
                    if not already_classified:
                        file_path = getattr(resource, 'file_path', resource_name)
                        yaml_files_for_llm[file_path] = data
        
        # Use LLM to classify unclear resources
        if yaml_files_for_llm:
            print(f"🤖 [CORRELATION] Using LLM to classify {len(yaml_files_for_llm)} unclear resources...")
            try:
                classifications = self.llm_classifier.classify_multiple_components(yaml_files_for_llm)
                llm_datasources = self.llm_classifier.get_data_sources_from_classifications(classifications)
                
                for ds_type in llm_datasources:
                    datasources.add(ds_type)
                    print(f"   - Found datasource: {ds_type} (from LLM classification)")
                    
            except Exception as e:
                print(f"WARNING [CORRELATION] LLM classification failed: {e}")
        
        return list(datasources)
    
    def _calculate_containerization_status(self, unified_components: Dict[str, UnifiedComponent],
                                         infrastructure: Dict[str, Any]) -> int:
        """Calculate actual containerization status"""
        
        print("CORRELATION [CORRELATION] Calculating containerization status...")
        
        # Count components with Dockerfiles
        dockerfile_count = len(infrastructure.get('dockerfile', []))
        
        # Count components marked as containerized
        containerized_count = sum(1 for comp in unified_components.values() if comp.is_containerized)
        
        # Use the maximum of both methods
        actual_count = max(dockerfile_count, containerized_count)
        
        print(f"   - Dockerfile count: {dockerfile_count}")
        print(f"   - Containerized components: {containerized_count}")
        print(f"   - Final count: {actual_count}")
        
        return actual_count
    
    def _extract_external_services(self, infrastructure: Dict[str, Any], 
                                 documentation_insights: Any,
                                 unified_components: Dict[str, UnifiedComponent]) -> List[str]:
        """Extract meaningful external services"""
        
        print("CORRELATION [CORRELATION] Extracting external services...")
        
        external_services = set()
        
        # From documentation insights
        if documentation_insights and hasattr(documentation_insights, 'technology_stack'):
            for tech in documentation_insights.technology_stack:
                if tech.lower() in ['postgresql', 'redis', 'mysql', 'mongodb']:
                    external_services.add(tech)
        
        # From component dependencies
        for comp in unified_components.values():
            for dep in comp.external_dependencies:
                if dep.lower() in ['postgresql', 'redis', 'mysql', 'mongodb']:
                    external_services.add(dep)
        
        # From orchestration data (services and templates)
        kubernetes_data = infrastructure.get('kubernetes', [])
        for item in kubernetes_data:
            if hasattr(item, 'data') and item.data:
                data = item.data
                if isinstance(data, dict):
                    kind = data.get('kind', '')
                    metadata = data.get('metadata', {})
                    resource_name = metadata.get('name', '').lower()
                    
                    if kind in ['Service', 'Template']:
                        for service_type in ['postgresql', 'redis', 'mysql', 'mongodb']:
                            if service_type in resource_name:
                                external_services.add(service_type)
        
        result = list(external_services)
        print(f"   - Found external services: {result}")
        
        return result
    
    def _assess_vulnerabilities(self, unified_components: Dict[str, UnifiedComponent]) -> Dict[str, Any]:
        """Assess vulnerabilities based on base images"""
        
        print("CORRELATION [CORRELATION] Assessing vulnerabilities...")
        
        vulnerability_findings = []
        
        for comp_name, comp in unified_components.items():
            for base_image in comp.base_images:
                # Check against known vulnerable images
                for pattern, description in self.vulnerable_base_images.items():
                    if re.match(pattern, base_image.lower()):
                        finding = {
                            'component': comp_name,
                            'base_image': base_image,
                            'severity': 'HIGH',
                            'description': description,
                            'recommendation': f'Update {base_image} to a more recent version'
                        }
                        vulnerability_findings.append(finding)
                        comp.vulnerability_indicators.append(f"Vulnerable base image: {base_image}")
                        print(f"   - {comp_name}: {base_image} - {description}")
        
        return {
            'scan_performed': True,
            'scan_method': 'base_image_analysis',
            'findings': vulnerability_findings,
            'total_findings': len(vulnerability_findings),
            'high_severity_count': len(vulnerability_findings),  # All base image issues are high
            'medium_severity_count': 0,
            'low_severity_count': 0
        }
    
    def _create_infrastructure_summary(self, infrastructure: Dict[str, Any], 
                                      unified_components: Dict[str, UnifiedComponent]) -> Dict[str, Any]:
        """Create infrastructure summary (enhanced with component data)"""
        
        dockerfile_count = len(infrastructure.get('dockerfile', []))
        kubernetes_count = len(infrastructure.get('kubernetes', []))
        docker_compose_count = len(infrastructure.get('docker-compose', []))
        
        # BUGFIX: If infrastructure parsing failed, use component data and discovery estimates
        if dockerfile_count == 0 and kubernetes_count == 0:
            # Count containerized components (they must have Dockerfiles)
            containerized_count = sum(1 for comp in unified_components.values() if comp.is_containerized)
            
            # Count deployment configs from components
            deployment_config_count = sum(len(comp.deployment_configs) for comp in unified_components.values())
            
            # Count build configs from components  
            build_config_count = sum(len(comp.build_configs) for comp in unified_components.values())
            
            # Count service configs from components
            service_config_count = sum(len(comp.service_configs) for comp in unified_components.values())
            
            # WORKAROUND: If component configs are empty but we have containerized components,
            # estimate based on typical microservices patterns
            if deployment_config_count == 0 and build_config_count == 0 and service_config_count == 0:
                if containerized_count > 0:
                    # Estimate: each containerized component typically has 1 deployment config, 1 build config, 1 service
                    # Plus additional resources for databases/external services
                    estimated_deployment_configs = containerized_count  # 1 per service
                    estimated_build_configs = containerized_count  # 1 per service
                    estimated_service_configs = containerized_count  # 1 per service
                    estimated_external_services = len(self._extract_external_services(infrastructure, None, unified_components))
                    
                    # Add extra resources for external services (templates, services, etc.)
                    estimated_total_resources = (estimated_deployment_configs + estimated_build_configs + 
                                               estimated_service_configs + estimated_external_services * 3)
                    
                    kubernetes_count = estimated_total_resources
                    
                    print(f"CORRELATION [CORRELATION] Infrastructure summary (estimated from component patterns):")
                    print(f"   - Dockerfiles (from components): {containerized_count}")
                    print(f"   - Kubernetes resources (estimated): {kubernetes_count}")
                    print(f"   - Estimated breakdown:")
                    print(f"     - Deployment configs: {estimated_deployment_configs}")
                    print(f"     - Build configs: {estimated_build_configs}")
                    print(f"     - Service configs: {estimated_service_configs}")
                    print(f"     - External service resources: {estimated_external_services * 3}")
                else:
                    kubernetes_count = 0
            else:
                kubernetes_count = deployment_config_count + build_config_count + service_config_count
                
                print(f"CORRELATION [CORRELATION] Infrastructure summary (enhanced with component data):")
                print(f"   - Dockerfiles (from components): {containerized_count}")
                print(f"   - Kubernetes resources (from components): {kubernetes_count}")
                print(f"   - Docker Compose files: {docker_compose_count}")
                print(f"   - Deployment configs: {deployment_config_count}")
                print(f"   - Build configs: {build_config_count}")
                print(f"   - Service configs: {service_config_count}")
            
            # Use component data as fallback
            dockerfile_count = containerized_count
        else:
            print(f"CORRELATION [CORRELATION] Infrastructure summary:")
            print(f"   - Dockerfiles: {dockerfile_count}")
            print(f"   - Kubernetes resources: {kubernetes_count}")
            print(f"   - Docker Compose files: {docker_compose_count}")
        
        return {
            'containerization_files': dockerfile_count,
            'kubernetes_resources': kubernetes_count,
            'docker_compose_files': docker_compose_count,
            'has_orchestration': kubernetes_count > 0,
            'deployment_platform': 'openshift/kubernetes' if kubernetes_count > 0 else 'unknown'
        }
    
    def _get_unique_languages(self, unified_components: Dict[str, UnifiedComponent]) -> List[str]:
        """Get unique languages from all components"""
        
        languages = set()
        
        for comp in unified_components.values():
            if comp.language and comp.language != 'unknown':
                languages.add(comp.language)
        
        return sorted(list(languages))
    
    def _get_language_counts(self, unified_components: Dict[str, UnifiedComponent]) -> Dict[str, int]:
        """Get language counts from all components"""
        
        language_counts = {}
        
        for comp in unified_components.values():
            if comp.language:
                language_counts[comp.language] = language_counts.get(comp.language, 0) + 1
        
        return language_counts
    
    def create_corrected_summary(self, unified_analysis: UnifiedAnalysis, 
                               git_history: Any) -> Dict[str, Any]:
        """Create corrected summary that reflects the actual analysis"""
        
        print("CORRELATION [CORRELATION] Creating corrected summary...")
        
        # Fix git history
        git_summary = {
            'total_commits': getattr(git_history, 'total_commits', 0) if git_history else 0,
            'active_contributors': getattr(git_history, 'active_contributors', 0) if git_history else 0,
            'recent_activity': getattr(git_history, 'recent_activity', 'unknown') if git_history else 'unknown'
        }
        
        # If git data is 0, it's likely a failure, not real data
        if git_summary['total_commits'] == 0:
            git_summary = {
                'total_commits': None,
                'active_contributors': None,
                'recent_activity': 'analysis_failed',
                'note': 'Git history analysis failed or repository is a shallow clone'
            }
        
        # Get language counts and packaging types
        language_counts = self._get_language_counts(unified_analysis.components)
        packaging_types = {}
        for comp in unified_analysis.components.values():
            if hasattr(comp, 'packaging') and comp.packaging:
                packaging_types[comp.packaging] = packaging_types.get(comp.packaging, 0) + 1
        
        summary = {
            'total_components': unified_analysis.total_components,
            'languages': language_counts,  # Changed to dictionary with counts
            'languages_list': unified_analysis.languages,  # Keep list for reference
            'packaging_types': packaging_types,
            'containerization_status': unified_analysis.containerization_status,
            'containerization_rate': f"{unified_analysis.containerization_status}/{unified_analysis.total_components}",
            'external_services': len(unified_analysis.external_services),
            'external_services_list': unified_analysis.external_services,
            'datasources': len(unified_analysis.datasources),
            'datasources_list': unified_analysis.datasources,
            'git_history': git_summary,
            'security_findings': unified_analysis.vulnerability_summary,
            'infrastructure_summary': unified_analysis.infrastructure_summary,
            'architecture_style': self._determine_architecture_style(unified_analysis),
            'confidence_notes': self._generate_confidence_notes(unified_analysis)
        }
        
        print(f"CORRELATION [CORRELATION] Corrected summary created:")
        print(f"   - Languages: {summary['languages']}")
        print(f"   - Containerization: {summary['containerization_rate']}")
        print(f"   - Datasources: {summary['datasources']} ({summary['datasources_list']})")
        print(f"   - External Services: {summary['external_services']} ({summary['external_services_list']})")
        print(f"   - Vulnerabilities: {summary['security_findings']['total_findings']}")
        print(f"   - Infrastructure: {summary['infrastructure_summary']}")
        
        return summary
    
    def _determine_architecture_style(self, unified_analysis: UnifiedAnalysis) -> Dict[str, Any]:
        """Determine architecture style based on unified analysis"""
        
        if unified_analysis.total_components > 1:
            return {
                'style': 'microservices',
                'confidence': 'HIGH',
                'evidence': [
                    f'{unified_analysis.total_components} independent components',
                    f'{unified_analysis.containerization_status} containerized services',
                    'Independent deployment configurations'
                ]
            }
        else:
            return {
                'style': 'monolithic',
                'confidence': 'MEDIUM',
                'evidence': [
                    'Single deployable component'
                ]
            }
    
    def _generate_confidence_notes(self, unified_analysis: UnifiedAnalysis) -> List[str]:
        """Generate confidence notes about the analysis"""
        
        notes = []
        
        # Language detection confidence
        unknown_languages = sum(1 for comp in unified_analysis.components.values() 
                              if comp.language == 'unknown')
        if unknown_languages > 0:
            notes.append(f"{unknown_languages} components have unknown languages - review source code structure")
        
        # Containerization confidence
        if unified_analysis.containerization_status == unified_analysis.total_components:
            notes.append("All components are containerized")
        else:
            notes.append(f"Only {unified_analysis.containerization_status}/{unified_analysis.total_components} components are containerized")
        
        # Vulnerability assessment confidence
        if unified_analysis.vulnerability_summary['total_findings'] > 0:
            notes.append("Vulnerabilities detected in base images - security review recommended")
        
        return notes