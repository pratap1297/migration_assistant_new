import os
import re
import json
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from typing import Dict, List, Set
from pathlib import Path
from src.core.models import SecurityFindings

class SecurityScanner:
    def __init__(self):
        self.auth_patterns = {
            'jwt': ['jwt', 'jsonwebtoken', 'auth0', 'system.identitymodel.tokens.jwt'],
            'oauth': ['oauth', 'oauth2', 'microsoft.aspnetcore.authentication.oauth'],
            'basic': ['basic auth', 'authorization: basic', 'basicauthenticationhandler'],
            'api_key': ['api.key', 'apikey', 'x-api-key'],
            'windows_auth': ['windows authentication', 'ntlm', 'kerberos'],
            'identity': ['asp.net identity', 'microsoft.aspnetcore.identity'],
            'ad': ['active directory', 'microsoft.aspnetcore.authentication.activedirectory'],
        }
        
        self.encryption_patterns = {
            'tls': ['https://', 'tls', 'ssl', 'sslstream'],
            'crypto': ['crypto', 'bcrypt', 'argon2', 'pbkdf2', 'system.security.cryptography'],
            'hashing': ['sha256', 'sha512', 'md5', 'system.security.cryptography.sha256'],
            'data_protection': ['microsoft.aspnetcore.dataprotection', 'dataprotectionprovider'],
            'certificate': ['x509certificate', 'certificatestore'],
        }
        
        self.secret_patterns = [
            (r'(?i)(password|pwd|passwd)\s*=\s*["\']([^"\']+)["\']', 'password'),
            (r'(?i)(api_key|apikey)\s*=\s*["\']([^"\']+)["\']', 'api_key'),
            (r'(?i)(secret|token)\s*=\s*["\']([^"\']+)["\']', 'secret'),
            (r'(?i)(aws_access_key|aws_secret)\s*=\s*["\']([^"\']+)["\']', 'aws_credential'),
            # .NET specific patterns
            (r'(?i)(connectionstring)\s*=\s*["\']([^"\']+)["\']', 'connection_string'),
            (r'(?i)(client_secret|clientsecret)\s*=\s*["\']([^"\']+)["\']', 'client_secret'),
            (r'(?i)(encryption_key|encryptionkey)\s*=\s*["\']([^"\']+)["\']', 'encryption_key'),
            (r'(?i)(jwt_secret|jwtsecret)\s*=\s*["\']([^"\']+)["\']', 'jwt_secret'),
        ]
        
    def scan_repository(self, repo_path: str) -> Dict[str, SecurityFindings]:
        """Scan entire repository for security findings"""
        findings = {}
        
        # Identify components
        components = self._identify_components(repo_path)
        
        for component_name, component_path in components.items():
            findings[component_name] = self._scan_component(component_path, component_name)
            
        return findings
    
    def _scan_component(self, component_path: str, component_name: str) -> SecurityFindings:
        """Scan a single component for security issues"""
        findings = SecurityFindings(component_name=component_name)
        
        # Scan dependencies
        self._scan_dependencies(component_path, findings)
        
        # Scan source files
        for file_path in self._walk_files(component_path):
            self._scan_file(file_path, findings)
            
        # Scan configuration files
        self._scan_config_files(component_path, findings)
        
        return findings
    
    def _scan_dependencies(self, component_path: str, findings: SecurityFindings):
        """Scan dependency files for security-related packages"""
        # Package.json
        package_json_path = os.path.join(component_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), 
                           **data.get('devDependencies', {})}
                    
                    for dep in deps:
                        for auth_type, patterns in self.auth_patterns.items():
                            if any(p in dep.lower() for p in patterns):
                                findings.authentication_mechanisms.append(f"{auth_type} (npm: {dep})")
                                
                        for enc_type, patterns in self.encryption_patterns.items():
                            if any(p in dep.lower() for p in patterns):
                                findings.encryption_usage.append(f"{enc_type} (npm: {dep})")
            except:
                pass
                
        # requirements.txt
        requirements_path = os.path.join(component_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r') as f:
                    content = f.read()
                    
                    for line in content.splitlines():
                        line_lower = line.lower()
                        for auth_type, patterns in self.auth_patterns.items():
                            if any(p in line_lower for p in patterns):
                                findings.authentication_mechanisms.append(f"{auth_type} (pip: {line.split('==')[0]})")
                                
                        for enc_type, patterns in self.encryption_patterns.items():
                            if any(p in line_lower for p in patterns):
                                findings.encryption_usage.append(f"{enc_type} (pip: {line.split('==')[0]})")
            except:
                pass
                
        # pom.xml
        pom_path = os.path.join(component_path, 'pom.xml')
        if os.path.exists(pom_path):
            try:
                with open(pom_path, 'r') as f:
                    content = f.read()
                    
                    # Simple pattern matching for Maven dependencies
                    if 'spring-security' in content:
                        findings.authentication_mechanisms.append('Spring Security (Maven)')
                    if 'jwt' in content.lower():
                        findings.authentication_mechanisms.append('JWT (Maven)')
            except:
                pass
                
        # .NET project files (.csproj, packages.config, etc.)
        self._scan_dotnet_dependencies(component_path, findings)
    
    def _scan_dotnet_dependencies(self, component_path: str, findings: SecurityFindings):
        """Scan .NET project files for security-related packages"""
        import glob
        
        # Check .csproj files
        csproj_files = glob.glob(os.path.join(component_path, '*.csproj'))
        for csproj_file in csproj_files:
            try:
                with open(csproj_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Common .NET security packages
                    security_packages = {
                        'Microsoft.AspNetCore.Authentication.JwtBearer': 'jwt',
                        'Microsoft.AspNetCore.Authentication.OpenIdConnect': 'oauth',
                        'Microsoft.AspNetCore.Authentication.OAuth': 'oauth',
                        'Microsoft.AspNetCore.Identity': 'identity',
                        'Microsoft.AspNetCore.Identity.EntityFrameworkCore': 'identity',
                        'Microsoft.IdentityModel.Tokens': 'jwt',
                        'System.IdentityModel.Tokens.Jwt': 'jwt',
                        'Microsoft.AspNetCore.DataProtection': 'data_protection',
                        'Microsoft.AspNetCore.Authentication.Certificate': 'certificate',
                        'Microsoft.AspNetCore.Authentication.Windows': 'windows_auth',
                        'Microsoft.AspNetCore.Authorization': 'authorization',
                    }
                    
                    for package, auth_type in security_packages.items():
                        if package in content:
                            findings.authentication_mechanisms.append(f"{auth_type} (NuGet: {package})")
                            
                    # Encryption packages
                    crypto_packages = {
                        'System.Security.Cryptography': 'crypto',
                        'Microsoft.AspNetCore.DataProtection': 'data_protection',
                        'Bouncy Castle': 'crypto',
                        'System.Security.Cryptography.Algorithms': 'crypto',
                    }
                    
                    for package, crypto_type in crypto_packages.items():
                        if package in content:
                            findings.encryption_usage.append(f"{crypto_type} (NuGet: {package})")
                            
            except Exception:
                pass
        
        # Check packages.config (legacy .NET Framework)
        packages_config = os.path.join(component_path, 'packages.config')
        if os.path.exists(packages_config):
            try:
                with open(packages_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if 'Microsoft.AspNet.Identity' in content:
                        findings.authentication_mechanisms.append('identity (NuGet: Microsoft.AspNet.Identity)')
                    if 'Microsoft.Owin.Security' in content:
                        findings.authentication_mechanisms.append('oauth (NuGet: Microsoft.Owin.Security)')
                    if 'System.IdentityModel.Tokens.Jwt' in content:
                        findings.authentication_mechanisms.append('jwt (NuGet: System.IdentityModel.Tokens.Jwt)')
                        
            except Exception:
                pass
        
        # Check appsettings.json for configuration
        appsettings_files = ['appsettings.json', 'appsettings.Development.json', 'appsettings.Production.json']
        for settings_file in appsettings_files:
            settings_path = os.path.join(component_path, settings_file)
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for authentication configuration
                        if 'Authentication' in content:
                            findings.authentication_mechanisms.append(f"Configured auth ({settings_file})")
                        if 'JwtBearer' in content:
                            findings.authentication_mechanisms.append(f"jwt (config: {settings_file})")
                        if 'DataProtection' in content:
                            findings.encryption_usage.append(f"data_protection (config: {settings_file})")
                        if 'Https' in content or 'UseHttps' in content:
                            findings.encryption_usage.append(f"tls (config: {settings_file})")
                            
                except Exception:
                    pass
    
    def _scan_file(self, file_path: str, findings: SecurityFindings):
        """Scan individual file for security patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for hardcoded secrets
            for pattern, secret_type in self.secret_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    value = match.group(2) if match.lastindex >= 2 else match.group(1)
                    
                    # Check if it's actually hardcoded (not env var)
                    if not any(env in value for env in ['process.env', 'os.environ', '${', 'ENV[']):
                        findings.hardcoded_secrets.append({
                            'type': secret_type,
                            'file': os.path.relpath(file_path),
                            'line': line_num,
                            'variable': match.group(1) if match.lastindex >= 2 else 'unknown'
                        })
                        
            # Check for insecure protocols
            if 'http://' in content and 'localhost' not in content:
                line_nums = [i+1 for i, line in enumerate(content.splitlines()) 
                           if 'http://' in line and 'localhost' not in line]
                if line_nums:
                    findings.potential_vulnerabilities.append({
                        'type': 'insecure_protocol',
                        'description': 'HTTP used instead of HTTPS',
                        'file': os.path.relpath(file_path),
                        'lines': line_nums[:5]  # First 5 occurrences
                    })
                    
            # Check for auth patterns in code
            for auth_type, patterns in self.auth_patterns.items():
                if any(p in content.lower() for p in patterns):
                    if auth_type not in [a.split(' ')[0] for a in findings.authentication_mechanisms]:
                        findings.authentication_mechanisms.append(f"{auth_type} (code reference)")
                        
        except Exception as e:
            pass
    
    def _scan_config_files(self, component_path: str, findings: SecurityFindings):
        """Scan configuration files for security settings"""
        config_files = ['config.json', 'config.yml', 'config.yaml', 
                       'application.properties', 'application.yml']
        
        for config_file in config_files:
            file_path = os.path.join(component_path, config_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Check for TLS/SSL configuration
                    if any(term in content.lower() for term in ['ssl', 'tls', 'https']):
                        findings.encryption_usage.append(f"TLS/SSL (config: {config_file})")
                        
                    # Check for auth configuration
                    if any(term in content.lower() for term in ['auth', 'jwt', 'oauth']):
                        findings.authentication_mechanisms.append(f"Configured auth ({config_file})")
                        
                except:
                    pass
    
    def _identify_components(self, repo_path: str) -> Dict[str, str]:
        """Identify components in repository (similar to semantic engine)"""
        components = {}
        
        # Check if root is a component
        if self._is_component_directory(repo_path):
            components['root'] = repo_path
            return components
            
        # Look for subdirectories
        for item in os.listdir(repo_path):
            item_path = os.path.join(repo_path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                if self._is_component_directory(item_path):
                    components[item] = item_path
                    
        return components
    
    def _is_component_directory(self, path: str) -> bool:
        """Check if directory is a component"""
        indicators = ['package.json', 'requirements.txt', 'pom.xml', 
                     'build.gradle', 'Dockerfile', 'src']
        return any(os.path.exists(os.path.join(path, ind)) for ind in indicators)
    
    def _walk_files(self, directory: str) -> List[str]:
        """Walk directory and return all files"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['node_modules', '__pycache__', 'target']]
            
            for filename in filenames:
                if not filename.startswith('.'):
                    files.append(os.path.join(root, filename))
                    
        return files