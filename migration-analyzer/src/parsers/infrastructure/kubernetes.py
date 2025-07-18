"""
Kubernetes manifest parser for extracting deployment and service configurations
"""
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from src.parsers.base import AbstractParser, ParseResult

class KubernetesParser(AbstractParser):
    """Parser for Kubernetes YAML manifests"""
    
    def get_parser_type(self) -> str:
        return "kubernetes"
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if file is a Kubernetes manifest"""
        if not file_path.suffix in ['.yaml', '.yml']:
            return False
        
        # Check common k8s file patterns
        name_lower = file_path.name.lower()
        k8s_patterns = ['deployment', 'service', 'pod', 'configmap', 'secret',
                       'ingress', 'statefulset', 'daemonset', 'k8s', 'kube']
        
        if any(pattern in name_lower for pattern in k8s_patterns):
            return True
        
        # Check if in k8s-related directory
        path_str = str(file_path).lower()
        if any(dir in path_str for dir in ['/k8s/', '/kubernetes/', '/manifests/', '/helm/']):
            return True
        
        # Try to peek at content for kind field
        try:
            content = file_path.read_text()
            return 'kind:' in content and 'apiVersion:' in content
        except:
            return False
    
    def parse(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """Parse Kubernetes manifest and extract configuration"""
        result = ParseResult(
            parser_type=self.get_parser_type(),
            file_path=str(file_path)
        )
        
        try:
            if content is None:
                content = self.read_file(file_path)
            
            # Handle multiple documents in one file
            documents = list(yaml.safe_load_all(content))
            
            data = {
                'resources': [],
                'services': {},
                'deployments': {},
                'configmaps': {},
                'secrets': [],
                'ingresses': {},
                'persistent_volumes': {},
                'service_dependencies': {},
                'external_endpoints': []
            }
            
            for doc in documents:
                if not doc or not isinstance(doc, dict):
                    continue
                
                kind = doc.get('kind', '').lower()
                metadata = doc.get('metadata', {})
                name = metadata.get('name', 'unnamed')
                
                resource_info = {
                    'kind': doc.get('kind'),
                    'apiVersion': doc.get('apiVersion'),
                    'name': name,
                    'namespace': metadata.get('namespace', 'default'),
                    'labels': metadata.get('labels', {}),
                    'annotations': metadata.get('annotations', {})
                }
                
                # Process based on resource type
                if kind == 'deployment':
                    self._parse_deployment(name, doc, data, resource_info)
                elif kind == 'service':
                    self._parse_service(name, doc, data, resource_info)
                elif kind == 'configmap':
                    self._parse_configmap(name, doc, data, resource_info)
                elif kind == 'secret':
                    self._parse_secret(name, doc, data, resource_info)
                elif kind == 'ingress':
                    self._parse_ingress(name, doc, data, resource_info)
                elif kind in ['persistentvolume', 'persistentvolumeclaim']:
                    self._parse_volume(name, doc, data, resource_info)
                
                data['resources'].append(resource_info)
            
            # Analyze service mesh and dependencies
            self._analyze_dependencies(data)
            
            # Add analysis insights
            data['analysis'] = {
                'resource_count': len(data['resources']),
                'service_count': len(data['services']),
                'deployment_count': len(data['deployments']),
                'uses_configmaps': len(data['configmaps']) > 0,
                'uses_secrets': len(data['secrets']) > 0,
                'has_ingress': len(data['ingresses']) > 0,
                'has_persistent_storage': len(data['persistent_volumes']) > 0
            }
            
            result.data = data
            
        except yaml.YAMLError as e:
            result.success = False
            result.errors.append(f"Invalid YAML format: {str(e)}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to parse Kubernetes manifest: {str(e)}")
        
        return result
    
    def _parse_deployment(self, name: str, doc: Dict[str, Any], data: Dict[str, Any], resource_info: Dict[str, Any]):
        """Parse Deployment resource"""
        spec = doc.get('spec', {})
        template = spec.get('template', {})
        pod_spec = template.get('spec', {})
        
        deployment_info = {
            'replicas': spec.get('replicas', 1),
            'strategy': spec.get('strategy', {}).get('type', 'RollingUpdate'),
            'containers': [],
            'volumes': [],
            'service_account': pod_spec.get('serviceAccountName'),
            'node_selector': pod_spec.get('nodeSelector', {}),
            'tolerations': pod_spec.get('tolerations', [])
        }
        
        # Parse containers
        for container in pod_spec.get('containers', []):
            container_info = {
                'name': container.get('name'),
                'image': container.get('image'),
                'ports': [],
                'env': {},
                'env_from': [],
                'volume_mounts': container.get('volumeMounts', []),
                'resources': container.get('resources', {}),
                'probes': {}
            }
            
            # Ports
            for port in container.get('ports', []):
                container_info['ports'].append({
                    'name': port.get('name'),
                    'containerPort': port.get('containerPort'),
                    'protocol': port.get('protocol', 'TCP')
                })
            
            # Environment variables
            for env in container.get('env', []):
                env_name = env.get('name')
                if 'value' in env:
                    container_info['env'][env_name] = env['value']
                elif 'valueFrom' in env:
                    # Reference to ConfigMap or Secret
                    value_from = env['valueFrom']
                    if 'configMapKeyRef' in value_from:
                        ref = value_from['configMapKeyRef']
                        container_info['env'][env_name] = f"configmap:{ref.get('name')}:{ref.get('key')}"
                    elif 'secretKeyRef' in value_from:
                        ref = value_from['secretKeyRef']
                        container_info['env'][env_name] = f"secret:{ref.get('name')}:{ref.get('key')}"
            
            # Environment from ConfigMap/Secret
            for env_from in container.get('envFrom', []):
                if 'configMapRef' in env_from:
                    container_info['env_from'].append({
                        'type': 'configmap',
                        'name': env_from['configMapRef'].get('name')
                    })
                elif 'secretRef' in env_from:
                    container_info['env_from'].append({
                        'type': 'secret',
                        'name': env_from['secretRef'].get('name')
                    })
            
            # Health checks
            if 'livenessProbe' in container:
                container_info['probes']['liveness'] = self._parse_probe(container['livenessProbe'])
            if 'readinessProbe' in container:
                container_info['probes']['readiness'] = self._parse_probe(container['readinessProbe'])
            
            deployment_info['containers'].append(container_info)
        
        # Volumes
        deployment_info['volumes'] = pod_spec.get('volumes', [])
        
        data['deployments'][name] = deployment_info
        resource_info['deployment_details'] = deployment_info
    
    def _parse_service(self, name: str, doc: Dict[str, Any], data: Dict[str, Any], resource_info: Dict[str, Any]):
        """Parse Service resource"""
        spec = doc.get('spec', {})
        
        service_info = {
            'type': spec.get('type', 'ClusterIP'),
            'ports': [],
            'selector': spec.get('selector', {}),
            'cluster_ip': spec.get('clusterIP'),
            'external_name': spec.get('externalName'),
            'load_balancer_ip': spec.get('loadBalancerIP')
        }
        
        # Parse ports
        for port in spec.get('ports', []):
            service_info['ports'].append({
                'name': port.get('name'),
                'port': port.get('port'),
                'targetPort': port.get('targetPort'),
                'protocol': port.get('protocol', 'TCP')
            })
        
        data['services'][name] = service_info
        resource_info['service_details'] = service_info
        
        # Track external services
        if service_info['type'] in ['LoadBalancer', 'NodePort'] or service_info['external_name']:
            data['external_endpoints'].append({
                'name': name,
                'type': service_info['type'],
                'external_name': service_info.get('external_name')
            })
    
    def _parse_configmap(self, name: str, doc: Dict[str, Any], data: Dict[str, Any], resource_info: Dict[str, Any]):
        """Parse ConfigMap resource"""
        configmap_info = {
            'data_keys': list(doc.get('data', {}).keys()),
            'binary_data_keys': list(doc.get('binaryData', {}).keys())
        }
        
        # Detect configuration patterns
        config_data = doc.get('data', {})
        for key, value in config_data.items():
            # Look for database connections, API endpoints, etc.
            if isinstance(value, str):
                if any(pattern in value.lower() for pattern in ['jdbc:', 'mongodb://', 'redis://', 'http://', 'https://']):
                    data['external_endpoints'].append({
                        'source': f'configmap:{name}',
                        'key': key,
                        'type': 'connection_string'
                    })
        
        data['configmaps'][name] = configmap_info
        resource_info['configmap_details'] = configmap_info
    
    def _parse_secret(self, name: str, doc: Dict[str, Any], data: Dict[str, Any], resource_info: Dict[str, Any]):
        """Parse Secret resource (without exposing values)"""
        secret_info = {
            'name': name,
            'type': doc.get('type', 'Opaque'),
            'data_keys': list(doc.get('data', {}).keys())
        }
        
        data['secrets'].append(secret_info)
        resource_info['secret_details'] = secret_info
    
    def _parse_ingress(self, name: str, doc: Dict[str, Any], data: Dict[str, Any], resource_info: Dict[str, Any]):
        """Parse Ingress resource"""
        spec = doc.get('spec', {})
        
        ingress_info = {
            'rules': [],
            'tls': spec.get('tls', []),
            'backend': spec.get('backend'),
            'ingress_class': spec.get('ingressClassName')
        }
        
        # Parse rules
        for rule in spec.get('rules', []):
            rule_info = {
                'host': rule.get('host'),
                'paths': []
            }
            
            http = rule.get('http', {})
            for path in http.get('paths', []):
                path_info = {
                    'path': path.get('path'),
                    'path_type': path.get('pathType', 'Prefix'),
                    'backend': path.get('backend', {})
                }
                rule_info['paths'].append(path_info)
            
            ingress_info['rules'].append(rule_info)
        
        data['ingresses'][name] = ingress_info
        resource_info['ingress_details'] = ingress_info
    
    def _parse_volume(self, name: str, doc: Dict[str, Any], data: Dict[str, Any], resource_info: Dict[str, Any]):
        """Parse PersistentVolume or PersistentVolumeClaim"""
        spec = doc.get('spec', {})
        
        volume_info = {
            'access_modes': spec.get('accessModes', []),
            'capacity': spec.get('capacity', {}),
            'storage_class': spec.get('storageClassName'),
            'volume_mode': spec.get('volumeMode', 'Filesystem')
        }
        
        data['persistent_volumes'][name] = volume_info
        resource_info['volume_details'] = volume_info
    
    def _parse_probe(self, probe: Dict[str, Any]) -> Dict[str, Any]:
        """Parse health check probe configuration"""
        probe_info = {
            'type': None,
            'initial_delay': probe.get('initialDelaySeconds', 0),
            'period': probe.get('periodSeconds', 10),
            'timeout': probe.get('timeoutSeconds', 1),
            'success_threshold': probe.get('successThreshold', 1),
            'failure_threshold': probe.get('failureThreshold', 3)
        }
        
        if 'httpGet' in probe:
            probe_info['type'] = 'http'
            probe_info['http'] = probe['httpGet']
        elif 'tcpSocket' in probe:
            probe_info['type'] = 'tcp'
            probe_info['tcp'] = probe['tcpSocket']
        elif 'exec' in probe:
            probe_info['type'] = 'exec'
            probe_info['exec'] = probe['exec']
        
        return probe_info
    
    def _analyze_dependencies(self, data: Dict[str, Any]):
        """Analyze service dependencies from deployments and services"""
        # Map services to their deployments
        service_to_deployment = {}
        for svc_name, svc_info in data['services'].items():
            selector = svc_info.get('selector', {})
            if selector:
                # Find deployments with matching labels
                for dep_name, dep_info in data['deployments'].items():
                    # Check if deployment pods would match this service selector
                    # This is simplified - real k8s matching is more complex
                    service_to_deployment[svc_name] = dep_name
        
        # Analyze environment variables for service dependencies
        for dep_name, dep_info in data['deployments'].items():
            deps = set()
            
            for container in dep_info.get('containers', []):
                # Check environment variables for service references
                for env_name, env_value in container.get('env', {}).items():
                    if isinstance(env_value, str):
                        # Look for service names in env values
                        for svc_name in data['services'].keys():
                            if svc_name in env_value:
                                deps.add(svc_name)
            
            if deps:
                data['service_dependencies'][dep_name] = list(deps)