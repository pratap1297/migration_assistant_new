"""
Dockerfile parser for extracting container infrastructure details
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.parsers.base import AbstractParser, ParseResult

class DockerfileParser(AbstractParser):
    """Parser for Dockerfile analysis"""
    
    def get_parser_type(self) -> str:
        return "dockerfile"
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if file is a Dockerfile"""
        name = file_path.name.lower()
        return name == 'dockerfile' or name.startswith('dockerfile.')
    
    def parse(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """Parse Dockerfile and extract key information"""
        result = ParseResult(
            parser_type=self.get_parser_type(),
            file_path=str(file_path)
        )
        
        try:
            if content is None:
                content = self.read_file(file_path)
            
            data = {
                'base_images': [],
                'exposed_ports': [],
                'environment_variables': {},
                'commands': [],
                'workdir': None,
                'user': None,
                'volumes': [],
                'labels': {},
                'build_stages': [],
                'package_managers': set(),
                'installed_packages': []
            }
            
            lines = content.split('\n')
            current_stage = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Multi-stage build detection
                if line.upper().startswith('FROM '):
                    parts = line.split()
                    base_image = parts[1]
                    stage_name = None
                    
                    if 'AS' in parts:
                        as_index = parts.index('AS')
                        if as_index + 1 < len(parts):
                            stage_name = parts[as_index + 1]
                            current_stage = stage_name
                            data['build_stages'].append(stage_name)
                    
                    data['base_images'].append({
                        'image': base_image,
                        'stage': stage_name
                    })
                    
                    # Detect package manager from base image
                    self._detect_package_manager(base_image, data)
                
                # Port exposure
                elif line.upper().startswith('EXPOSE '):
                    ports = line[7:].split()
                    for port in ports:
                        port_num = port.split('/')[0]  # Remove protocol if present
                        if port_num.isdigit():
                            data['exposed_ports'].append(int(port_num))
                
                # Environment variables
                elif line.upper().startswith('ENV '):
                    env_content = line[4:].strip()
                    # Handle both ENV KEY=VALUE and ENV KEY VALUE formats
                    if '=' in env_content:
                        for pair in env_content.split():
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                data['environment_variables'][key] = value.strip('"\'')
                    else:
                        parts = env_content.split(None, 1)
                        if len(parts) == 2:
                            data['environment_variables'][parts[0]] = parts[1].strip('"\'')
                
                # Working directory
                elif line.upper().startswith('WORKDIR '):
                    data['workdir'] = line[8:].strip()
                
                # User
                elif line.upper().startswith('USER '):
                    data['user'] = line[5:].strip()
                
                # Volumes
                elif line.upper().startswith('VOLUME '):
                    volume = line[7:].strip()
                    # Handle JSON array format
                    if volume.startswith('['):
                        volumes = eval(volume)  # Safe since we control the input
                        data['volumes'].extend(volumes)
                    else:
                        data['volumes'].append(volume)
                
                # Labels (often contain metadata)
                elif line.upper().startswith('LABEL '):
                    label_content = line[6:].strip()
                    # Parse key=value pairs
                    for match in re.finditer(r'(\w+)="([^"]*)"', label_content):
                        data['labels'][match.group(1)] = match.group(2)
                
                # Package installations
                elif any(cmd in line for cmd in ['RUN apt-get install', 'RUN yum install', 
                                                  'RUN apk add', 'RUN pip install',
                                                  'RUN npm install', 'RUN yarn add']):
                    packages = self._extract_packages(line)
                    data['installed_packages'].extend(packages)
                
                # Commands (CMD, ENTRYPOINT)
                elif line.upper().startswith(('CMD ', 'ENTRYPOINT ')):
                    cmd_type = line.split()[0].upper()
                    cmd_content = line[len(cmd_type):].strip()
                    data['commands'].append({
                        'type': cmd_type,
                        'command': cmd_content
                    })
            
            # Convert set to list for JSON serialization
            data['package_managers'] = list(data['package_managers'])
            
            # Add analysis insights
            data['analysis'] = {
                'is_multistage': len(data['build_stages']) > 0,
                'has_non_root_user': data['user'] is not None and data['user'] != 'root',
                'exposes_services': len(data['exposed_ports']) > 0,
                'uses_environment_config': len(data['environment_variables']) > 0
            }
            
            result.data = data
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to parse Dockerfile: {str(e)}")
        
        return result
    
    def _detect_package_manager(self, base_image: str, data: Dict[str, Any]):
        """Detect package manager from base image"""
        image_lower = base_image.lower()
        
        if any(distro in image_lower for distro in ['ubuntu', 'debian']):
            data['package_managers'].add('apt')
        elif any(distro in image_lower for distro in ['centos', 'rhel', 'fedora']):
            data['package_managers'].add('yum')
        elif 'alpine' in image_lower:
            data['package_managers'].add('apk')
        elif 'node' in image_lower:
            data['package_managers'].add('npm')
        elif 'python' in image_lower:
            data['package_managers'].add('pip')
        elif any(lang in image_lower for lang in ['golang', 'go:']):
            data['package_managers'].add('go')
        elif any(java in image_lower for java in ['java', 'openjdk', 'maven']):
            data['package_managers'].add('maven')
    
    def _extract_packages(self, line: str) -> List[str]:
        """Extract package names from install commands"""
        packages = []
        
        # Remove the RUN command
        if line.upper().startswith('RUN '):
            line = line[4:]
        
        # Common patterns for different package managers
        patterns = [
            r'apt-get install.*?([a-z0-9\-\+\.]+)',
            r'yum install.*?([a-z0-9\-\+\.]+)',
            r'apk add.*?([a-z0-9\-\+\.]+)',
            r'pip install\s+([a-z0-9\-\+\._]+)',
            r'npm install.*?([a-z0-9\-\+@/]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            packages.extend(matches)
        
        # Filter out flags and common non-package strings
        filtered = []
        exclude = {'-y', '--yes', '--no-cache', '--no-install-recommends', '-g', '--global'}
        for pkg in packages:
            if pkg not in exclude and not pkg.startswith('-'):
                filtered.append(pkg)
        
        return filtered