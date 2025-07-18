"""
YAML configuration file parser for application settings
"""
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from src.parsers.base import AbstractParser, ParseResult

class YamlConfigParser(AbstractParser):
    """Parser for YAML configuration files"""
    
    def get_parser_type(self) -> str:
        return "yaml-config"
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if file is a configuration YAML"""
        name = file_path.name.lower()
        
        # Common config file names
        config_names = ['application.yml', 'application.yaml', 'config.yml', 'config.yaml',
                       'settings.yml', 'settings.yaml', 'values.yaml']
        
        if name in config_names:
            return True
        
        # Check for Spring Boot profile configs
        if name.startswith('application-') and file_path.suffix in ['.yml', '.yaml']:
            return True
        
        # Check if in config directory
        if 'config' in str(file_path).lower() and file_path.suffix in ['.yml', '.yaml']:
            return True
        
        return False
    
    def parse(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """Parse YAML configuration file"""
        result = ParseResult(
            parser_type=self.get_parser_type(),
            file_path=str(file_path)
        )
        
        try:
            if content is None:
                content = self.read_file(file_path)
            
            config = yaml.safe_load(content)
            
            data = {
                'raw_config': config,
                'profiles': [],
                'datasources': [],
                'external_services': [],
                'messaging': [],
                'security_config': {},
                'server_config': {},
                'feature_flags': {},
                'secrets_references': [],
                'cloud_config': {}
            }
            
            # Extract profile from filename
            filename = file_path.name
            if filename.startswith('application-'):
                profile = filename.replace('application-', '').replace('.yml', '').replace('.yaml', '')
                data['profiles'].append(profile)
            
            # Parse the configuration
            self._analyze_config(config, data)
            
            # Add analysis insights
            data['analysis'] = {
                'config_depth': self._calculate_depth(config),
                'has_datasources': len(data['datasources']) > 0,
                'has_external_services': len(data['external_services']) > 0,
                'has_messaging': len(data['messaging']) > 0,
                'has_security_config': len(data['security_config']) > 0,
                'uses_profiles': len(data['profiles']) > 0,
                'secrets_count': len(data['secrets_references']),
                'uses_cloud_services': len(data['cloud_config']) > 0
            }
            
            result.data = data
            
        except yaml.YAMLError as e:
            result.success = False
            result.errors.append(f"Invalid YAML format: {str(e)}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to parse YAML config: {str(e)}")
        
        return result
    
    def _analyze_config(self, config: Any, data: Dict[str, Any], path: str = ''):
        """Recursively analyze configuration structure"""
        if not isinstance(config, dict):
            return
        
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            
            # Spring configuration
            if key == 'spring':
                self._analyze_spring_config(value, data)
            
            # Server configuration
            elif key == 'server':
                self._analyze_server_config(value, data)
            
            # Database/datasource configuration
            elif key in ['datasource', 'datasources', 'database']:
                self._analyze_datasources(value, data)
            
            # Cloud provider configuration
            elif key in ['aws', 'azure', 'gcp', 'cloud']:
                self._analyze_cloud_config(key, value, data)
            
            # Security configuration
            elif key in ['security', 'auth', 'oauth2', 'jwt']:
                self._analyze_security_config(key, value, data)
            
            # Messaging configuration
            elif key in ['kafka', 'rabbitmq', 'redis', 'messaging']:
                self._analyze_messaging_config(key, value, data)
            
            # Recursive analysis for nested configs
            elif isinstance(value, dict):
                self._analyze_config(value, data, current_path)
            
            # Check for external services and secrets
            self._check_value_patterns(current_path, value, data)
    
    def _analyze_spring_config(self, spring_config: Dict[str, Any], data: Dict[str, Any]):
        """Analyze Spring Boot specific configuration"""
        if not isinstance(spring_config, dict):
            return
        
        # Profiles
        if 'profiles' in spring_config:
            profiles = spring_config['profiles']
            if isinstance(profiles, dict) and 'active' in profiles:
                active_profiles = profiles['active']
                if isinstance(active_profiles, str):
                    data['profiles'].extend(active_profiles.split(','))
                elif isinstance(active_profiles, list):
                    data['profiles'].extend(active_profiles)
        
        # Datasources
        if 'datasource' in spring_config:
            self._analyze_datasources(spring_config['datasource'], data)
        
        # Cloud configuration
        if 'cloud' in spring_config:
            cloud = spring_config['cloud']
            if isinstance(cloud, dict):
                for provider, config in cloud.items():
                    data['cloud_config'][f"spring-cloud-{provider}"] = config
        
        # Security
        if 'security' in spring_config:
            self._analyze_security_config('spring-security', spring_config['security'], data)
    
    def _analyze_server_config(self, server_config: Dict[str, Any], data: Dict[str, Any]):
        """Analyze server configuration"""
        if not isinstance(server_config, dict):
            return
        
        data['server_config'] = {
            'port': server_config.get('port', 8080),
            'context_path': server_config.get('servlet', {}).get('context-path', '/'),
            'ssl_enabled': 'ssl' in server_config,
            'compression_enabled': server_config.get('compression', {}).get('enabled', False)
        }
        
        if 'ssl' in server_config:
            data['security_config']['ssl'] = {
                'enabled': True,
                'key_store': server_config['ssl'].get('key-store', '')
            }
    
    def _analyze_datasources(self, ds_config: Union[Dict, List], data: Dict[str, Any]):
        """Analyze datasource configuration"""
        if isinstance(ds_config, dict):
            # Single datasource
            datasource = {
                'name': 'default',
                'type': 'unknown',
                'properties': {}
            }
            
            if 'url' in ds_config:
                url = ds_config['url']
                datasource['url'] = url
                datasource['type'] = self._identify_db_type(url)
            
            if 'username' in ds_config:
                datasource['username'] = '<present>'
            
            if 'driver-class-name' in ds_config:
                datasource['driver'] = ds_config['driver-class-name']
            
            # Connection pool settings
            if 'hikari' in ds_config:
                datasource['connection_pool'] = 'hikari'
                datasource['pool_config'] = {
                    'maximum-pool-size': ds_config['hikari'].get('maximum-pool-size', 10),
                    'minimum-idle': ds_config['hikari'].get('minimum-idle', 10)
                }
            
            data['datasources'].append(datasource)
            
        elif isinstance(ds_config, list):
            # Multiple datasources
            for idx, ds in enumerate(ds_config):
                if isinstance(ds, dict):
                    datasource = {
                        'name': ds.get('name', f'datasource-{idx}'),
                        'type': self._identify_db_type(ds.get('url', '')),
                        'url': ds.get('url', '')
                    }
                    data['datasources'].append(datasource)
    
    def _analyze_cloud_config(self, provider: str, config: Dict[str, Any], data: Dict[str, Any]):
        """Analyze cloud provider configuration"""
        if not isinstance(config, dict):
            return
        
        cloud_info = {
            'provider': provider,
            'services': [],
            'region': None
        }
        
        # AWS
        if provider == 'aws':
            if 'region' in config:
                cloud_info['region'] = config['region']
            
            # Check for AWS services
            aws_services = ['s3', 'sqs', 'sns', 'dynamodb', 'rds', 'lambda', 'ecs', 'eks']
            for service in aws_services:
                if service in config:
                    cloud_info['services'].append(service)
        
        # Azure
        elif provider == 'azure':
            if 'storage' in config:
                cloud_info['services'].append('storage')
            if 'service-bus' in config:
                cloud_info['services'].append('service-bus')
            if 'key-vault' in config:
                cloud_info['services'].append('key-vault')
                data['secrets_references'].append({
                    'type': 'azure-key-vault',
                    'config': 'present'
                })
        
        # GCP
        elif provider == 'gcp':
            if 'project-id' in config:
                cloud_info['project_id'] = config['project-id']
            gcp_services = ['storage', 'pubsub', 'firestore', 'spanner']
            for service in gcp_services:
                if service in config:
                    cloud_info['services'].append(service)
        
        data['cloud_config'][provider] = cloud_info
    
    def _analyze_security_config(self, sec_type: str, config: Any, data: Dict[str, Any]):
        """Analyze security configuration"""
        if not isinstance(config, dict):
            return
        
        if sec_type == 'oauth2':
            data['security_config']['oauth2'] = {
                'client': config.get('client', {}),
                'resource_server': 'resource-server' in config
            }
        elif sec_type == 'jwt':
            data['security_config']['jwt'] = {
                'secret_present': 'secret' in config or 'key' in config,
                'expiration': config.get('expiration', 'unknown')
            }
        else:
            data['security_config'][sec_type] = config
    
    def _analyze_messaging_config(self, msg_type: str, config: Any, data: Dict[str, Any]):
        """Analyze messaging configuration"""
        if not isinstance(config, dict):
            return
        
        messaging_info = {
            'type': msg_type,
            'properties': {}
        }
        
        if msg_type == 'kafka':
            messaging_info['properties'] = {
                'bootstrap_servers': config.get('bootstrap-servers', []),
                'consumer_group': config.get('consumer', {}).get('group-id'),
                'topics': self._extract_kafka_topics(config)
            }
        elif msg_type == 'rabbitmq':
            messaging_info['properties'] = {
                'host': config.get('host', 'localhost'),
                'port': config.get('port', 5672),
                'virtual_host': config.get('virtual-host', '/'),
                'queues': config.get('queues', [])
            }
        elif msg_type == 'redis':
            messaging_info['properties'] = {
                'host': config.get('host', 'localhost'),
                'port': config.get('port', 6379),
                'sentinel': 'sentinel' in config,
                'cluster': 'cluster' in config
            }
        
        data['messaging'].append(messaging_info)
    
    def _check_value_patterns(self, path: str, value: Any, data: Dict[str, Any]):
        """Check values for patterns indicating external services or secrets"""
        if isinstance(value, str):
            # Check for URLs
            url_match = re.search(r'(https?://[^\s]+)', value)
            if url_match:
                data['external_services'].append({
                    'path': path,
                    'url': url_match.group(1),
                    'type': 'http_endpoint'
                })
            
            # Check for secret references
            secret_patterns = [
                (r'\${([^}]+)}', 'placeholder'),
                (r'{{([^}]+)}}', 'template'),
                (r'vault:([^\s]+)', 'vault'),
                (r'ENC\(([^)]+)\)', 'encrypted')
            ]
            
            for pattern, ref_type in secret_patterns:
                match = re.search(pattern, value)
                if match:
                    data['secrets_references'].append({
                        'path': path,
                        'type': ref_type,
                        'reference': match.group(1)
                    })
                    break
            
            # Check for feature flags
            if path.count('.') >= 2 and any(ff in path.lower() for ff in ['feature', 'flag', 'toggle', 'enable']):
                if value.lower() in ['true', 'false', 'on', 'off', 'enabled', 'disabled']:
                    data['feature_flags'][path] = value.lower() in ['true', 'on', 'enabled']
        
        elif isinstance(value, list):
            # Check list items
            for idx, item in enumerate(value):
                self._check_value_patterns(f"{path}[{idx}]", item, data)
    
    def _identify_db_type(self, url: str) -> str:
        """Identify database type from connection URL"""
        if not url:
            return 'unknown'
        
        db_patterns = {
            'mysql': ['mysql:', 'mariadb:'],
            'postgresql': ['postgresql:', 'postgres:'],
            'mongodb': ['mongodb:'],
            'redis': ['redis:'],
            'oracle': ['oracle:'],
            'sqlserver': ['sqlserver:', 'mssql:'],
            'h2': ['h2:'],
            'cassandra': ['cassandra:']
        }
        
        for db_type, patterns in db_patterns.items():
            if any(pattern in url.lower() for pattern in patterns):
                return db_type
        
        return 'unknown'
    
    def _extract_kafka_topics(self, config: Dict[str, Any]) -> List[str]:
        """Extract Kafka topics from configuration"""
        topics = []
        
        # Direct topics configuration
        if 'topics' in config:
            if isinstance(config['topics'], list):
                topics.extend(config['topics'])
            elif isinstance(config['topics'], str):
                topics.append(config['topics'])
        
        # Consumer configuration
        consumer = config.get('consumer', {})
        if 'topics' in consumer:
            if isinstance(consumer['topics'], list):
                topics.extend(consumer['topics'])
        
        # Producer configuration
        producer = config.get('producer', {})
        if 'topic' in producer:
            topics.append(producer['topic'])
        
        return list(set(topics))  # Remove duplicates
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of configuration structure"""
        if not isinstance(obj, dict) or current_depth > 10:  # Prevent infinite recursion
            return current_depth
        
        max_depth = current_depth
        for value in obj.values():
            if isinstance(value, dict):
                depth = self._calculate_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth