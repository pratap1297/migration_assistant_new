"""
Docker Compose parser for extracting service dependencies and configurations
"""
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.parsers.base import AbstractParser, ParseResult

class DockerComposeParser(AbstractParser):
    """Parser for docker-compose.yml files"""
    
    def get_parser_type(self) -> str:
        return "docker-compose"
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if file is a docker-compose file"""
        name = file_path.name.lower()
        return name in ['docker-compose.yml', 'docker-compose.yaml'] or \
               (name.startswith('docker-compose') and name.endswith(('.yml', '.yaml')))
    
    def parse(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """Parse docker-compose file and extract service relationships"""
        result = ParseResult(
            parser_type=self.get_parser_type(),
            file_path=str(file_path)
        )
        
        try:
            if content is None:
                content = self.read_file(file_path)
            
            compose_data = yaml.safe_load(content)
            
            data = {
                'version': compose_data.get('version', 'unknown'),
                'services': {},
                'networks': {},
                'volumes': {},
                'service_dependencies': {},
                'external_dependencies': []
            }
            
            # Extract services
            services = compose_data.get('services', {})
            for service_name, service_config in services.items():
                service_info = {
                    'image': service_config.get('image'),
                    'build': service_config.get('build'),
                    'ports': [],
                    'environment': {},
                    'volumes': [],
                    'depends_on': [],
                    'networks': [],
                    'command': service_config.get('command'),
                    'healthcheck': service_config.get('healthcheck'),
                    'restart': service_config.get('restart', 'no'),
                    'labels': service_config.get('labels', {})
                }
                
                # Parse ports
                if 'ports' in service_config:
                    for port in service_config['ports']:
                        if isinstance(port, str):
                            # Format: "host:container" or "container"
                            parts = str(port).split(':')
                            if len(parts) == 2:
                                service_info['ports'].append({
                                    'host': parts[0],
                                    'container': parts[1].split('/')[0]
                                })
                            else:
                                service_info['ports'].append({
                                    'container': parts[0].split('/')[0]
                                })
                        elif isinstance(port, dict):
                            service_info['ports'].append(port)
                
                # Parse environment variables
                env = service_config.get('environment', {})
                if isinstance(env, list):
                    # List format: ["KEY=VALUE"]
                    for item in env:
                        if '=' in item:
                            key, value = item.split('=', 1)
                            service_info['environment'][key] = value
                elif isinstance(env, dict):
                    service_info['environment'] = env
                
                # Parse volumes
                if 'volumes' in service_config:
                    for volume in service_config['volumes']:
                        if isinstance(volume, str):
                            service_info['volumes'].append(volume)
                        elif isinstance(volume, dict):
                            service_info['volumes'].append(volume)
                
                # Dependencies
                if 'depends_on' in service_config:
                    deps = service_config['depends_on']
                    if isinstance(deps, list):
                        service_info['depends_on'] = deps
                    elif isinstance(deps, dict):
                        # New format with conditions
                        service_info['depends_on'] = list(deps.keys())
                
                # Networks
                if 'networks' in service_config:
                    nets = service_config['networks']
                    if isinstance(nets, list):
                        service_info['networks'] = nets
                    elif isinstance(nets, dict):
                        service_info['networks'] = list(nets.keys())
                
                data['services'][service_name] = service_info
                
                # Build service dependency graph
                data['service_dependencies'][service_name] = service_info['depends_on']
                
                # Detect external dependencies from environment variables
                self._detect_external_dependencies(service_name, service_info, data)
            
            # Extract networks
            if 'networks' in compose_data:
                data['networks'] = compose_data['networks']
            
            # Extract volumes
            if 'volumes' in compose_data:
                data['volumes'] = compose_data['volumes']
            
            # Add analysis insights
            data['analysis'] = {
                'service_count': len(data['services']),
                'has_dependencies': any(deps for deps in data['service_dependencies'].values()),
                'uses_custom_networks': len(data['networks']) > 0,
                'uses_volumes': len(data['volumes']) > 0,
                'external_service_count': len(data['external_dependencies'])
            }
            
            result.data = data
            
        except yaml.YAMLError as e:
            result.success = False
            result.errors.append(f"Invalid YAML format: {str(e)}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to parse docker-compose: {str(e)}")
        
        return result
    
    def _detect_external_dependencies(self, service_name: str, service_info: Dict[str, Any], data: Dict[str, Any]):
        """Detect external service dependencies from environment variables"""
        env_vars = service_info.get('environment', {})
        
        # Common patterns for external services
        patterns = {
            'database': [
                r'(.*)_(HOST|URL|URI|DSN|CONNECTION)',
                r'(DB|DATABASE|POSTGRES|MYSQL|MONGO|REDIS)_(.*)' 
            ],
            'messaging': [
                r'(KAFKA|RABBITMQ|AMQP|SQS|PUBSUB)_(.*)',
                r'(.*)_QUEUE_(.*)'
            ],
            'api': [
                r'(.*)_API_(URL|KEY|ENDPOINT)',
                r'(.*)_SERVICE_URL'
            ]
        }
        
        for key, value in env_vars.items():
            if not isinstance(value, str):
                continue
                
            # Check for URLs
            if any(proto in str(value) for proto in ['http://', 'https://', 'tcp://', 'amqp://']):
                # Skip internal service references
                if not any(svc in str(value) for svc in data['services'].keys()):
                    data['external_dependencies'].append({
                        'service': service_name,
                        'type': 'url',
                        'name': key,
                        'value': value
                    })
            
            # Check patterns
            for dep_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.match(pattern, key, re.IGNORECASE):
                        # Avoid duplicates
                        if not any(d['name'] == key for d in data['external_dependencies']):
                            data['external_dependencies'].append({
                                'service': service_name,
                                'type': dep_type,
                                'name': key,
                                'value': value if not self._is_sensitive(key) else '<redacted>'
                            })
    
    def _is_sensitive(self, key: str) -> bool:
        """Check if environment variable name suggests sensitive data"""
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)