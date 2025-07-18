import json
from typing import List, Dict, Optional
from datetime import datetime

from src.core.models import (
    RepositoryAnalysis, HLDContent, MigrationPhase,
    AzureArchitecture, AzureServiceMapping
)
from src.core.utils import RateLimiter
from src.synthesis.insight_synthesizer import InsightSynthesizer

class HLDSynthesizer(InsightSynthesizer):
    """Synthesizes High-Level Design using LLM and analysis data"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        
    @RateLimiter(max_calls=14, period=60)
    def synthesize_hld(self, analysis: RepositoryAnalysis, 
                      service_mappings: List[AzureServiceMapping]) -> HLDContent:
        """Synthesize complete HLD content"""
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(analysis, service_mappings)
        
        # Define scope
        scope = self._define_migration_scope(analysis)
        
        # Create target architecture
        target_architecture = self._design_target_architecture(analysis, service_mappings)
        
        # Generate migration phases
        migration_phases = self._generate_migration_phases(analysis, service_mappings)
        
        # Generate technical decisions
        technical_decisions = self._generate_technical_decisions(analysis)
        
        # Risk mitigation strategies
        risk_mitigation = self._generate_risk_mitigation(analysis)
        
        # Cost analysis
        cost_analysis = self._perform_cost_analysis(service_mappings)
        
        return HLDContent(
            executive_summary=executive_summary,
            scope=scope,
            azure_service_mappings=service_mappings,
            target_architecture=target_architecture,
            migration_phases=migration_phases,
            technical_decisions=technical_decisions,
            risk_mitigation=risk_mitigation,
            cost_analysis=cost_analysis
        )
    
    def _generate_executive_summary(self, analysis: RepositoryAnalysis,
                                  service_mappings: List[AzureServiceMapping]) -> str:
        """Generate executive summary using LLM"""
        
        prompt = f"""
Generate an executive summary for a High-Level Design document for migrating {getattr(analysis, 'repository_url', 'the application')} to Azure.

Current State:
- Architecture: Microservices
- Components: {len(analysis.components)}
- Critical Services: {sum(1 for c in analysis.components if hasattr(c, 'criticality') and c.criticality and c.criticality.score > 0.5)}
- Technologies: {', '.join(set(sm.current_technology for sm in service_mappings))}

Target State:
- Primary compute: {self._get_primary_compute(service_mappings)}
- Data services: {self._get_data_services(service_mappings)}
- Estimated complexity: {self._get_overall_complexity(service_mappings)}

Write a concise executive summary (3-4 paragraphs) that:
1. Summarizes the migration objective
2. Highlights key architectural decisions
3. Outlines expected benefits
4. Mentions timeline and complexity
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback summary
            return self._generate_fallback_executive_summary(analysis, service_mappings)
    
    def _define_migration_scope(self, analysis: RepositoryAnalysis) -> Dict:
        """Define what's in and out of scope"""
        
        scope = {
            'in_scope': {
                'applications': list(analysis.components.keys()),
                'databases': self._extract_databases(analysis),
                'integrations': self._extract_integrations(analysis),
                'infrastructure': [
                    'Container orchestration',
                    'Load balancing',
                    'Networking',
                    'Security controls',
                    'Monitoring'
                ]
            },
            'out_of_scope': [
                'Third-party SaaS migrations',
                'End-user training',
                'Legacy system decommissioning',
                'Data archival beyond 2 years'
            ],
            'assumptions': [
                'Current application architecture is stable',
                'No major feature changes during migration',
                'Azure subscription and landing zone ready',
                'Team has basic Azure knowledge'
            ],
            'constraints': [
                'Migration must be completed within 3 months',
                'Minimal downtime allowed for critical services',
                'Budget constraints as per approved proposal',
                'Compliance requirements must be maintained'
            ]
        }
        
        return scope
    
    def _design_target_architecture(self, analysis: RepositoryAnalysis,
                                  service_mappings: List[AzureServiceMapping]) -> AzureArchitecture:
        """Design the target Azure architecture"""
        
        # Group services by type
        compute_services = {}
        data_services = {}
        
        for mapping in service_mappings:
            if any(svc in mapping.target_azure_service for svc in ['AKS', 'App Service', 'Functions', 'Container']):
                compute_services[mapping.component_name] = mapping.target_azure_service
            else:
                data_services[mapping.component_name] = mapping.target_azure_service
        
        # Design networking
        networking = {
            'vnet': {
                'name': 'app-vnet',
                'address_space': '10.0.0.0/16',
                'subnets': {
                    'aks-subnet': '10.0.1.0/24',
                    'app-subnet': '10.0.2.0/24',
                    'data-subnet': '10.0.3.0/24',
                    'agw-subnet': '10.0.4.0/24'
                }
            },
            'load_balancer': 'Azure Application Gateway',
            'dns': 'Azure DNS',
            'cdn': 'Azure Front Door'
        }
        
        # Design security
        security = {
            'identity': 'Azure Active Directory',
            'secrets': 'Azure Key Vault',
            'certificates': 'Azure Key Vault',
            'waf': 'Azure Application Gateway WAF',
            'network_security': 'Network Security Groups',
            'encryption': {
                'at_rest': 'Azure Storage Encryption',
                'in_transit': 'TLS 1.2+'
            }
        }
        
        # Design monitoring
        monitoring = {
            'apm': 'Azure Application Insights',
            'logs': 'Azure Log Analytics',
            'metrics': 'Azure Monitor',
            'alerts': 'Azure Monitor Alerts',
            'dashboards': 'Azure Dashboard'
        }
        
        # Calculate estimated cost
        total_cost = sum(
            self._parse_cost_range(mapping.estimated_cost_range)[1]
            for mapping in service_mappings
        )
        estimated_monthly_cost = f"${int(total_cost * 0.8)} - ${int(total_cost * 1.2)}"
        
        return AzureArchitecture(
            compute_services=compute_services,
            data_services=data_services,
            networking=networking,
            security=security,
            monitoring=monitoring,
            estimated_monthly_cost=estimated_monthly_cost
        )
    
    def _generate_migration_phases(self, analysis: RepositoryAnalysis,
                                 service_mappings: List[AzureServiceMapping]) -> List[MigrationPhase]:
        """Generate migration phases based on dependencies and complexity"""
        
        phases = []
        
        # Phase 1: Foundation
        phase1 = MigrationPhase(
            phase_number=1,
            phase_name="Foundation and Infrastructure",
            duration="2-3 weeks",
            components=[],
            dependencies=[],
            activities=[
                "Set up Azure subscription and resource groups",
                "Configure networking (VNet, Subnets, NSGs)",
                "Set up Azure Key Vault for secrets",
                "Configure Azure Container Registry",
                "Set up monitoring infrastructure",
                "Create CI/CD pipelines"
            ],
            risks=[
                "Azure subscription limits",
                "Network configuration complexity"
            ],
            success_criteria=[
                "All infrastructure components deployed",
                "Connectivity established",
                "Security baseline configured"
            ]
        )
        phases.append(phase1)
        
        # Phase 2: Data Services
        data_services = [m.component_name for m in service_mappings 
                        if 'Database' in m.target_azure_service or 'Cache' in m.target_azure_service]
        
        if data_services:
            phase2 = MigrationPhase(
                phase_number=2,
                phase_name="Data Services Migration",
                duration="2-3 weeks",
                components=data_services,
                dependencies=["Phase 1"],
                activities=[
                    f"Deploy {', '.join(data_services)}",
                    "Migrate data with minimal downtime",
                    "Set up database replication",
                    "Test data integrity",
                    "Configure backup policies"
                ],
                risks=[
                    "Data migration failures",
                    "Performance degradation",
                    "Connection string updates"
                ],
                success_criteria=[
                    "All data migrated successfully",
                    "Performance benchmarks met",
                    "Zero data loss verified"
                ]
            )
            phases.append(phase2)
        
        # Phase 3: Non-Critical Services
        non_critical = []
        for m in service_mappings:
            if m.component_name not in data_services:
                # Check if component is critical
                component = analysis.components.get(m.component_name)
                is_critical = False
                if component and hasattr(component, 'criticality') and component.criticality:
                    is_critical = component.criticality.score >= 0.5
                
                if not is_critical:
                    non_critical.append(m.component_name)
        
        if non_critical:
            phase3 = MigrationPhase(
                phase_number=3,
                phase_name="Non-Critical Services Migration",
                duration="1-2 weeks",
                components=non_critical,
                dependencies=["Phase 2"] if data_services else ["Phase 1"],
                activities=[
                    f"Containerize and deploy {', '.join(non_critical)}",
                    "Update service configurations",
                    "Test service functionality",
                    "Update DNS entries"
                ],
                risks=["Service compatibility issues"],
                success_criteria=["All non-critical services operational"]
            )
            phases.append(phase3)
        
        # Phase 4: Critical Services
        critical = [
            m.component_name for m in service_mappings
            if m.component_name not in data_services
            and m.component_name not in non_critical
        ]
        
        if critical:
            phase4 = MigrationPhase(
                phase_number=len(phases) + 1,
                phase_name="Critical Services Migration",
                duration="2-3 weeks",
                components=critical,
                dependencies=[f"Phase {len(phases)}"],
                activities=[
                    f"Deploy {', '.join(critical)} with zero-downtime strategy",
                    "Implement canary deployment",
                    "Run parallel operation",
                    "Monitor performance closely",
                    "Gradual traffic shift"
                ],
                risks=[
                    "Service disruption",
                    "Data consistency issues",
                    "Performance impact"
                ],
                success_criteria=[
                    "Zero downtime achieved",
                    "Performance SLAs met",
                    "All critical services operational"
                ]
            )
            phases.append(phase4)
        
        # Phase 5: Cutover and Optimization
        phase5 = MigrationPhase(
            phase_number=len(phases) + 1,
            phase_name="Cutover and Optimization",
            duration="1-2 weeks",
            components=["all"],
            dependencies=[f"Phase {len(phases)}"],
            activities=[
                "Complete traffic cutover",
                "Decommission old infrastructure",
                "Performance optimization",
                "Cost optimization",
                "Documentation updates",
                "Knowledge transfer"
            ],
            risks=["Rollback complexity"],
            success_criteria=[
                "100% traffic on Azure",
                "Old infrastructure decommissioned",
                "Cost targets achieved"
            ]
        )
        phases.append(phase5)
        
        return phases
    
    def _generate_technical_decisions(self, analysis: RepositoryAnalysis) -> Dict[str, str]:
        """Generate key technical decisions"""
        
        decisions = {
            'container_orchestration': 'Azure Kubernetes Service (AKS) for microservices requiring orchestration',
            'simple_services': 'Azure App Service for stateless web applications',
            'data_migration': 'Azure Database Migration Service for minimal downtime',
            'ci_cd': 'Azure DevOps Pipelines with GitOps approach',
            'monitoring': 'Azure Monitor with Application Insights for full observability',
            'security': 'Azure Key Vault for secrets, Managed Identity for authentication',
            'networking': 'Hub-spoke topology with Azure Application Gateway',
            'backup': 'Azure Backup with geo-redundancy for critical data',
            'disaster_recovery': 'Multi-region deployment for critical services'
        }
        
        return decisions
    
    def _generate_risk_mitigation(self, analysis: RepositoryAnalysis) -> Dict[str, str]:
        """Generate risk mitigation strategies"""
        
        risks = {
            'data_loss': 'Implement comprehensive backup strategy before migration, maintain source systems until validation',
            'service_disruption': 'Use blue-green deployment with gradual traffic shifting',
            'performance_degradation': 'Conduct thorough performance testing, implement auto-scaling',
            'security_vulnerabilities': 'Security assessment and remediation before migration',
            'cost_overrun': 'Implement cost monitoring and alerts from day 1',
            'skill_gaps': 'Provide Azure training, engage Azure FastTrack program',
            'integration_failures': 'Comprehensive integration testing in staging environment',
            'compliance_issues': 'Ensure Azure services meet compliance requirements'
        }
        
        return risks
    
    def _perform_cost_analysis(self, service_mappings: List[AzureServiceMapping]) -> Dict:
        """Perform cost analysis"""
        
        # Calculate costs by category
        costs_by_category = {
            'compute': 0,
            'data': 0,
            'networking': 100,  # Base networking cost
            'monitoring': 50,   # Base monitoring cost
            'backup': 30       # Base backup cost
        }
        
        for mapping in service_mappings:
            min_cost, max_cost = self._parse_cost_range(mapping.estimated_cost_range)
            avg_cost = (min_cost + max_cost) / 2
            
            if 'Database' in mapping.target_azure_service or 'Cache' in mapping.target_azure_service:
                costs_by_category['data'] += avg_cost
            else:
                costs_by_category['compute'] += avg_cost
        
        total_monthly = sum(costs_by_category.values())
        
        return {
            'monthly_breakdown': costs_by_category,
            'total_monthly': total_monthly,
            'total_annual': total_monthly * 12,
            'cost_optimization': [
                'Use Reserved Instances for 30-60% savings',
                'Implement auto-scaling to reduce costs during low usage',
                'Use Azure Hybrid Benefit if applicable',
                'Regular cost reviews and right-sizing'
            ],
            'roi_factors': [
                'Reduced operational overhead',
                'Improved scalability',
                'Enhanced security posture',
                'Faster time to market'
            ]
        }
    
    # Helper methods
    def _get_primary_compute(self, mappings: List[AzureServiceMapping]) -> str:
        """Get the primary compute platform"""
        compute_services = [m.target_azure_service for m in mappings 
                          if 'Database' not in m.target_azure_service]
        if 'Azure Kubernetes Service' in compute_services:
            return 'Azure Kubernetes Service (AKS)'
        elif 'Azure App Service' in compute_services:
            return 'Azure App Service'
        return 'Mixed compute services'
    
    def _get_data_services(self, mappings: List[AzureServiceMapping]) -> str:
        """Get the data services being used"""
        data_services = [m.target_azure_service for m in mappings 
                        if 'Database' in m.target_azure_service or 'Cache' in m.target_azure_service]
        return ', '.join(set(data_services)) if data_services else 'None'
    
    def _get_overall_complexity(self, mappings: List[AzureServiceMapping]) -> str:
        """Calculate overall migration complexity"""
        complexities = [m.migration_complexity for m in mappings]
        high_count = complexities.count('High')
        
        if high_count > len(mappings) / 2:
            return 'High'
        elif high_count > 0:
            return 'Medium'
        return 'Low'
    
    def _parse_cost_range(self, cost_range: str) -> tuple:
        """Parse cost range string to min/max values"""
        import re
        numbers = re.findall(r'\d+', cost_range)
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        return 0, 100
    
    def _extract_databases(self, analysis: RepositoryAnalysis) -> List[str]:
        """Extract database names from analysis"""
        databases = []
        
        # Look for database mentions in architecture insights
        for insight in analysis.architecture_insights:
            if 'redis' in insight.lower():
                databases.append('Redis Cache')
            if 'sql' in insight.lower() or 'postgres' in insight.lower():
                databases.append('SQL Database')
            if 'mongo' in insight.lower():
                databases.append('MongoDB')
        
        return list(set(databases))
    
    def _extract_integrations(self, analysis: RepositoryAnalysis) -> List[str]:
        """Extract external integrations"""
        integrations = []
        
        # For now, return common integrations
        return ['HTTP APIs', 'Message Queues', 'External Services']
    
    def _generate_fallback_executive_summary(self, analysis: RepositoryAnalysis,
                                           service_mappings: List[AzureServiceMapping]) -> str:
        """Generate fallback executive summary if LLM fails"""
        return f"""
This High-Level Design document outlines the migration strategy for the application from its current 
infrastructure to Microsoft Azure. The migration encompasses {len(analysis.components)} microservices 
and associated data stores, leveraging Azure's cloud-native services for improved scalability, 
reliability, and operational efficiency.

The proposed architecture utilizes {self._get_primary_compute(service_mappings)} as the primary 
compute platform, complemented by {self._get_data_services(service_mappings)} for data persistence. 
This design maintains the current microservices architecture while introducing cloud-native 
capabilities such as auto-scaling, managed services, and integrated monitoring.

The migration is planned to be executed in 5 phases over approximately 10-12 weeks, with a 
focus on minimal disruption to existing operations. The phased approach allows for risk mitigation, 
thorough testing, and gradual transition of services based on their criticality and dependencies.
"""