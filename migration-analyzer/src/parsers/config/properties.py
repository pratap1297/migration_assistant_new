"""
Properties file parser for application configuration
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.parsers.base import AbstractParser, ParseResult

class PropertiesParser(AbstractParser):
    """Parser for .properties files (Java, Spring Boot, etc.)"""
    
    def get_parser_type(self) -> str:
        return "properties"
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if file is a properties file"""
        return file_path.suffix.lower() == '.properties' or \
               file_path.name in ['config.properties', 'application.properties']
    
    def parse(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """Parse properties file and extract configuration"""
        result = ParseResult(
            parser_type=self.get_parser_type(),
            file_path=str(file_path)
        )
        
        try:
            if content is None:
                content = self.read_file(file_path)
            
            data = {
                'properties': {},
                'profiles': set(),
                'datasources': [],
                'external_services': [],
                'messaging': [],
                'security_config': {},
                'server_config': {},
                'feature_flags': {},
                'secrets_references': []
            }
            
            lines = content.split('\n')
            current_section = None
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#') or line.startswith('!'):
                    continue
                
                # Handle line continuations
                while line.endswith('\\') and line_num < len(lines):
                    line = line[:-1] + lines[line_num].strip()
                    line_num += 1
                
                # Parse key-value pair
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                elif ':' in line and not line.startswith('http'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                else:
                    continue
                
                data['properties'][key] = value
                
                # Analyze the property
                self._analyze_property(key, value, data)
            
            # Convert sets to lists for JSON serialization
            data['profiles'] = list(data['profiles'])
            
            # Add analysis insights
            data['analysis'] = {
                'total_properties': len(data['properties']),
                'has_datasources': len(data['datasources']) > 0,
                'has_external_services': len(data['external_services']) > 0,
                'has_messaging': len(data['messaging']) > 0,
                'has_security_config': len(data['security_config']) > 0,
                'uses_profiles': len(data['profiles']) > 0,
                'secrets_count': len(data['secrets_references'])
            }
            
            result.data = data
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to parse properties file: {str(e)}")
        
        return result
    
    def _analyze_property(self, key: str, value: str, data: Dict[str, Any]):
        """Analyze property key-value pair for insights"""
        key_lower = key.lower()
        
        # Spring profiles
        if 'spring.profiles' in key_lower:
            profiles = value.split(',')
            data['profiles'].update(p.strip() for p in profiles)
        
        # Datasource configuration
        if any(ds in key_lower for ds in ['datasource', 'jdbc', 'database']):
            self._extract_datasource(key, value, data)
        
        # Server configuration
        if any(srv in key_lower for srv in ['server.port', 'server.host', 'server.context']):
            data['server_config'][key] = value
        
        # External services
        if any(svc in key_lower for svc in ['api.url', 'service.url', 'endpoint']):
            if any(proto in value for proto in ['http://', 'https://', 'tcp://']):
                data['external_services'].append({
                    'property': key,
                    'url': value,
                    'type': 'api_endpoint'
                })
        
        # Messaging configuration
        if any(msg in key_lower for msg in ['kafka', 'rabbitmq', 'amqp', 'jms', 'activemq']):
            data['messaging'].append({
                'property': key,
                'value': value if not self._is_sensitive(key) else '<redacted>',
                'type': self._get_messaging_type(key_lower)
            })
        
        # Security configuration
        security_patterns = {
            'authentication': ['auth', 'oauth', 'oidc', 'saml'],
            'encryption': ['encrypt', 'crypto', 'ssl', 'tls'],
            'jwt': ['jwt', 'token'],
            'cors': ['cors']
        }
        
        for sec_type, patterns in security_patterns.items():
            if any(pattern in key_lower for pattern in patterns):
                if sec_type not in data['security_config']:
                    data['security_config'][sec_type] = []
                data['security_config'][sec_type].append({
                    'property': key,
                    'value': value if not self._is_sensitive(key) else '<redacted>'
                })
        
        # Feature flags
        if any(ff in key_lower for ff in ['feature.', 'flag.', 'toggle.', 'enable.']):
            if value.lower() in ['true', 'false', 'on', 'off', 'enabled', 'disabled']:
                data['feature_flags'][key] = value.lower() in ['true', 'on', 'enabled']
        
        # Secrets and sensitive data
        if self._is_sensitive(key) or self._has_secret_reference(value):
            data['secrets_references'].append({
                'property': key,
                'type': 'direct' if self._is_sensitive(key) else 'reference',
                'reference': self._extract_secret_reference(value) if self._has_secret_reference(value) else None
            })
    
    def _extract_datasource(self, key: str, value: str, data: Dict[str, Any]):
        """Extract datasource configuration"""
        key_lower = key.lower()
        
        # Find or create datasource entry
        datasource = None
        
        # Try to identify datasource by name (e.g., spring.datasource.primary.url)
        parts = key.split('.')
        ds_name = 'default'
        if len(parts) > 2 and 'datasource' in parts:
            idx = parts.index('datasource')
            if idx + 1 < len(parts) and parts[idx + 1] not in ['url', 'username', 'password', 'driver']:
                ds_name = parts[idx + 1]
        
        # Find existing datasource or create new one
        datasource = next((ds for ds in data['datasources'] if ds['name'] == ds_name), None)
        if not datasource:
            datasource = {
                'name': ds_name,
                'type': 'unknown',
                'properties': {}
            }
            data['datasources'].append(datasource)
        
        # Extract datasource details
        if 'url' in key_lower:
            datasource['url'] = value
            # Identify database type from URL
            if 'mysql' in value:
                datasource['type'] = 'mysql'
            elif 'postgresql' in value or 'postgres' in value:
                datasource['type'] = 'postgresql'
            elif 'oracle' in value:
                datasource['type'] = 'oracle'
            elif 'mongodb' in value:
                datasource['type'] = 'mongodb'
            elif 'redis' in value:
                datasource['type'] = 'redis'
            elif 'h2' in value:
                datasource['type'] = 'h2'
        elif 'username' in key_lower:
            datasource['username'] = value if not self._is_sensitive(key) else '<redacted>'
        elif 'driver' in key_lower:
            datasource['driver'] = value
        else:
            datasource['properties'][key] = value
    
    def _get_messaging_type(self, key_lower: str) -> str:
        """Determine messaging system type from key"""
        if 'kafka' in key_lower:
            return 'kafka'
        elif 'rabbitmq' in key_lower or 'amqp' in key_lower:
            return 'rabbitmq'
        elif 'activemq' in key_lower or 'jms' in key_lower:
            return 'activemq'
        elif 'sqs' in key_lower:
            return 'aws_sqs'
        elif 'pubsub' in key_lower:
            return 'gcp_pubsub'
        else:
            return 'unknown'
    
    def _is_sensitive(self, key: str) -> bool:
        """Check if property key indicates sensitive data"""
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential', 'private']
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)
    
    def _has_secret_reference(self, value: str) -> bool:
        """Check if value contains a secret reference"""
        secret_patterns = [
            r'\${.*}',  # Spring placeholder
            r'{{.*}}',  # Template syntax
            r'vault:.*',  # Vault reference
            r'secret:.*',  # Generic secret reference
            r'ENC\(.*\)',  # Jasypt encrypted value
        ]
        return any(re.search(pattern, value) for pattern in secret_patterns)
    
    def _extract_secret_reference(self, value: str) -> str:
        """Extract the secret reference from value"""
        # Try different patterns
        patterns = [
            (r'\${([^}]+)}', 'placeholder'),
            (r'{{([^}]+)}}', 'template'),
            (r'vault:(.*)', 'vault'),
            (r'secret:(.*)', 'secret'),
            (r'ENC\((.*)\)', 'encrypted')
        ]
        
        for pattern, ref_type in patterns:
            match = re.search(pattern, value)
            if match:
                return f"{ref_type}:{match.group(1)}"
        
        return value