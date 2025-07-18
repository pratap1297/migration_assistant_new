import json
from typing import List, Dict, Optional
from dataclasses import asdict

from src.core.models import (
    ComponentInfo, AzureServiceMapping, ServiceCriticality,
    RepositoryAnalysis
)

class AzureServiceMapper:
    """Maps application components to appropriate Azure services"""
    
    def __init__(self):
        # Define Azure service catalog with characteristics
        self.azure_catalog = {
            'compute': {
                'aks': {
                    'name': 'Azure Kubernetes Service',
                    'best_for': ['microservices', 'containerized', 'complex_orchestration'],
                    'tiers': ['Basic', 'Standard'],
                    'base_cost': 150  # per node/month
                },
                'app_service': {
                    'name': 'Azure App Service',
                    'best_for': ['web_apps', 'apis', 'simple_services'],
                    'tiers': ['F1 (Free)', 'B1 (Basic)', 'S1 (Standard)', 'P1v3 (Premium)'],
                    'base_cost': 55  # B1 tier
                },
                'container_instances': {
                    'name': 'Azure Container Instances',
                    'best_for': ['simple_containers', 'batch_jobs', 'low_complexity'],
                    'tiers': ['Pay-per-use'],
                    'base_cost': 30  # 1 vCPU, 1.5GB
                },
                'functions': {
                    'name': 'Azure Functions',
                    'best_for': ['event_driven', 'serverless', 'microservices'],
                    'tiers': ['Consumption', 'Premium'],
                    'base_cost': 0  # Consumption plan
                }
            },
            'data': {
                'postgresql': {
                    'name': 'Azure Database for PostgreSQL',
                    'best_for': ['postgresql', 'relational'],
                    'tiers': ['Basic', 'General Purpose', 'Memory Optimized'],
                    'base_cost': 35  # Basic tier
                },
                'mysql': {
                    'name': 'Azure Database for MySQL',
                    'best_for': ['mysql', 'relational'],
                    'tiers': ['Basic', 'General Purpose', 'Memory Optimized'],
                    'base_cost': 35
                },
                'cosmos': {
                    'name': 'Azure Cosmos DB',
                    'best_for': ['mongodb', 'nosql', 'global_distribution'],
                    'tiers': ['Serverless', 'Provisioned'],
                    'base_cost': 25  # Serverless
                },
                'redis': {
                    'name': 'Azure Cache for Redis',
                    'best_for': ['redis', 'cache', 'session_store'],
                    'tiers': ['Basic', 'Standard', 'Premium'],
                    'base_cost': 50  # C1 Standard
                }
            },
            'messaging': {
                'service_bus': {
                    'name': 'Azure Service Bus',
                    'best_for': ['message_queue', 'pub_sub', 'enterprise_messaging'],
                    'tiers': ['Basic', 'Standard', 'Premium'],
                    'base_cost': 10
                },
                'event_grid': {
                    'name': 'Azure Event Grid',
                    'best_for': ['event_driven', 'reactive', 'serverless'],
                    'tiers': ['Pay-per-event'],
                    'base_cost': 0
                }
            }
        }
    
    def map_component_to_azure(self, component: ComponentInfo, 
                              analysis: RepositoryAnalysis) -> AzureServiceMapping:
        """Map a single component to appropriate Azure service"""
        
        # Analyze component characteristics
        characteristics = self._analyze_component_characteristics(component)
        
        # Determine best Azure service
        azure_service = self._determine_best_azure_service(component, characteristics)
        
        # Determine tier based on criticality
        tier = self._determine_service_tier(component.criticality, azure_service)
        
        # Calculate complexity
        complexity = self._calculate_migration_complexity(component)
        
        # Estimate cost
        cost_range = self._estimate_cost_range(azure_service, tier, component)
        
        # Build justification
        justification = self._build_justification(component, characteristics, azure_service)
        
        return AzureServiceMapping(
            component_name=component.name,
            current_technology=self._get_component_technology(component),
            target_azure_service=azure_service['name'],
            azure_service_tier=tier,
            justification=justification,
            migration_complexity=complexity,
            estimated_cost_range=cost_range
        )
    
    def _analyze_component_characteristics(self, component: ComponentInfo) -> Dict[str, bool]:
        """Analyze component to determine its characteristics"""
        chars = {
            'is_containerized': False,
            'is_web_app': False,
            'is_api': False,
            'is_worker': False,
            'is_stateful': False,
            'is_event_driven': False,
            'has_complex_dependencies': False,
            'needs_orchestration': False
        }
        
        # Check if containerized (has Dockerfile)
        # In real implementation, would check for Dockerfile in component path
        chars['is_containerized'] = True  # Assume all are containerized for voting app
        
        # Check if web app or API
        if component.api_endpoints_count > 0:
            chars['is_api'] = True
            # Check for UI-related endpoints
            if component.api_endpoints_count > 1 or 'result' in component.name.lower():
                chars['is_web_app'] = True
        
        # Check if worker/background service
        if 'worker' in component.name.lower() or component.api_endpoints_count == 0:
            chars['is_worker'] = True
        
        # Check if stateful
        if hasattr(component, 'criticality') and component.criticality:
            chars['is_stateful'] = component.database_operations_count > 0
        
        # Check dependency complexity
        if hasattr(component, 'dependencies') and len(component.dependencies) > 3:
            chars['has_complex_dependencies'] = True
        
        # Check if needs orchestration (multiple services working together)
        if chars['has_complex_dependencies'] and chars['is_containerized']:
            chars['needs_orchestration'] = True
        
        return chars
    
    def _determine_best_azure_service(self, component: ComponentInfo, 
                                    characteristics: Dict[str, bool]) -> Dict:
        """Determine the best Azure service for the component"""
        
        # Decision tree for service selection
        if characteristics['needs_orchestration']:
            # Complex microservices -> AKS
            return self.azure_catalog['compute']['aks']
        
        elif characteristics['is_web_app'] or (characteristics['is_api'] and not characteristics['is_worker']):
            # Web apps and APIs -> App Service
            return self.azure_catalog['compute']['app_service']
        
        elif characteristics['is_worker'] and characteristics['is_containerized']:
            # Simple workers -> Container Instances
            return self.azure_catalog['compute']['container_instances']
        
        elif characteristics['is_event_driven']:
            # Event-driven -> Functions
            return self.azure_catalog['compute']['functions']
        
        else:
            # Default to App Service
            return self.azure_catalog['compute']['app_service']
    
    def _determine_service_tier(self, criticality: Optional[ServiceCriticality], 
                              azure_service: Dict) -> str:
        """Determine appropriate service tier based on criticality"""
        
        if not criticality:
            return azure_service['tiers'][0]  # Default to lowest tier
        
        # Map criticality to tiers
        if criticality.business_criticality == 'critical' or criticality.score > 0.7:
            # Choose premium/production tier
            if 'Premium' in str(azure_service['tiers']):
                return next(t for t in azure_service['tiers'] if 'Premium' in t)
            elif 'Standard' in str(azure_service['tiers']):
                return next(t for t in azure_service['tiers'] if 'Standard' in t)
            else:
                return azure_service['tiers'][-1]  # Highest tier
        
        elif criticality.business_criticality == 'high' or criticality.score > 0.5:
            # Choose standard tier
            if 'Standard' in str(azure_service['tiers']):
                return next(t for t in azure_service['tiers'] if 'Standard' in t)
            else:
                return azure_service['tiers'][1] if len(azure_service['tiers']) > 1 else azure_service['tiers'][0]
        
        else:
            # Low/Medium - choose basic tier
            if 'Basic' in str(azure_service['tiers']):
                return next(t for t in azure_service['tiers'] if 'Basic' in t)
            else:
                return azure_service['tiers'][0]
    
    def _calculate_migration_complexity(self, component: ComponentInfo) -> str:
        """Calculate migration complexity for a component"""
        complexity_score = 0
        
        # Factor 1: Number of dependencies
        if hasattr(component, 'dependencies'):
            if len(component.dependencies) > 5:
                complexity_score += 3
            elif len(component.dependencies) > 2:
                complexity_score += 2
            else:
                complexity_score += 1
        
        # Factor 2: Database operations
        if component.database_operations_count > 10:
            complexity_score += 2
        elif component.database_operations_count > 5:
            complexity_score += 1
        
        # Factor 3: External integrations
        if component.http_calls_count > 5:
            complexity_score += 2
        elif component.http_calls_count > 0:
            complexity_score += 1
        
        # Factor 4: Code complexity (using LOC as proxy)
        if component.lines_of_code > 1000:
            complexity_score += 2
        elif component.lines_of_code > 500:
            complexity_score += 1
        
        # Determine complexity level
        if complexity_score >= 7:
            return "High"
        elif complexity_score >= 4:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_cost_range(self, azure_service: Dict, tier: str, 
                           component: ComponentInfo) -> str:
        """Estimate monthly cost range for the service"""
        base_cost = azure_service.get('base_cost', 50)
        
        # Adjust for tier
        tier_multipliers = {
            'Free': 0,
            'Basic': 1,
            'Standard': 2,
            'Premium': 4,
            'General Purpose': 3,
            'Memory Optimized': 5
        }
        
        multiplier = 1
        for tier_name, mult in tier_multipliers.items():
            if tier_name in tier:
                multiplier = mult
                break
        
        # Calculate range
        min_cost = int(base_cost * multiplier * 0.8)
        max_cost = int(base_cost * multiplier * 1.5)
        
        if min_cost == 0:
            return "$0 - $20"
        else:
            return f"${min_cost} - ${max_cost}"
    
    def _build_justification(self, component: ComponentInfo, 
                           characteristics: Dict[str, bool], 
                           azure_service: Dict) -> str:
        """Build justification for the service selection"""
        reasons = []
        
        if characteristics['needs_orchestration']:
            reasons.append("Complex microservice requiring orchestration")
        
        if characteristics['is_containerized']:
            reasons.append("Already containerized, enabling cloud-native deployment")
        
        if characteristics['is_web_app']:
            reasons.append("Web application with user-facing interface")
        
        if characteristics['is_api']:
            reasons.append("RESTful API service")
        
        if characteristics['is_worker']:
            reasons.append("Background worker/processor service")
        
        if component.criticality and component.criticality.score > 0.5:
            reasons.append(f"High criticality (score: {component.criticality.score:.2f}) requiring high availability")
        
        return f"{azure_service['name']} selected because: {'; '.join(reasons)}"
    
    def _get_component_technology(self, component: ComponentInfo) -> str:
        """Get the primary technology of a component"""
        return component.language if hasattr(component, 'language') else "Unknown"
    
    def map_data_services(self, analysis: RepositoryAnalysis) -> Dict[str, AzureServiceMapping]:
        """Map databases and caches to Azure services"""
        data_mappings = {}
        
        # Look for Redis in architecture insights
        if any('redis' in insight.lower() for insight in analysis.architecture_insights):
            mapping = AzureServiceMapping(
                component_name="redis",
                current_technology="Redis",
                target_azure_service=self.azure_catalog['data']['redis']['name'],
                azure_service_tier="Standard C1",
                justification="Direct Redis compatibility for caching and message queue",
                migration_complexity="Low",
                estimated_cost_range="$50 - $100"
            )
            data_mappings["redis"] = mapping
        
        # Look for SQL database mentions
        if any('sql' in insight.lower() or 'postgres' in insight.lower() or 'mysql' in insight.lower() 
               for insight in analysis.architecture_insights):
            service = self.azure_catalog['data']['postgresql']
            mapping = AzureServiceMapping(
                component_name="database",
                current_technology="SQL Database",
                target_azure_service=service['name'],
                azure_service_tier="General Purpose",
                justification="SQL database migration with managed service benefits",
                migration_complexity="Medium",
                estimated_cost_range="$100 - $200"
            )
            data_mappings["database"] = mapping
        
        return data_mappings