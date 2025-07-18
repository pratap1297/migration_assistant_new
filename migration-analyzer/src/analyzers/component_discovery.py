"""
Enhanced component discovery analyzer for identifying deployable units and their relationships
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

@dataclass
class ComponentInfo:
    """Information about a discovered component"""
    name: str
    path: str
    type: str  # 'microservice', 'library', 'frontend', 'database', 'infrastructure'
    language: str
    runtime: str
    build_tool: str
    packaging: str  # 'docker', 'jar', 'npm', 'wheel', etc.
    dependencies: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    exposed_ports: List[int] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    health_checks: List[str] = field(default_factory=list)
    deployment_info: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)

class ComponentDiscoveryAnalyzer:
    """Analyzer for discovering components and their relationships"""
    
    def __init__(self):
        self.parsers = {
            'dockerfile': DockerfileParser(),
            'docker-compose': DockerComposeParser(),
            'kubernetes': KubernetesParser()
        }
        
        # Component indicators by language/technology
        self.component_indicators = {
            'java': ['pom.xml', 'build.gradle', 'gradle.properties', 'settings.gradle'],
            'nodejs': ['package.json', 'package-lock.json', 'yarn.lock'],
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'dotnet': ['*.csproj', '*.sln', 'project.json', 'packages.config'],
            'go': ['go.mod', 'go.sum', 'Gopkg.toml', 'glide.yaml'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'ruby': ['Gemfile', 'Gemfile.lock', '*.gemspec'],
            'php': ['composer.json', 'composer.lock'],
            'scala': ['build.sbt', 'project/build.properties'],
            'kotlin': ['build.gradle.kts', 'pom.xml']
        }
    
    def discover_components(self, repo_path: str) -> Dict[str, ComponentInfo]:
        """Discover all components in the repository"""
        components = {}
        
        # First pass: identify potential component directories
        potential_components = self._find_potential_components(repo_path)
        
        for comp_path in potential_components:
            comp_name = os.path.basename(comp_path)
            component = self._analyze_component(comp_name, comp_path)
            if component:
                components[comp_name] = component
        
        # Second pass: analyze relationships between components
        self._analyze_component_relationships(components, repo_path)
        
        # Third pass: extract deployment information
        self._extract_deployment_info(components, repo_path)
        
        return components
    
    def _find_potential_components(self, repo_path: str) -> List[str]:
        """Find directories that might contain components"""
        potential_components = []
        
        # Check if root is a component
        if self._is_component_directory(repo_path):
            potential_components.append(repo_path)
            return potential_components
        
        # Walk through subdirectories
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories, common build/dependency directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['node_modules', '__pycache__', 'target', 'build', 'dist', 'out']]
            
            # Check each directory
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if self._is_component_directory(dir_path):
                    potential_components.append(dir_path)
                    # Don't recurse into component directories
                    dirs.remove(dir_name)
        
        return potential_components
    
    def _is_component_directory(self, path: str) -> bool:
        """Check if directory contains a component"""
        files = os.listdir(path)
        
        # Check for component indicators
        for lang, indicators in self.component_indicators.items():
            for indicator in indicators:
                if indicator.startswith('*'):
                    # Glob pattern
                    pattern = indicator[1:]  # Remove *
                    if any(f.endswith(pattern) for f in files):
                        return True
                else:
                    # Exact filename
                    if indicator in files:
                        return True
        
        # Check for containerization indicators
        container_indicators = ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']
        if any(indicator in files for indicator in container_indicators):
            return True
        
        # Check for source code presence
        source_extensions = ['.java', '.js', '.py', '.go', '.rs', '.rb', '.php', '.cs', '.scala', '.kt']
        if any(any(f.endswith(ext) for ext in source_extensions) for f in files):
            return True
        
        return False
    
    def _analyze_component(self, name: str, path: str) -> Optional[ComponentInfo]:
        """Analyze a single component"""
        try:
            component = ComponentInfo(
                name=name,
                path=path,
                type='unknown',
                language='unknown',
                runtime='unknown',
                build_tool='unknown',
                packaging='unknown'
            )
            
            files = os.listdir(path)
            
            # Determine language and build tool
            self._detect_language_and_build_tool(component, files, path)
            
            # Determine component type
            self._determine_component_type(component, files, path)
            
            # Extract dependencies
            self._extract_dependencies(component, files, path)
            
            # Analyze containerization
            self._analyze_containerization(component, files, path)
            
            # Extract environment configuration
            self._extract_environment_config(component, files, path)
            
            return component
            
        except Exception as e:
            print(f"Error analyzing component {name}: {str(e)}")
            return None
    
    def _detect_language_and_build_tool(self, component: ComponentInfo, files: List[str], path: str):
        """Detect language and build tool from files"""
        # Java
        if 'pom.xml' in files:
            component.language = 'java'
            component.build_tool = 'maven'
            component.packaging = 'jar'
            # Check for Spring Boot
            try:
                with open(os.path.join(path, 'pom.xml'), 'r') as f:
                    content = f.read()
                    if 'spring-boot' in content:
                        component.runtime = 'spring-boot'
                        component.type = 'microservice'
            except:
                pass
        elif any(f.endswith('.gradle') for f in files):
            component.language = 'java'
            component.build_tool = 'gradle'
            component.packaging = 'jar'
        
        # Node.js
        elif 'package.json' in files:
            component.language = 'javascript'
            component.build_tool = 'npm'
            component.packaging = 'npm'
            try:
                with open(os.path.join(path, 'package.json'), 'r') as f:
                    package_data = json.load(f)
                    # Check for frameworks
                    deps = {**package_data.get('dependencies', {}), 
                           **package_data.get('devDependencies', {})}
                    if 'express' in deps:
                        component.runtime = 'express'
                        component.type = 'microservice'
                    elif 'react' in deps:
                        component.runtime = 'react'
                        component.type = 'frontend'
                    elif 'vue' in deps:
                        component.runtime = 'vue'
                        component.type = 'frontend'
                    elif 'angular' in deps:
                        component.runtime = 'angular'
                        component.type = 'frontend'
                    elif 'next' in deps:
                        component.runtime = 'nextjs'
                        component.type = 'frontend'
            except:
                pass
        
        # Python
        elif 'requirements.txt' in files or 'setup.py' in files or 'pyproject.toml' in files:
            component.language = 'python'
            component.build_tool = 'pip'
            component.packaging = 'wheel'
            # Check for frameworks
            try:
                if 'requirements.txt' in files:
                    with open(os.path.join(path, 'requirements.txt'), 'r') as f:
                        reqs = f.read().lower()
                        if 'django' in reqs:
                            component.runtime = 'django'
                            component.type = 'microservice'
                        elif 'flask' in reqs:
                            component.runtime = 'flask'
                            component.type = 'microservice'
                        elif 'fastapi' in reqs:
                            component.runtime = 'fastapi'
                            component.type = 'microservice'
            except:
                pass
        
        # Go
        elif 'go.mod' in files:
            component.language = 'go'
            component.build_tool = 'go'
            component.packaging = 'binary'
            component.type = 'microservice'
        
        # .NET
        elif any(f.endswith('.csproj') for f in files):
            component.language = 'csharp'
            component.build_tool = 'dotnet'
            component.packaging = 'dll'
            component.runtime = 'dotnet'
        
        # Rust
        elif 'Cargo.toml' in files:
            component.language = 'rust'
            component.build_tool = 'cargo'
            component.packaging = 'binary'
        
        # Ruby
        elif 'Gemfile' in files:
            component.language = 'ruby'
            component.build_tool = 'bundler'
            component.packaging = 'gem'
            # Check for Rails
            try:
                with open(os.path.join(path, 'Gemfile'), 'r') as f:
                    content = f.read()
                    if 'rails' in content:
                        component.runtime = 'rails'
                        component.type = 'microservice'
            except:
                pass
    
    def _determine_component_type(self, component: ComponentInfo, files: List[str], path: str):
        """Determine component type based on structure and files"""
        if component.type != 'unknown':
            return  # Already determined
        
        # Check for web frontend indicators
        frontend_indicators = ['index.html', 'src/App.js', 'src/App.vue', 'angular.json']
        if any(indicator in files for indicator in frontend_indicators):
            component.type = 'frontend'
            return
        
        # Check for database indicators
        db_indicators = ['docker-compose.yml', 'init.sql', 'migrations/']
        if any(indicator in files for indicator in db_indicators):
            # Check if it's a database service
            if 'docker-compose.yml' in files:
                try:
                    compose_parser = DockerComposeParser()
                    result = compose_parser.parse(Path(os.path.join(path, 'docker-compose.yml')))
                    if result.success:
                        services = result.data.get('services', {})
                        db_services = ['postgres', 'mysql', 'mongodb', 'redis']
                        if any(any(db in service.get('image', '') for db in db_services) 
                               for service in services.values()):
                            component.type = 'database'
                            return
                except:
                    pass
        
        # Check for library indicators
        library_indicators = ['lib/', 'src/lib/', 'include/']
        if any(os.path.exists(os.path.join(path, indicator)) for indicator in library_indicators):
            component.type = 'library'
            return
        
        # Check for test-only components
        test_indicators = ['test/', 'tests/', 'spec/']
        if any(os.path.exists(os.path.join(path, indicator)) for indicator in test_indicators):
            # Check if it's primarily tests
            source_files = []
            test_files = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(('.java', '.js', '.py', '.go', '.rs')):
                        if 'test' in root.lower() or 'spec' in root.lower():
                            test_files.append(file)
                        else:
                            source_files.append(file)
            
            if len(test_files) > len(source_files):
                component.type = 'test'
                return
        
        # Default to microservice if it has server-like characteristics
        if component.runtime in ['spring-boot', 'express', 'django', 'flask', 'fastapi']:
            component.type = 'microservice'
        else:
            component.type = 'application'
    
    def _extract_dependencies(self, component: ComponentInfo, files: List[str], path: str):
        """Extract component dependencies"""
        # Maven dependencies
        if component.build_tool == 'maven':
            try:
                with open(os.path.join(path, 'pom.xml'), 'r') as f:
                    content = f.read()
                    # Simple regex to find dependencies
                    import re
                    deps = re.findall(r'<artifactId>([^<]+)</artifactId>', content)
                    component.dependencies = deps[:10]  # Limit to avoid too many
            except:
                pass
        
        # NPM dependencies
        elif component.build_tool == 'npm':
            try:
                with open(os.path.join(path, 'package.json'), 'r') as f:
                    package_data = json.load(f)
                    deps = list(package_data.get('dependencies', {}).keys())
                    component.dependencies = deps[:10]  # Limit to avoid too many
            except:
                pass
        
        # Python dependencies
        elif component.build_tool == 'pip':
            if 'requirements.txt' in files:
                try:
                    with open(os.path.join(path, 'requirements.txt'), 'r') as f:
                        lines = f.readlines()
                        deps = []
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                dep = line.split('==')[0].split('>=')[0].split('~=')[0]
                                deps.append(dep)
                        component.dependencies = deps[:10]  # Limit to avoid too many
                except:
                    pass
    
    def _analyze_containerization(self, component: ComponentInfo, files: List[str], path: str):
        """Analyze containerization setup"""
        if 'Dockerfile' in files:
            try:
                dockerfile_parser = DockerfileParser()
                result = dockerfile_parser.parse(Path(os.path.join(path, 'Dockerfile')))
                if result.success:
                    data = result.data
                    component.packaging = 'docker'
                    component.exposed_ports = data.get('exposed_ports', [])
                    component.environment_variables = data.get('environment_variables', {})
                    component.volumes = data.get('volumes', [])
                    
                    # Extract runtime from base image
                    base_images = data.get('base_images', [])
                    if base_images:
                        base_image = base_images[0]['image']
                        if 'java' in base_image or 'openjdk' in base_image:
                            component.runtime = 'java'
                        elif 'node' in base_image:
                            component.runtime = 'nodejs'
                        elif 'python' in base_image:
                            component.runtime = 'python'
                        elif 'golang' in base_image:
                            component.runtime = 'go'
                        elif 'nginx' in base_image:
                            component.runtime = 'nginx'
            except:
                pass
    
    def _extract_environment_config(self, component: ComponentInfo, files: List[str], path: str):
        """Extract environment configuration"""
        config_files = ['application.properties', 'application.yml', 'config.yml', '.env']
        
        for config_file in config_files:
            if config_file in files:
                try:
                    with open(os.path.join(path, config_file), 'r') as f:
                        content = f.read()
                        # Extract key patterns
                        import re
                        
                        # Database URLs
                        db_urls = re.findall(r'(?:url|uri|host)[=:]\s*([^\\s\\n]+)', content, re.IGNORECASE)
                        for url in db_urls:
                            if any(db in url for db in ['mysql', 'postgres', 'mongodb', 'redis']):
                                component.external_dependencies.append(url)
                        
                        # API endpoints
                        api_urls = re.findall(r'https?://[^\\s\\n]+', content)
                        component.external_dependencies.extend(api_urls)
                        
                        # Server port
                        port_match = re.search(r'(?:port|server\\.port)[=:]\s*(\\d+)', content)
                        if port_match:
                            port = int(port_match.group(1))
                            if port not in component.exposed_ports:
                                component.exposed_ports.append(port)
                        
                except:
                    pass
    
    def _analyze_component_relationships(self, components: Dict[str, ComponentInfo], repo_path: str):
        """Analyze relationships between components"""
        # Check for docker-compose files that might link services
        compose_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file in ['docker-compose.yml', 'docker-compose.yaml']:
                    compose_files.append(os.path.join(root, file))
        
        for compose_file in compose_files:
            try:
                compose_parser = DockerComposeParser()
                result = compose_parser.parse(Path(compose_file))
                if result.success:
                    services = result.data.get('services', {})
                    dependencies = result.data.get('service_dependencies', {})
                    
                    # Map services to components
                    for service_name, deps in dependencies.items():
                        if service_name in components:
                            for dep in deps:
                                if dep in components:
                                    components[service_name].dependencies.append(dep)
            except:
                pass
    
    def _extract_deployment_info(self, components: Dict[str, ComponentInfo], repo_path: str):
        """Extract deployment information from K8s manifests"""
        k8s_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    k8s_parser = KubernetesParser()
                    if k8s_parser.can_parse(Path(file_path)):
                        k8s_files.append(file_path)
        
        for k8s_file in k8s_files:
            try:
                k8s_parser = KubernetesParser()
                result = k8s_parser.parse(Path(k8s_file))
                if result.success:
                    deployments = result.data.get('deployments', {})
                    services = result.data.get('services', {})
                    
                    # Match deployments to components
                    for dep_name, dep_info in deployments.items():
                        # Try to find matching component
                        matching_component = None
                        for comp_name, component in components.items():
                            if dep_name in comp_name or comp_name in dep_name:
                                matching_component = component
                                break
                        
                        if matching_component:
                            matching_component.deployment_info = {
                                'platform': 'kubernetes',
                                'replicas': dep_info.get('replicas', 1),
                                'strategy': dep_info.get('strategy', 'RollingUpdate'),
                                'resource_limits': dep_info.get('containers', [{}])[0].get('resources', {}),
                                'health_checks': []
                            }
                            
                            # Extract health check info
                            containers = dep_info.get('containers', [])
                            for container in containers:
                                probes = container.get('probes', {})
                                if probes:
                                    matching_component.health_checks.extend(probes.keys())
            except:
                pass