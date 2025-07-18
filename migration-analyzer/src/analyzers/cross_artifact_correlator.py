"""
Cross-artifact correlator that connects deployment manifests to source code
This fixes the critical issue where components show "Language: unknown"
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

@dataclass
class ArtifactEvidence:
    """Evidence collected from various artifacts for a component"""
    component_name: str
    directories: Set[str] = field(default_factory=set)
    deployment_configs: List[Dict[str, Any]] = field(default_factory=list)
    docker_files: List[str] = field(default_factory=list)
    build_configs: List[Dict[str, Any]] = field(default_factory=list)
    source_indicators: Dict[str, List[str]] = field(default_factory=dict)  # language -> [files]
    exposed_ports: Set[int] = field(default_factory=set)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    base_images: Set[str] = field(default_factory=set)
    s2i_images: Set[str] = field(default_factory=set)

class CrossArtifactCorrelator:
    """Correlates deployment manifests with source code to get complete component picture"""
    
    def __init__(self):
        # Language detection patterns
        self.language_indicators = {
            'java': [
                'pom.xml', 'build.gradle', 'gradle.properties', 'settings.gradle',
                'build.xml', 'ivy.xml', '.java'
            ],
            'python': [
                'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',
                'setup.cfg', 'environment.yml', '.py'
            ],
            'nodejs': [
                'package.json', 'package-lock.json', 'yarn.lock', 'npm-shrinkwrap.json',
                'node_modules', '.js', '.ts'
            ],
            'dotnet': [
                '*.csproj', '*.sln', 'project.json', 'packages.config',
                'web.config', 'app.config', '.cs'
            ],
            'go': [
                'go.mod', 'go.sum', 'Gopkg.toml', 'glide.yaml', 'vendor', '.go'
            ],
            'rust': [
                'Cargo.toml', 'Cargo.lock', 'src/main.rs', 'src/lib.rs', '.rs'
            ],
            'ruby': [
                'Gemfile', 'Gemfile.lock', 'config.ru', 'Rakefile', '.rb'
            ],
            'php': [
                'composer.json', 'composer.lock', 'index.php', 'wp-config.php', '.php'
            ]
        }
        
        # Base image to language mapping
        self.base_image_languages = {
            'node': 'nodejs',
            'nodejs': 'nodejs',
            'openjdk': 'java',
            'maven': 'java',
            'gradle': 'java',
            'tomcat': 'java',
            'python': 'python',
            'alpine': 'unknown',  # Need more context
            'ubuntu': 'unknown',
            'centos': 'unknown',
            'dotnet': 'dotnet',
            'golang': 'go',
            'rust': 'rust',
            'ruby': 'ruby',
            'php': 'php'
        }
        
        # S2I image to language mapping
        self.s2i_image_languages = {
            'nodejs': 'nodejs',
            'java': 'java',
            'python': 'python',
            'dotnet': 'dotnet',
            'golang': 'go',
            'ruby': 'ruby',
            'php': 'php'
        }
    
    def correlate_components(self, repo_path: str, 
                           deployment_configs: Dict[str, Any],
                           build_configs: Dict[str, Any],
                           docker_files: Dict[str, str]) -> Dict[str, ArtifactEvidence]:
        """
        Correlate deployment artifacts with source code to get complete component picture
        """
        print(f"CORRELATOR [CORRELATOR] Starting cross-artifact correlation for {repo_path}")
        
        # Collect evidence for each component
        evidence_map = {}
        
        # Step 1: Extract component names from deployment configs
        component_names = self._extract_component_names(deployment_configs, build_configs, docker_files)
        print(f"CORRELATOR [CORRELATOR] Found potential components: {component_names}")
        
        # Step 2: For each component, gather evidence from all artifacts
        for component_name in component_names:
            evidence = ArtifactEvidence(component_name=component_name)
            
            # Gather deployment evidence
            self._gather_deployment_evidence(evidence, deployment_configs, build_configs)
            
            # Gather Docker evidence
            self._gather_docker_evidence(evidence, docker_files)
            
            # Gather source code evidence
            self._gather_source_evidence(evidence, repo_path)
            
            # Correlate and resolve conflicts
            self._correlate_evidence(evidence, repo_path)
            
            evidence_map[component_name] = evidence
        
        print(f"CORRELATOR [CORRELATOR] Correlation complete. Found {len(evidence_map)} components")
        return evidence_map
    
    def _extract_component_names(self, deployment_configs: Dict[str, Any],
                               build_configs: Dict[str, Any],
                               docker_files: Dict[str, str]) -> Set[str]:
        """Extract all potential component names from various artifacts"""
        component_names = set()
        
        # From deployment configs (primary components)
        for config_name, config_data in deployment_configs.items():
            if isinstance(config_data, dict):
                # OpenShift DeploymentConfig
                if 'metadata' in config_data and 'name' in config_data['metadata']:
                    name = config_data['metadata']['name']
                    # Filter out infrastructure components (databases, caches, etc.)
                    if not self._is_infrastructure_component(name):
                        component_names.add(name)
                # Kubernetes Deployment
                elif 'spec' in config_data and 'selector' in config_data['spec']:
                    labels = config_data['spec']['selector'].get('matchLabels', {})
                    if 'app' in labels:
                        name = labels['app']
                        if not self._is_infrastructure_component(name):
                            component_names.add(name)
        
        # From build configs (only if not already covered by deployment configs)
        for config_name, config_data in build_configs.items():
            if isinstance(config_data, dict) and 'metadata' in config_data:
                if 'name' in config_data['metadata']:
                    name = config_data['metadata']['name']
                    # Normalize name by removing deployment strategy suffixes
                    normalized_name = self._normalize_component_name(name)
                    if not self._is_infrastructure_component(normalized_name):
                        component_names.add(normalized_name)
        
        # From Docker files (extract directory names)
        for docker_path in docker_files.keys():
            # Extract component name from path like "vote/Dockerfile" -> "vote"
            parts = docker_path.split('/')
            if len(parts) > 1:
                name = parts[-2]  # Directory containing Dockerfile
                if not self._is_infrastructure_component(name):
                    component_names.add(name)
        
        return component_names
    
    def _is_infrastructure_component(self, name: str) -> bool:
        """Check if a component name represents infrastructure (database, cache, etc.) rather than application logic"""
        infrastructure_indicators = [
            'postgresql', 'postgres', 'redis', 'mysql', 'mongodb', 'mongo',
            'elasticsearch', 'elastic', 'cassandra', 'oracle', 'sqlserver',
            'ephemeral', 'persistent', 'database', 'cache', 'queue'
        ]
        name_lower = name.lower()
        return any(indicator in name_lower for indicator in infrastructure_indicators)
    
    def _normalize_component_name(self, name: str) -> str:
        """Normalize component name by removing deployment strategy suffixes"""
        # Remove common deployment strategy suffixes
        suffixes_to_remove = ['-s2i', '-binary', '-docker', '-git', '-ephemeral', '-persistent']
        normalized = name
        for suffix in suffixes_to_remove:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
                break
        return normalized
    
    def _gather_deployment_evidence(self, evidence: ArtifactEvidence, 
                                  deployment_configs: Dict[str, Any],
                                  build_configs: Dict[str, Any]):
        """Gather evidence from deployment and build configurations"""
        
        # Look for deployment configs matching this component
        for config_name, config_data in deployment_configs.items():
            if isinstance(config_data, dict):
                config_name_lower = config_name.lower()
                component_name_lower = evidence.component_name.lower()
                
                if (component_name_lower in config_name_lower or 
                    (config_data.get('metadata', {}).get('name', '') == evidence.component_name)):
                    
                    evidence.deployment_configs.append(config_data)
                    
                    # Extract ports
                    self._extract_ports_from_config(evidence, config_data)
                    
                    # Extract environment variables
                    self._extract_env_vars_from_config(evidence, config_data)
        
        # Look for build configs
        for config_name, config_data in build_configs.items():
            if isinstance(config_data, dict):
                config_name_lower = config_name.lower()
                component_name_lower = evidence.component_name.lower()
                build_config_name = config_data.get('metadata', {}).get('name', '')
                
                # Check for exact match or match with deployment strategy suffixes
                if (component_name_lower in config_name_lower or 
                    (build_config_name == evidence.component_name) or
                    (self._normalize_component_name(build_config_name) == evidence.component_name)):
                    
                    evidence.build_configs.append(config_data)
                    
                    # Extract S2I images
                    self._extract_s2i_images(evidence, config_data)
    
    def _extract_ports_from_config(self, evidence: ArtifactEvidence, config_data: Dict[str, Any]):
        """Extract exposed ports from deployment config"""
        try:
            spec = config_data.get('spec', {})
            template = spec.get('template', {})
            containers = template.get('spec', {}).get('containers', [])
            
            for container in containers:
                ports = container.get('ports', [])
                for port in ports:
                    if 'containerPort' in port:
                        evidence.exposed_ports.add(port['containerPort'])
        except Exception as e:
            print(f"⚠️  [CORRELATOR] Error extracting ports: {e}")
    
    def _extract_env_vars_from_config(self, evidence: ArtifactEvidence, config_data: Dict[str, Any]):
        """Extract environment variables from deployment config"""
        try:
            spec = config_data.get('spec', {})
            template = spec.get('template', {})
            containers = template.get('spec', {}).get('containers', [])
            
            for container in containers:
                env_vars = container.get('env', [])
                for env_var in env_vars:
                    if 'name' in env_var and 'value' in env_var:
                        evidence.environment_vars[env_var['name']] = env_var['value']
        except Exception as e:
            print(f"⚠️  [CORRELATOR] Error extracting env vars: {e}")
    
    def _extract_s2i_images(self, evidence: ArtifactEvidence, build_config: Dict[str, Any]):
        """Extract S2I (Source-to-Image) images from build config"""
        try:
            spec = build_config.get('spec', {})
            strategy = spec.get('strategy', {})
            source_strategy = strategy.get('sourceStrategy', {})
            
            if 'from' in source_strategy:
                image_ref = source_strategy['from']
                if 'name' in image_ref:
                    evidence.s2i_images.add(image_ref['name'])
        except Exception as e:
            print(f"⚠️  [CORRELATOR] Error extracting S2I images: {e}")
    
    def _gather_docker_evidence(self, evidence: ArtifactEvidence, docker_files: Dict[str, str]):
        """Gather evidence from Docker files"""
        
        # Look for Docker files related to this component
        for docker_path, docker_content in docker_files.items():
            # Check if this Docker file belongs to this component
            if evidence.component_name.lower() in docker_path.lower():
                evidence.docker_files.append(docker_path)
                
                # Extract base images
                self._extract_base_images(evidence, docker_content)
                
                # Extract exposed ports
                self._extract_docker_ports(evidence, docker_content)
    
    def _extract_base_images(self, evidence: ArtifactEvidence, docker_content: str):
        """Extract base images from Dockerfile"""
        lines = docker_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('FROM '):
                image = line.split()[1]
                evidence.base_images.add(image)
    
    def _extract_docker_ports(self, evidence: ArtifactEvidence, docker_content: str):
        """Extract exposed ports from Dockerfile"""
        lines = docker_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('EXPOSE '):
                ports = line.split()[1:]
                for port in ports:
                    try:
                        evidence.exposed_ports.add(int(port))
                    except ValueError:
                        pass
    
    def _gather_source_evidence(self, evidence: ArtifactEvidence, repo_path: str):
        """Gather evidence from source code"""
        
        # Look for directories that might contain this component
        potential_dirs = []
        
        # Check for exact match
        component_dir = os.path.join(repo_path, evidence.component_name)
        if os.path.exists(component_dir):
            potential_dirs.append(component_dir)
        
        # Check for case-insensitive match
        for item in os.listdir(repo_path):
            item_path = os.path.join(repo_path, item)
            if os.path.isdir(item_path):
                if item.lower() == evidence.component_name.lower():
                    potential_dirs.append(item_path)
        
        # Analyze each potential directory
        for dir_path in potential_dirs:
            evidence.directories.add(dir_path)
            self._analyze_directory_for_language(evidence, dir_path)
    
    def _analyze_directory_for_language(self, evidence: ArtifactEvidence, dir_path: str):
        """Analyze a directory to determine programming language"""
        
        for root, dirs, files in os.walk(dir_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['node_modules', '__pycache__', 'target', 'build']]
            
            for file in files:
                # Check against language indicators
                for language, indicators in self.language_indicators.items():
                    for indicator in indicators:
                        if indicator.startswith('.'):
                            # File extension
                            if file.endswith(indicator):
                                if language not in evidence.source_indicators:
                                    evidence.source_indicators[language] = []
                                evidence.source_indicators[language].append(os.path.join(root, file))
                        else:
                            # Exact filename
                            if file == indicator or file.startswith(indicator):
                                if language not in evidence.source_indicators:
                                    evidence.source_indicators[language] = []
                                evidence.source_indicators[language].append(os.path.join(root, file))
    
    def _correlate_evidence(self, evidence: ArtifactEvidence, repo_path: str):
        """Correlate all evidence to determine final component properties"""
        
        print(f"CORRELATOR [CORRELATOR] Correlating evidence for {evidence.component_name}")
        
        # Determine language with confidence scoring
        language_confidence = self._calculate_language_confidence(evidence)
        
        print(f"CORRELATOR [CORRELATOR] Language confidence for {evidence.component_name}: {language_confidence}")
        
        # Store the results back in evidence for later use
        evidence.language_confidence = language_confidence
    
    def _calculate_language_confidence(self, evidence: ArtifactEvidence) -> Dict[str, float]:
        """Calculate confidence scores for different languages"""
        confidence = {}
        
        # Evidence from source code files (highest weight)
        for language, files in evidence.source_indicators.items():
            confidence[language] = confidence.get(language, 0) + len(files) * 3
        
        # Evidence from base images (medium weight)
        for base_image in evidence.base_images:
            for image_part, lang in self.base_image_languages.items():
                if image_part in base_image.lower() and lang != 'unknown':
                    confidence[lang] = confidence.get(lang, 0) + 2
        
        # Evidence from S2I images (high weight)
        for s2i_image in evidence.s2i_images:
            for s2i_part, lang in self.s2i_image_languages.items():
                if s2i_part in s2i_image.lower():
                    confidence[lang] = confidence.get(lang, 0) + 4
        
        return confidence
    
    def get_component_language(self, evidence: ArtifactEvidence) -> str:
        """Get the most likely language for a component"""
        if hasattr(evidence, 'language_confidence'):
            if evidence.language_confidence:
                return max(evidence.language_confidence.items(), key=lambda x: x[1])[0]
        return 'unknown'
    
    def get_component_summary(self, evidence: ArtifactEvidence) -> Dict[str, Any]:
        """Get a summary of component evidence"""
        return {
            'name': evidence.component_name,
            'language': self.get_component_language(evidence),
            'language_confidence': getattr(evidence, 'language_confidence', {}),
            'directories': list(evidence.directories),
            'docker_files': evidence.docker_files,
            'base_images': list(evidence.base_images),
            's2i_images': list(evidence.s2i_images),
            'exposed_ports': list(evidence.exposed_ports),
            'environment_vars': evidence.environment_vars,
            'has_deployment_config': len(evidence.deployment_configs) > 0,
            'has_build_config': len(evidence.build_configs) > 0,
            'source_files_found': sum(len(files) for files in evidence.source_indicators.values())
        }