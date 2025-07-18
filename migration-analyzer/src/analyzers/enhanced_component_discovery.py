"""
Enhanced component discovery analyzer using cross-artifact correlation
This fixes the critical "Language: unknown" issue by properly correlating artifacts
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from src.parsers.base import AbstractParser, ParseResult
from src.parsers.infrastructure.dockerfile import DockerfileParser
from src.parsers.infrastructure.docker_compose import DockerComposeParser
from src.parsers.infrastructure.kubernetes import KubernetesParser
from src.analyzers.cross_artifact_correlator import CrossArtifactCorrelator, ArtifactEvidence

@dataclass
class EnhancedComponentInfo:
    """Enhanced information about a discovered component with correlation evidence"""
    name: str
    path: str
    type: str  # 'microservice', 'library', 'frontend', 'database', 'infrastructure'
    language: str
    language_confidence: Dict[str, float] = field(default_factory=dict)
    runtime: str = ""
    build_tool: str = ""
    packaging: str = ""  # 'docker', 'jar', 'npm', 'wheel', etc.
    dependencies: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    exposed_ports: List[int] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    health_checks: List[str] = field(default_factory=list)
    deployment_info: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    
    # New fields for correlation evidence
    docker_files: List[str] = field(default_factory=list)
    base_images: List[str] = field(default_factory=list)
    s2i_images: List[str] = field(default_factory=list)
    has_deployment_config: bool = False
    has_build_config: bool = False
    source_files_found: int = 0
    correlation_evidence: Optional[ArtifactEvidence] = None

class EnhancedComponentDiscoveryAnalyzer:
    """Enhanced analyzer that correlates deployment artifacts with source code"""
    
    def __init__(self):
        self.parsers = {
            'dockerfile': DockerfileParser(),
            'docker-compose': DockerComposeParser(),
            'kubernetes': KubernetesParser()
        }
        
        self.correlator = CrossArtifactCorrelator()
        
        # Enhanced component type detection
        self.component_type_indicators = {
            'microservice': [
                'Dockerfile', 'deployment.yaml', 'service.yaml',
                'deploymentconfig.yaml', 'route.yaml'
            ],
            'library': [
                'pom.xml', 'build.gradle', 'setup.py', 'package.json',
                'composer.json', 'Cargo.toml', 'Gemfile'
            ],
            'frontend': [
                'package.json', 'webpack.config.js', 'angular.json',
                'vue.config.js', 'public/index.html'
            ],
            'database': [
                'schema.sql', 'migrations', 'models.py', 'entity',
                'flyway', 'liquibase'
            ],
            'infrastructure': [
                'terraform', 'cloudformation', 'helm', 'kustomize',
                'ansible', 'puppet', 'chef'
            ]
        }
        
        # Runtime detection from various indicators
        self.runtime_indicators = {
            'java': {
                'spring-boot': ['@SpringBootApplication', 'spring-boot-starter'],
                'quarkus': ['quarkus-maven-plugin', '@QuarkusMain'],
                'tomcat': ['web.xml', 'webapps'],
                'jetty': ['jetty-maven-plugin', 'jetty.xml'],
                'wildfly': ['jboss-deployment-structure.xml']
            },
            'nodejs': {
                'express': ['express'],
                'nest': ['@nestjs/core'],
                'next': ['next'],
                'react': ['react', 'react-dom'],
                'vue': ['vue'],
                'angular': ['@angular/core']
            },
            'python': {
                'django': ['django', 'manage.py'],
                'flask': ['flask', 'app.py'],
                'fastapi': ['fastapi', 'uvicorn'],
                'tornado': ['tornado'],
                'pyramid': ['pyramid']
            }
        }
        
        # Build tool detection
        self.build_tool_indicators = {
            'maven': ['pom.xml', 'mvnw', '.mvn'],
            'gradle': ['build.gradle', 'gradlew', 'gradle.properties'],
            'npm': ['package.json', 'package-lock.json'],
            'yarn': ['yarn.lock'],
            'pip': ['requirements.txt', 'setup.py'],
            'poetry': ['pyproject.toml', 'poetry.lock'],
            'cargo': ['Cargo.toml', 'Cargo.lock'],
            'composer': ['composer.json', 'composer.lock'],
            'bundler': ['Gemfile', 'Gemfile.lock']
        }
    
    def discover_components(self, repo_path: str) -> Dict[str, EnhancedComponentInfo]:
        """Discover all components using cross-artifact correlation"""
        print(f"DISCOVERY [ENHANCED-DISCOVERY] Starting enhanced component discovery for {repo_path}")
        
        # Step 1: Gather all artifacts
        deployment_configs = self._collect_deployment_configs(repo_path)
        build_configs = self._collect_build_configs(repo_path)
        docker_files = self._collect_docker_files(repo_path)
        
        print(f"DISCOVERY [ENHANCED-DISCOVERY] Found {len(deployment_configs)} deployment configs")
        print(f"DISCOVERY [ENHANCED-DISCOVERY] Found {len(build_configs)} build configs")
        print(f"DISCOVERY [ENHANCED-DISCOVERY] Found {len(docker_files)} Docker files")
        
        # Step 2: Use cross-artifact correlation
        evidence_map = self.correlator.correlate_components(
            repo_path, deployment_configs, build_configs, docker_files
        )
        
        # Step 3: Convert evidence to enhanced component info
        components = {}
        for component_name, evidence in evidence_map.items():
            component = self._create_enhanced_component(evidence, repo_path)
            components[component_name] = component
        
        # Step 4: Analyze relationships and additional metadata
        self._analyze_component_relationships(components, repo_path)
        
        print(f"COMPLETE [ENHANCED-DISCOVERY] Discovery complete. Found {len(components)} components")
        return components
    
    def _collect_deployment_configs(self, repo_path: str) -> Dict[str, Any]:
        """Collect all deployment configurations"""
        deployment_configs = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check if it's a deployment config
                        if self._is_deployment_config(content):
                            relative_path = os.path.relpath(file_path, repo_path)
                            
                            # Parse YAML
                            import yaml
                            try:
                                yaml_data = yaml.safe_load(content)
                                if yaml_data:
                                    deployment_configs[relative_path] = yaml_data
                            except yaml.YAMLError:
                                pass
                                
                    except Exception as e:
                        print(f"WARNING [ENHANCED-DISCOVERY] Error reading {file_path}: {e}")
        
        return deployment_configs
    
    def _collect_build_configs(self, repo_path: str) -> Dict[str, Any]:
        """Collect all build configurations"""
        build_configs = {}
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check if it's a build config
                        if self._is_build_config(content):
                            relative_path = os.path.relpath(file_path, repo_path)
                            
                            # Parse YAML
                            import yaml
                            try:
                                yaml_data = yaml.safe_load(content)
                                if yaml_data:
                                    build_configs[relative_path] = yaml_data
                            except yaml.YAMLError:
                                pass
                                
                    except Exception as e:
                        print(f"WARNING [ENHANCED-DISCOVERY] Error reading {file_path}: {e}")
        
        return build_configs
    
    def _collect_docker_files(self, repo_path: str) -> Dict[str, str]:
        """Collect all Docker files"""
        docker_files = {}
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.lower() in ['dockerfile', 'dockerfile.prod', 'dockerfile.dev']:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        relative_path = os.path.relpath(file_path, repo_path)
                        docker_files[relative_path] = content
                        
                    except Exception as e:
                        print(f"WARNING [ENHANCED-DISCOVERY] Error reading {file_path}: {e}")
        
        return docker_files
    
    def _is_deployment_config(self, content: str) -> bool:
        """Check if YAML content is a deployment configuration"""
        deployment_indicators = [
            'kind: Deployment',
            'kind: DeploymentConfig',
            'kind: StatefulSet',
            'kind: DaemonSet',
            'kind: Service',
            'kind: Route',
            'kind: Ingress'
        ]
        
        return any(indicator in content for indicator in deployment_indicators)
    
    def _is_build_config(self, content: str) -> bool:
        """Check if YAML content is a build configuration"""
        build_indicators = [
            'kind: BuildConfig',
            'kind: ImageStream',
            'sourceStrategy',
            'dockerStrategy',
            'customStrategy'
        ]
        
        return any(indicator in content for indicator in build_indicators)
    
    def _create_enhanced_component(self, evidence: ArtifactEvidence, repo_path: str) -> EnhancedComponentInfo:
        """Create enhanced component info from correlation evidence"""
        
        # Get the correlated language
        language = self.correlator.get_component_language(evidence)
        
        # Determine component type
        component_type = self._determine_component_type(evidence, repo_path)
        
        # Determine runtime
        runtime = self._determine_runtime(evidence, language)
        
        # Determine build tool
        build_tool = self._determine_build_tool(evidence, language)
        
        # Determine packaging
        packaging = self._determine_packaging(evidence, language)
        
        # Get the primary directory path
        primary_path = self._get_primary_path(evidence, repo_path)
        
        component = EnhancedComponentInfo(
            name=evidence.component_name,
            path=primary_path,
            type=component_type,
            language=language,
            language_confidence=getattr(evidence, 'language_confidence', {}),
            runtime=runtime,
            build_tool=build_tool,
            packaging=packaging,
            exposed_ports=list(evidence.exposed_ports),
            environment_variables=evidence.environment_vars,
            docker_files=evidence.docker_files,
            base_images=list(evidence.base_images),
            s2i_images=list(evidence.s2i_images),
            has_deployment_config=len(evidence.deployment_configs) > 0,
            has_build_config=len(evidence.build_configs) > 0,
            source_files_found=sum(len(files) for files in evidence.source_indicators.values()),
            correlation_evidence=evidence
        )
        
        return component
    
    def _determine_component_type(self, evidence: ArtifactEvidence, repo_path: str) -> str:
        """Determine component type based on evidence"""
        
        # If it has deployment config, it's likely a microservice
        if evidence.deployment_configs:
            return 'microservice'
        
        # If it has Docker files, it's likely a microservice
        if evidence.docker_files:
            return 'microservice'
        
        # Check for type indicators in source files
        for comp_type, indicators in self.component_type_indicators.items():
            for directory in evidence.directories:
                for indicator in indicators:
                    for root, dirs, files in os.walk(directory):
                        if indicator in files:
                            return comp_type
        
        # Default based on language
        if evidence.source_indicators:
            return 'application'
        
        return 'unknown'
    
    def _determine_runtime(self, evidence: ArtifactEvidence, language: str) -> str:
        """Determine runtime based on evidence"""
        
        if language in self.runtime_indicators:
            runtime_patterns = self.runtime_indicators[language]
            
            # Check source files for runtime indicators
            for directory in evidence.directories:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            for runtime_name, patterns in runtime_patterns.items():
                                if any(pattern in content for pattern in patterns):
                                    return runtime_name
                        except Exception:
                            pass
        
        # Check base images for runtime hints
        for base_image in evidence.base_images:
            if 'spring-boot' in base_image:
                return 'spring-boot'
            elif 'node' in base_image:
                return 'nodejs'
            elif 'python' in base_image:
                return 'python'
        
        return language if language != 'unknown' else 'unknown'
    
    def _determine_build_tool(self, evidence: ArtifactEvidence, language: str) -> str:
        """Determine build tool based on evidence"""
        
        for directory in evidence.directories:
            for root, dirs, files in os.walk(directory):
                for build_tool, indicators in self.build_tool_indicators.items():
                    if any(indicator in files for indicator in indicators):
                        return build_tool
        
        return 'unknown'
    
    def _determine_packaging(self, evidence: ArtifactEvidence, language: str) -> str:
        """Determine packaging method based on evidence"""
        
        # If it has Docker files, it's containerized
        if evidence.docker_files:
            return 'docker'
        
        # If it has deployment configs, it's likely containerized
        if evidence.deployment_configs:
            return 'docker'
        
        # Language-specific packaging
        language_packaging = {
            'java': 'jar',
            'nodejs': 'npm',
            'python': 'wheel',
            'go': 'binary',
            'rust': 'binary',
            'dotnet': 'nuget',
            'php': 'composer',
            'ruby': 'gem'
        }
        
        return language_packaging.get(language, 'unknown')
    
    def _get_primary_path(self, evidence: ArtifactEvidence, repo_path: str) -> str:
        """Get the primary path for the component"""
        
        if evidence.directories:
            # Return the first directory, but prefer one that matches the component name
            for directory in evidence.directories:
                if evidence.component_name.lower() in directory.lower():
                    return directory
            return list(evidence.directories)[0]
        
        # Fallback to repo path
        return repo_path
    
    def _analyze_component_relationships(self, components: Dict[str, EnhancedComponentInfo], repo_path: str):
        """Analyze relationships between components"""
        
        # This is a placeholder for relationship analysis
        # Could include dependency analysis, communication patterns, etc.
        for component_name, component in components.items():
            # Add deployment metadata
            if component.has_deployment_config:
                component.deployment_info['platform'] = 'kubernetes/openshift'
            
            # Add business context based on component name and type
            if component.type == 'microservice':
                component.business_context['deployment_pattern'] = 'microservice'
            
            # Set default values for missing fields
            if not component.runtime:
                component.runtime = component.language
            
            if not component.build_tool:
                component.build_tool = 'unknown'