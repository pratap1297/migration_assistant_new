"""
GitHub Actions workflow parser for CI/CD pipeline analysis
"""
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from src.parsers.base import AbstractParser, ParseResult

class GitHubActionsParser(AbstractParser):
    """Parser for GitHub Actions workflow files"""
    
    def get_parser_type(self) -> str:
        return "github-actions"
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if file is a GitHub Actions workflow"""
        # Must be in .github/workflows directory
        parts = file_path.parts
        if len(parts) >= 2:
            if parts[-3:-1] == ('.github', 'workflows') and file_path.suffix in ['.yml', '.yaml']:
                return True
        return False
    
    def parse(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """Parse GitHub Actions workflow and extract CI/CD information"""
        result = ParseResult(
            parser_type=self.get_parser_type(),
            file_path=str(file_path)
        )
        
        try:
            if content is None:
                content = self.read_file(file_path)
            
            workflow = yaml.safe_load(content)
            
            data = {
                'name': workflow.get('name', file_path.stem),
                'triggers': self._parse_triggers(workflow.get('on', {})),
                'jobs': {},
                'environment_variables': workflow.get('env', {}),
                'permissions': workflow.get('permissions', {}),
                'quality_gates': [],
                'deployment_info': [],
                'security_scans': [],
                'artifacts': [],
                'docker_builds': [],
                'external_services': []
            }
            
            # Parse jobs
            jobs = workflow.get('jobs', {})
            for job_name, job_config in jobs.items():
                job_info = self._parse_job(job_name, job_config)
                data['jobs'][job_name] = job_info
                
                # Extract quality gates, deployments, and security scans
                self._extract_pipeline_insights(job_name, job_info, data)
            
            # Add analysis insights
            data['analysis'] = {
                'total_jobs': len(data['jobs']),
                'has_tests': any('test' in job.lower() for job in data['jobs'].keys()),
                'has_security_scanning': len(data['security_scans']) > 0,
                'has_quality_gates': len(data['quality_gates']) > 0,
                'deployment_environments': list(set(d['environment'] for d in data['deployment_info'] if 'environment' in d)),
                'uses_containers': len(data['docker_builds']) > 0,
                'workflow_complexity': self._calculate_complexity(data)
            }
            
            result.data = data
            
        except yaml.YAMLError as e:
            result.success = False
            result.errors.append(f"Invalid YAML format: {str(e)}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to parse GitHub Actions workflow: {str(e)}")
        
        return result
    
    def _parse_triggers(self, on_config: Union[str, List, Dict]) -> Dict[str, Any]:
        """Parse workflow triggers"""
        triggers = {
            'push': False,
            'pull_request': False,
            'schedule': [],
            'workflow_dispatch': False,
            'other': []
        }
        
        if isinstance(on_config, str):
            # Simple trigger
            triggers[on_config] = True
        elif isinstance(on_config, list):
            # List of triggers
            for trigger in on_config:
                if trigger in triggers:
                    triggers[trigger] = True
                else:
                    triggers['other'].append(trigger)
        elif isinstance(on_config, dict):
            # Complex triggers with configuration
            for trigger, config in on_config.items():
                if trigger == 'push':
                    triggers['push'] = {
                        'branches': config.get('branches', []) if isinstance(config, dict) else True,
                        'paths': config.get('paths', []) if isinstance(config, dict) else []
                    }
                elif trigger == 'pull_request':
                    triggers['pull_request'] = {
                        'branches': config.get('branches', []) if isinstance(config, dict) else True
                    }
                elif trigger == 'schedule':
                    if isinstance(config, list):
                        triggers['schedule'] = [item.get('cron', '') for item in config]
                elif trigger == 'workflow_dispatch':
                    triggers['workflow_dispatch'] = True
                else:
                    triggers['other'].append(trigger)
        
        return triggers
    
    def _parse_job(self, job_name: str, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse individual job configuration"""
        job_info = {
            'name': job_config.get('name', job_name),
            'runs_on': job_config.get('runs-on', 'unknown'),
            'needs': job_config.get('needs', []),
            'if': job_config.get('if'),
            'environment': job_config.get('environment'),
            'container': job_config.get('container'),
            'services': job_config.get('services', {}),
            'steps': [],
            'strategy': job_config.get('strategy', {}),
            'timeout_minutes': job_config.get('timeout-minutes', 360),
            'outputs': job_config.get('outputs', {})
        }
        
        # Parse steps
        for step in job_config.get('steps', []):
            step_info = {
                'name': step.get('name', 'Unnamed step'),
                'uses': step.get('uses'),
                'run': step.get('run'),
                'with': step.get('with', {}),
                'env': step.get('env', {}),
                'if': step.get('if'),
                'continue_on_error': step.get('continue-on-error', False)
            }
            
            # Identify step type
            if step_info['uses']:
                step_info['type'] = 'action'
                step_info['action'] = step_info['uses'].split('@')[0]
            elif step_info['run']:
                step_info['type'] = 'script'
                step_info['commands'] = self._extract_commands(step_info['run'])
            else:
                step_info['type'] = 'unknown'
            
            job_info['steps'].append(step_info)
        
        return job_info
    
    def _extract_commands(self, run_script: str) -> List[str]:
        """Extract individual commands from run script"""
        if not run_script:
            return []
        
        # Split by newlines and common separators
        lines = run_script.strip().split('\n')
        commands = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Split by && or ;
                parts = re.split(r'&&|;', line)
                commands.extend([p.strip() for p in parts if p.strip()])
        
        return commands
    
    def _extract_pipeline_insights(self, job_name: str, job_info: Dict[str, Any], data: Dict[str, Any]):
        """Extract quality gates, deployments, and security scans from job"""
        
        for step in job_info['steps']:
            step_name_lower = step['name'].lower()
            
            # Check for testing frameworks
            if any(test in step_name_lower for test in ['test', 'jest', 'pytest', 'unit', 'integration']):
                data['quality_gates'].append({
                    'job': job_name,
                    'step': step['name'],
                    'type': 'testing'
                })
            
            # Check for quality/analysis tools
            quality_tools = {
                'sonarqube': ['sonar', 'sonarqube', 'sonarcloud'],
                'code_coverage': ['coverage', 'codecov', 'coveralls'],
                'linting': ['lint', 'eslint', 'pylint', 'flake8', 'rubocop']
            }
            
            for tool_type, patterns in quality_tools.items():
                if any(pattern in step_name_lower for pattern in patterns):
                    data['quality_gates'].append({
                        'job': job_name,
                        'step': step['name'],
                        'type': tool_type
                    })
            
            # Check for security scanning
            security_tools = {
                'snyk': ['snyk'],
                'trivy': ['trivy'],
                'dependency_check': ['dependency-check', 'owasp'],
                'secrets_scanning': ['gitleaks', 'trufflehog', 'detect-secrets'],
                'sast': ['semgrep', 'codeql', 'fortify', 'checkmarx'],
                'container_scan': ['anchore', 'clair', 'grype']
            }
            
            for tool_type, patterns in security_tools.items():
                if any(pattern in step_name_lower for pattern in patterns):
                    data['security_scans'].append({
                        'job': job_name,
                        'step': step['name'],
                        'type': tool_type,
                        'tool': next((p for p in patterns if p in step_name_lower), tool_type)
                    })
            
            # Check for deployment activities
            if any(deploy in step_name_lower for deploy in ['deploy', 'release', 'publish']):
                deployment_info = {
                    'job': job_name,
                    'step': step['name'],
                    'environment': job_info.get('environment', 'unknown')
                }
                
                # Try to identify deployment target
                if 'kubernetes' in step_name_lower or 'k8s' in step_name_lower:
                    deployment_info['target'] = 'kubernetes'
                elif 'docker' in step_name_lower or 'container' in step_name_lower:
                    deployment_info['target'] = 'container_registry'
                elif 'aws' in step_name_lower:
                    deployment_info['target'] = 'aws'
                elif 'azure' in step_name_lower:
                    deployment_info['target'] = 'azure'
                elif 'gcp' in step_name_lower or 'google' in step_name_lower:
                    deployment_info['target'] = 'gcp'
                
                data['deployment_info'].append(deployment_info)
            
            # Check for Docker operations
            if step['type'] == 'action' and 'docker' in step.get('action', '').lower():
                data['docker_builds'].append({
                    'job': job_name,
                    'step': step['name'],
                    'action': step.get('action')
                })
            elif step['type'] == 'script':
                commands = step.get('commands', [])
                for cmd in commands:
                    if 'docker build' in cmd or 'docker push' in cmd:
                        data['docker_builds'].append({
                            'job': job_name,
                            'step': step['name'],
                            'command': cmd
                        })
            
            # Check for external service usage in environment variables
            env_vars = {**job_info.get('environment', {}), **step.get('env', {})}
            for key, value in env_vars.items():
                if any(svc in key.upper() for svc in ['SONAR', 'SNYK', 'CODECOV', 'SENTRY']):
                    data['external_services'].append({
                        'service': key,
                        'job': job_name
                    })
    
    def _calculate_complexity(self, data: Dict[str, Any]) -> str:
        """Calculate workflow complexity based on various factors"""
        score = 0
        
        # Job count
        job_count = len(data['jobs'])
        if job_count > 5:
            score += 3
        elif job_count > 2:
            score += 2
        else:
            score += 1
        
        # Dependencies between jobs
        has_dependencies = any(job.get('needs') for job in data['jobs'].values())
        if has_dependencies:
            score += 2
        
        # Matrix builds
        has_matrix = any(job.get('strategy', {}).get('matrix') for job in data['jobs'].values())
        if has_matrix:
            score += 2
        
        # External services
        if len(data['external_services']) > 3:
            score += 2
        elif len(data['external_services']) > 0:
            score += 1
        
        # Determine complexity level
        if score >= 7:
            return 'high'
        elif score >= 4:
            return 'medium'
        else:
            return 'low'