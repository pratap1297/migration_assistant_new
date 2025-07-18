import os
from datetime import datetime
from typing import Dict, List, Optional

from src.core.models import (
    RepositoryAnalysis, HLDContent, AzureServiceMapping,
    MigrationPhase, AzureArchitecture
)

class HLDDocumentGenerator:
    """Generates the complete HLD document"""
    
    def __init__(self):
        self.toc_items = []
    
    def generate_hld_document(self, analysis: RepositoryAnalysis, 
                            hld_content: HLDContent) -> str:
        """Generate complete HLD document"""
        self.toc_items = []  # Reset TOC
        
        sections = [
            self._generate_header(analysis),
            self._generate_toc(),  # Placeholder
            self._generate_introduction(analysis, hld_content),
            self._generate_scope(hld_content),
            self._generate_current_state_summary(analysis),
            self._generate_target_architecture(hld_content),
            self._generate_service_mapping(hld_content),
            self._generate_migration_strategy(hld_content),
            self._generate_technical_architecture(hld_content),
            self._generate_security_design(hld_content),
            self._generate_networking_design(hld_content),
            self._generate_data_architecture(analysis, hld_content),
            self._generate_monitoring_strategy(hld_content),
            self._generate_migration_phases(hld_content),
            self._generate_risk_assessment(hld_content),
            self._generate_cost_analysis(hld_content),
            self._generate_success_criteria(),
            self._generate_appendices()
        ]
        
        # Build document
        doc_content = "\n\n".join(sections)
        
        # Replace TOC placeholder
        toc = self._build_toc()
        doc_content = doc_content.replace("<!-- TOC_PLACEHOLDER -->", toc)
        
        return doc_content
    
    def _generate_header(self, analysis: RepositoryAnalysis) -> str:
        """Generate document header"""
        repo_name = getattr(analysis, 'repo_name', None)
        if not repo_name and hasattr(analysis, 'repository_url'):
            repo_name = analysis.repository_url.rstrip('/').split('/')[-1]
        if not repo_name:
            repo_name = 'Unknown Repository'
        return f"""# High-Level Design - {repo_name} Azure Migration

**Document Version**: 1.0  
**Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Classification**: Confidential  
**Status**: Draft

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {datetime.now().strftime('%Y-%m-%d')} | Migration Team | Initial version |

---"""

    def _generate_toc(self) -> str:
        """Generate table of contents placeholder"""
        return """## Table of Contents

<!-- TOC_PLACEHOLDER -->"""

    def _generate_introduction(self, analysis: RepositoryAnalysis, 
                             hld_content: HLDContent) -> str:
        """Generate introduction section"""
        self._add_toc_item("1. Introduction", 1)
        
        content = f"""## 1. Introduction

### 1.1 Purpose

{hld_content.executive_summary}

### 1.2 Document Scope

This High-Level Design document provides:
- Target state architecture on Microsoft Azure
- Service mapping from current to target state  
- Migration strategy and phasing
- Technical design decisions
- Risk mitigation approaches
- Cost estimates and optimization strategies

### 1.3 Audience

This document is intended for:
- Technical Architecture Team
- Development Teams
- Infrastructure Teams
- Project Management
- Security and Compliance Teams
- Executive Stakeholders

### 1.4 Related Documents

- AS-IS State Analysis Document
- Azure Well-Architected Framework
- Organization's Cloud Adoption Framework
- Security and Compliance Requirements"""
        
        return content

    def _generate_scope(self, hld_content: HLDContent) -> str:
        """Generate scope section"""
        self._add_toc_item("2. Scope", 1)
        
        scope = hld_content.scope
        
        content = """## 2. Scope

### 2.1 In Scope

#### Applications and Services
"""
        
        for app in scope['in_scope']['applications']:
            content += f"- {app}\n"
        
        content += """
#### Data Stores
"""
        for db in scope['in_scope']['databases']:
            content += f"- {db}\n"
        
        content += """
#### Infrastructure Components
"""
        for infra in scope['in_scope']['infrastructure']:
            content += f"- {infra}\n"
        
        content += """
### 2.2 Out of Scope

The following items are explicitly out of scope for this migration:
"""
        for item in scope['out_of_scope']:
            content += f"- {item}\n"
        
        content += """
### 2.3 Assumptions

"""
        for assumption in scope['assumptions']:
            content += f"- {assumption}\n"
        
        content += """
### 2.4 Constraints

"""
        for constraint in scope['constraints']:
            content += f"- {constraint}\n"
        
        return content

    def _generate_current_state_summary(self, analysis: RepositoryAnalysis) -> str:
        """Generate current state summary"""
        self._add_toc_item("3. Current State Summary", 1)
        
        # Count critical services
        critical_count = sum(1 for c in analysis.components.values() 
                           if c.criticality and c.criticality.business_criticality.lower() == "critical")
        
        content = f"""## 3. Current State Summary

### 3.1 Architecture Overview

The current application follows a **microservices architecture** with the following characteristics:

- **Total Services**: {len(analysis.components)}
- **Critical Services**: {critical_count}
- **Architecture Pattern**: Event-driven microservices
- **Container Platform**: Docker
- **Orchestration**: Kubernetes/OpenShift

### 3.2 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
"""
        
        for comp_name, comp in analysis.components.items():
            tech = comp.semantic_maps[0].language if hasattr(comp, 'semantic_maps') and comp.semantic_maps else "Unknown"
            purpose = "Frontend" if "vote" in comp_name else "Backend" if "worker" in comp_name else "Service"
            content += f"| {comp_name} | {tech} | {purpose} |\n"
        
        content += """
### 3.3 Current Challenges

Based on the AS-IS analysis, the following challenges have been identified:

1. **Scalability**: Manual scaling of services
2. **Operations**: High operational overhead for infrastructure management  
3. **Security**: Limited security controls and monitoring
4. **Cost**: Unpredictable infrastructure costs
5. **Agility**: Slow deployment and update cycles"""
        
        return content

    def _generate_target_architecture(self, hld_content: HLDContent) -> str:
        """Generate target architecture section"""
        self._add_toc_item("4. Target Architecture", 1)
        
        arch = hld_content.target_architecture
        
        content = """## 4. Target Architecture

### 4.1 Architecture Principles

The target architecture on Azure follows these principles:

1. **Cloud-Native**: Leverage PaaS services where possible
2. **Microservices**: Maintain service independence and scalability
3. **Security by Design**: Implement defense in depth
4. **Cost Optimized**: Right-size resources with auto-scaling
5. **Highly Available**: Multi-zone deployment for critical services
6. **Observable**: Comprehensive monitoring and logging

### 4.2 High-Level Architecture Diagram
┌─────────────────────────────────────────────────────────────────┐
│                        Azure Subscription                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐     ┌─────────────────┐    ┌──────────────┐  │
│  │ Azure Front  │────▶│ App Gateway WAF │───▶│     AKS      │  │
│  │    Door      │     └─────────────────┘    │              │  │
│  └──────────────┘                             │  ┌────────┐  │  │
│                                               │  │  Pods  │  │  │
│                                               │  └────────┘  │  │
│                                               └───────┬──────┘  │
│                                                       │         │
│  ┌──────────────────────────────┬────────────────────┴──────┐  │
│  │                              │                            │  │
│  ▼                              ▼                            ▼  │
│ ┌─────────────┐  ┌──────────────────────┐  ┌──────────────┐  │
│ │Azure Cache  │  │ Azure Database for   │  │ Azure Key    │  │
│ │for Redis    │  │ PostgreSQL           │  │ Vault        │  │
│ └─────────────┘  └──────────────────────┘  └──────────────┘  │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │                    Azure Monitor / App Insights              ││
│ └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

### 4.3 Compute Services

"""
        
        for service, azure_service in arch.compute_services.items():
            content += f"- **{service}**: {azure_service}\n"
        
        content += """
### 4.4 Data Services

"""
        
        for service, azure_service in arch.data_services.items():
            content += f"- **{service}**: {azure_service}\n"
        
        return content

    def _generate_service_mapping(self, hld_content: HLDContent) -> str:
        """Generate service mapping section"""
        self._add_toc_item("5. Service Mapping", 1)
        
        content = """## 5. Service Mapping

### 5.1 Application Services

| Current Component | Current Tech | Target Azure Service | Tier | Complexity | Est. Cost/Month |
|-------------------|--------------|---------------------|------|------------|-----------------|
"""
        
        for mapping in hld_content.azure_service_mappings:
            if 'Database' not in mapping.target_azure_service:
                content += f"| {mapping.component_name} | {mapping.current_technology} | "
                content += f"{mapping.target_azure_service} | {mapping.azure_service_tier} | "
                content += f"{mapping.migration_complexity} | {mapping.estimated_cost_range} |\n"
        
        content += """
### 5.2 Data Services

| Current Component | Current Tech | Target Azure Service | Tier | Complexity | Est. Cost/Month |
|-------------------|--------------|---------------------|------|------------|-----------------|
"""
        
        for mapping in hld_content.azure_service_mappings:
            if 'Database' in mapping.target_azure_service or 'Cache' in mapping.target_azure_service:
                content += f"| {mapping.component_name} | {mapping.current_technology} | "
                content += f"{mapping.target_azure_service} | {mapping.azure_service_tier} | "
                content += f"{mapping.migration_complexity} | {mapping.estimated_cost_range} |\n"
        
        content += """
### 5.3 Service Selection Justification

"""
        
        for mapping in hld_content.azure_service_mappings[:3]:  # Show first 3 as examples
            content += f"""#### {mapping.component_name}
**Selection**: {mapping.target_azure_service}  
**Justification**: {mapping.justification}

"""
        
        return content

    def _generate_migration_strategy(self, hld_content: HLDContent) -> str:
        """Generate migration strategy section"""
        self._add_toc_item("6. Migration Strategy", 1)
        
        content = """## 6. Migration Strategy

### 6.1 Migration Approach

The migration will follow a **phased approach** to minimize risk and ensure business continuity:

1. **Lift and Shift with Optimization**: Containerized services will be migrated with minimal changes
2. **Gradual Modernization**: Post-migration optimization and cloud-native feature adoption
3. **Blue-Green Deployment**: Zero-downtime migration for critical services

### 6.2 Migration Principles

- **Risk Mitigation**: Test thoroughly in non-production before production migration
- **Incremental**: Migrate services based on criticality and dependencies
- **Reversible**: Maintain rollback capability throughout the migration
- **Observable**: Comprehensive monitoring during and after migration
- **Automated**: Use Infrastructure as Code and CI/CD pipelines

### 6.3 Migration Tools

- **Azure Migrate**: Assessment and migration planning
- **Azure Database Migration Service**: Database migration with minimal downtime
- **Azure DevOps**: CI/CD pipeline for automated deployments
- **Terraform**: Infrastructure as Code for Azure resources
- **Azure Container Registry**: Container image management"""
        
        return content

    def _generate_technical_architecture(self, hld_content: HLDContent) -> str:
        """Generate technical architecture details"""
        self._add_toc_item("7. Technical Architecture", 1)
        
        decisions = hld_content.technical_decisions
        
        content = """## 7. Technical Architecture

### 7.1 Container Platform

"""
        
        content += f"**Decision**: {decisions.get('container_orchestration', 'AKS')}\n\n"
        
        content += """**AKS Configuration**:
- **Node Pools**: System (2 nodes) + User (3-10 nodes with auto-scaling)
- **VM Size**: Standard_D4s_v3 for production workloads
- **Networking**: Azure CNI with private cluster
- **Ingress**: NGINX Ingress Controller
- **Service Mesh**: Optional Istio/Linkerd for advanced scenarios

### 7.2 Application Services

"""
        
        content += f"**Decision**: {decisions.get('simple_services', 'App Service')}\n\n"
        
        content += """**App Service Configuration**:
- **Plan**: P1v3 for production, B1 for dev/test
- **Deployment Slots**: Blue-Green deployment support
- **Auto-scale**: CPU/Memory based scaling rules

### 7.3 Data Platform

"""
        
        content += f"**Decision**: {decisions.get('data_migration', 'Azure Database Migration Service')}\n\n"
        
        content += """**Database Configuration**:
- **PostgreSQL**: General Purpose, Gen5, 4 vCores
- **High Availability**: Zone redundant deployment
- **Backup**: Automated daily backups with 35-day retention
- **Redis Cache**: Standard C1 (1GB) with persistence

### 7.4 DevOps and CI/CD

"""
        
        content += f"**Decision**: {decisions.get('ci_cd', 'Azure DevOps')}\n\n"
        
        content += """**Pipeline Architecture**:
```yaml
trigger:
  - main
  - develop

stages:
  - stage: Build
    jobs:
      - job: BuildContainers
      - job: RunTests
      - job: SecurityScan
      
  - stage: DeployDev
    jobs:
      - deployment: DeployToAKS
      
  - stage: DeployProd
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployToProduction
```"""
        
        return content

    def _generate_security_design(self, hld_content: HLDContent) -> str:
        """Generate security design section"""
        self._add_toc_item("8. Security Design", 1)
        
        security = hld_content.target_architecture.security
        
        content = """## 8. Security Design

### 8.1 Security Architecture

The security design follows **Defense in Depth** principles:
┌─────────────────────────────────────────────────┐
│             Azure Security Center                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────┐    ┌──────────┐   ┌──────────┐ │
│  │    WAF    │───▶│   NSGs   │──▶│ Firewall │ │
│  └───────────┘    └──────────┘   └──────────┘ │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │         Identity & Access (AAD)          │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌──────────┐    ┌──────────────┐             │
│  │Key Vault │    │Managed Identity│            │
│  └──────────┘    └──────────────┘             │
└─────────────────────────────────────────────────┘

### 8.2 Identity and Access Management

"""
        
        content += f"- **Identity Provider**: {security.get('identity', 'Azure AD')}\n"
        content += f"- **Service Authentication**: Managed Identity (no passwords)\n"
        content += f"- **User Authentication**: Azure AD with MFA\n"
        content += f"- **RBAC**: Role-based access control at all levels\n"
        
        content += f"""
### 8.3 Secrets Management

- **Secret Store**: {security.get('secrets', 'Azure Key Vault')}
- **Certificate Management**: {security.get('certificates', 'Azure Key Vault')}
- **Key Rotation**: Automated rotation policies
- **Access Control**: Managed Identity for applications

### 8.4 Network Security

- **WAF**: {security.get('waf', 'Application Gateway WAF')}
- **DDoS Protection**: Azure DDoS Protection Standard
- **Network Segmentation**: {security.get('network_security', 'NSGs')}
- **Private Endpoints**: For all PaaS services

### 8.5 Data Protection

- **Encryption at Rest**: {security['encryption']['at_rest']}
- **Encryption in Transit**: {security['encryption']['in_transit']}
- **Data Classification**: Automated with Azure Purview
- **Backup Encryption**: Encrypted backups with customer-managed keys"""
        
        return content

    def _generate_networking_design(self, hld_content: HLDContent) -> str:
        """Generate networking design section"""
        self._add_toc_item("9. Networking Design", 1)
        
        networking = hld_content.target_architecture.networking
        
        content = f"""## 9. Networking Design

### 9.1 Network Topology

**Hub-Spoke Architecture** with centralized services:
                Internet
                    │
             ┌──────┴──────┐
             │ Front Door  │
             └──────┬──────┘
                    │
             ┌──────┴──────┐
             │   App GW    │
             └──────┬──────┘
                    │
┌───────────────────┴───────────────────┐
│          Hub VNet (10.0.0.0/16)       │
│  ┌─────────────┐    ┌──────────────┐ │
│  │ Firewall    │    │ Bastion Host │ │
│  └─────────────┘    └──────────────┘ │
└────────────────┬──────────────────────┘
                 │ Peering
     ┌───────────┴───────────┐
     │                       │
┌────┴─────┐          ┌─────┴────┐
│ Spoke 1  │          │ Spoke 2  │
│   AKS    │          │ Data     │
└──────────┘          └──────────┘

### 9.2 Virtual Network Design

**VNet**: {networking['vnet']['name']}  
**Address Space**: {networking['vnet']['address_space']}

| Subnet | Address Range | Purpose |
|--------|---------------|---------|
"""
        
        for subnet_name, cidr in networking['vnet']['subnets'].items():
            purpose = subnet_name.replace('-subnet', '').replace('-', ' ').title()
            content += f"| {subnet_name} | {cidr} | {purpose} |\n"
        
        content += f"""
### 9.3 Load Balancing

- **Global Load Balancer**: {networking.get('cdn', 'Azure Front Door')}
- **Regional Load Balancer**: {networking.get('load_balancer', 'Application Gateway')}
- **Internal Load Balancer**: AKS Internal Load Balancer

### 9.4 DNS Strategy

- **Public DNS**: {networking.get('dns', 'Azure DNS')}
- **Private DNS**: Azure Private DNS Zones
- **Split-Brain DNS**: Internal and external resolution

### 9.5 Connectivity

- **ExpressRoute/VPN**: For hybrid connectivity (if required)
- **Private Endpoints**: All PaaS services accessed privately
- **Service Endpoints**: For Azure Storage and Key Vault
- **NAT Gateway**: For outbound internet connectivity"""
        
        return content

    def _generate_data_architecture(self, analysis: RepositoryAnalysis, 
                                  hld_content: HLDContent) -> str:
        """Generate data architecture section"""
        self._add_toc_item("10. Data Architecture", 1)
        
        content = """## 10. Data Architecture

### 10.1 Data Services Overview

| Data Store | Purpose | Azure Service | High Availability | Backup Strategy |
|------------|---------|---------------|-------------------|-----------------|
"""
        
        # Add data services from mappings
        for mapping in hld_content.azure_service_mappings:
            if 'Database' in mapping.target_azure_service or 'Cache' in mapping.target_azure_service:
                purpose = "Transactional Data" if 'Database' in mapping.target_azure_service else "Cache/Queue"
                ha = "Zone Redundant" if 'Database' in mapping.target_azure_service else "Standard Replication"
                backup = "Daily, 35-day retention" if 'Database' in mapping.target_azure_service else "Persistence enabled"
                
                content += f"| {mapping.component_name} | {purpose} | {mapping.target_azure_service} | {ha} | {backup} |\n"
        
        content += """
### 10.2 Data Migration Strategy

1. **Assessment Phase**
   - Current data volume assessment
   - Schema compatibility check
   - Performance baseline

2. **Migration Approach**
   - Azure Database Migration Service for PostgreSQL
   - Redis replication for cache migration
   - Minimal downtime approach

3. **Validation**
   - Data integrity checks
   - Performance validation
   - Application testing

### 10.3 Data Security

- **Encryption at Rest**: Transparent Data Encryption (TDE)
- **Encryption in Transit**: SSL/TLS enforced
- **Access Control**: Azure AD authentication where supported
- **Audit Logging**: Enabled for all data operations

### 10.4 Backup and Recovery

- **RPO**: 1 hour (point-in-time restore)
- **RTO**: < 4 hours
- **Backup Retention**: 35 days
- **Geo-redundancy**: Enabled for critical databases
- **DR Testing**: Quarterly DR drills"""
        
        return content

    def _generate_monitoring_strategy(self, hld_content: HLDContent) -> str:
        """Generate monitoring strategy section"""
        self._add_toc_item("11. Monitoring and Observability", 1)
        
        monitoring = hld_content.target_architecture.monitoring
        
        content = f"""## 11. Monitoring and Observability

### 11.1 Monitoring Architecture
Applications/Services
│
├──── Metrics ────▶ {monitoring['metrics']}
│
├──── Logs ──────▶ {monitoring['logs']}
│
└──── Traces ────▶ {monitoring['apm']}
│
▼
{monitoring['dashboards']}
│
▼
{monitoring['alerts']}

### 11.2 Application Performance Monitoring

- **APM Solution**: {monitoring['apm']}
- **Instrumentation**: Auto-instrumentation + custom metrics
- **Distributed Tracing**: End-to-end transaction tracking
- **Performance Baselines**: Established during migration

### 11.3 Infrastructure Monitoring

- **Metrics Collection**: {monitoring['metrics']}
- **Log Aggregation**: {monitoring['logs']}
- **Resource Metrics**: CPU, Memory, Disk, Network
- **Custom Metrics**: Business KPIs

### 11.4 Alerting Strategy

| Alert Category | Examples | Severity | Action |
|----------------|----------|----------|--------|
| Availability | Service down, Health check failed | Critical | Immediate response |
| Performance | Response time > 1s, CPU > 80% | High | Investigation required |
| Capacity | Storage > 80%, Memory > 85% | Medium | Planning required |
| Security | Failed auth attempts, Suspicious activity | High | Security team notified |

### 11.5 Dashboards

- **Executive Dashboard**: Business KPIs, SLA compliance
- **Operations Dashboard**: Service health, performance metrics
- **Security Dashboard**: Security events, compliance status
- **Cost Dashboard**: Resource utilization, spending trends"""
        
        return content

    def _generate_migration_phases(self, hld_content: HLDContent) -> str:
        """Generate detailed migration phases"""
        self._add_toc_item("12. Migration Phases", 1)
        
        content = """## 12. Migration Phases

### 12.1 Migration Timeline Overview
Week  1  2  3  4  5  6  7  8  9  10 11 12
│--Phase 1--│--Phase 2--│--P3-│-P4-│P5│
Foundation  Data Svcs   NCrit Crit Cut

### 12.2 Detailed Phase Breakdown

"""
        
        for phase in hld_content.migration_phases:
            content += f"""#### Phase {phase.phase_number}: {phase.phase_name}

**Duration**: {phase.duration}  
**Dependencies**: {', '.join(phase.dependencies) if phase.dependencies else 'None'}

**Components**:
"""
            for comp in phase.components:
                content += f"- {comp}\n"
            
            content += "\n**Key Activities**:\n"
            for i, activity in enumerate(phase.activities, 1):
                content += f"{i}. {activity}\n"
            
            content += "\n**Risks**:\n"
            for risk in phase.risks:
                content += f"- {risk}\n"
            
            content += "\n**Success Criteria**:\n"
            for criteria in phase.success_criteria:
                content += f"- {criteria}\n"
            
            content += "\n---\n\n"
        
        return content

    def _generate_risk_assessment(self, hld_content: HLDContent) -> str:
        """Generate risk assessment section"""
        self._add_toc_item("13. Risk Assessment and Mitigation", 1)
        
        content = """## 13. Risk Assessment and Mitigation

### 13.1 Risk Matrix

| Risk | Probability | Impact | Severity | Mitigation Strategy |
|------|-------------|--------|----------|-------------------|
"""
        
        risk_items = [
            {
                'risk': 'Data Loss During Migration',
                'probability': 'Low',
                'impact': 'High',
                'severity': 'High',
                'mitigation': hld_content.risk_mitigation.get('data_loss', 'Backup strategy')
            },
            {
                'risk': 'Service Disruption',
                'probability': 'Medium',
                'impact': 'High',
                'severity': 'High',
                'mitigation': hld_content.risk_mitigation.get('service_disruption', 'Blue-green deployment')
            },
            {
                'risk': 'Performance Degradation',
                'probability': 'Medium',
                'impact': 'Medium',
                'severity': 'Medium',
                'mitigation': hld_content.risk_mitigation.get('performance_degradation', 'Performance testing')
            },
            {
                'risk': 'Cost Overrun',
                'probability': 'Medium',
                'impact': 'Medium',
                'severity': 'Medium',
                'mitigation': hld_content.risk_mitigation.get('cost_overrun', 'Cost monitoring')
            },
            {
                'risk': 'Security Vulnerabilities',
                'probability': 'Low',
                'impact': 'High',
                'severity': 'High',
                'mitigation': hld_content.risk_mitigation.get('security_vulnerabilities', 'Security assessment')
            }
        ]
        
        for item in risk_items:
            content += f"| {item['risk']} | {item['probability']} | {item['impact']} | "
            content += f"{item['severity']} | {item['mitigation']} |\n"
        
        content += """
### 13.2 Detailed Mitigation Strategies

"""
        
        for risk_type, mitigation in hld_content.risk_mitigation.items():
            risk_name = risk_type.replace('_', ' ').title()
            content += f"""#### {risk_name}
**Strategy**: {mitigation}

"""
        
        content += """### 13.3 Contingency Planning

1. **Rollback Strategy**
  - Maintain source systems until validation complete
  - Database replication for quick rollback
  - DNS-based traffic switching

2. **Business Continuity**
  - Parallel run capability
  - Gradual migration approach
  - Communication plan for stakeholders

3. **Technical Contingencies**
  - Alternative Azure services identified
  - Hybrid operation mode possible
  - Performance tuning playbooks ready"""
        
        return content

    def _generate_cost_analysis(self, hld_content: HLDContent) -> str:
        """Generate cost analysis section"""
        self._add_toc_item("14. Cost Analysis", 1)
        
        cost = hld_content.cost_analysis
        
        content = f"""## 14. Cost Analysis

### 14.1 Estimated Monthly Costs

| Category | Estimated Cost/Month | Percentage |
|----------|---------------------|------------|
"""
        
        total = cost['total_monthly']
        for category, amount in cost['monthly_breakdown'].items():
            percentage = (amount / total * 100) if total > 0 else 0
            content += f"| {category.title()} | ${amount:,.0f} | {percentage:.1f}% |\n"
        
        content += f"""| **Total** | **${total:,.0f}** | **100%** |

### 14.2 Annual Projection

- **Monthly Cost**: ${total:,.0f}
- **Annual Cost**: ${cost['total_annual']:,.0f}
- **3-Year TCO**: ${cost['total_annual'] * 3:,.0f}

### 14.3 Cost Optimization Opportunities

"""
        
        for optimization in cost['cost_optimization']:
            content += f"- {optimization}\n"
        
        content += """
### 14.4 Cost Comparison

| Item | Current (Estimated) | Azure | Savings |
|------|-------------------|--------|---------|
| Infrastructure | $X,XXX | ${:,.0f} | TBD |
| Operations | $X,XXX | Reduced | ~30-40% |
| Licensing | $X,XXX | Included | Varies |

### 14.5 Return on Investment

**Quantifiable Benefits**:
""".format(total)
        
        for factor in cost['roi_factors']:
            content += f"- {factor}\n"
        
        content += """
**Expected ROI Timeline**: 18-24 months based on operational savings and efficiency gains"""
        
        return content

    def _generate_success_criteria(self) -> str:
        """Generate success criteria section"""
        self._add_toc_item("15. Success Criteria", 1)
        
        return """## 15. Success Criteria

### 15.1 Technical Success Criteria

- [ ] All services successfully migrated to Azure
- [ ] Zero data loss during migration
- [ ] Performance SLAs met or exceeded
- [ ] Security baseline implemented
- [ ] Automated CI/CD pipelines operational
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery tested successfully

### 15.2 Operational Success Criteria

- [ ] Operations team trained on Azure
- [ ] Runbooks and documentation updated
- [ ] Support processes established
- [ ] Incident response procedures tested
- [ ] Cost tracking and optimization in place

### 15.3 Business Success Criteria

- [ ] Minimal business disruption (< 4 hours total)
- [ ] User experience maintained or improved
- [ ] Scalability objectives achieved
- [ ] Cost targets met (± 10%)
- [ ] Compliance requirements satisfied

### 15.4 Migration Acceptance Criteria

**Phase Gate Reviews**: Each phase must meet the following criteria before proceeding:

1. **Functional Testing**: 100% pass rate
2. **Performance Testing**: Meet or exceed baseline
3. **Security Validation**: No critical vulnerabilities
4. **Documentation**: Updated and reviewed
5. **Stakeholder Approval**: Sign-off obtained"""

    def _generate_appendices(self) -> str:
        """Generate appendices"""
        self._add_toc_item("16. Appendices", 1)
        
        return """## 16. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| AKS | Azure Kubernetes Service |
| PaaS | Platform as a Service |
| IaC | Infrastructure as Code |
| NSG | Network Security Group |
| WAF | Web Application Firewall |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |

### Appendix B: Reference Architecture

- [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/)
- [AKS Best Practices](https://docs.microsoft.com/azure/aks/best-practices)
- [Azure Security Best Practices](https://docs.microsoft.com/azure/security/fundamentals/best-practices-and-patterns)

### Appendix C: Configuration Templates

Sample Terraform configuration for AKS:

```hcl
resource "azurerm_kubernetes_cluster" "main" {
 name                = "${var.prefix}-aks"
 location            = azurerm_resource_group.main.location
 resource_group_name = azurerm_resource_group.main.name
 dns_prefix          = var.prefix

 default_node_pool {
   name                = "default"
   node_count          = 3
   vm_size            = "Standard_D4s_v3"
   enable_auto_scaling = true
   min_count          = 2
   max_count          = 10
 }

 identity {
   type = "SystemAssigned"
 }

 network_profile {
   network_plugin = "azure"
   network_policy = "calico"
 }
}
```

### Appendix D: Contact Information

| Role | Name | Email | Phone |
|------|------|-------|-------|
| Project Manager | TBD | TBD | TBD |
| Technical Lead | TBD | TBD | TBD |
| Azure Architect | TBD | TBD | TBD |
| Security Lead | TBD | TBD | TBD |"""

    def _add_toc_item(self, title: str, level: int):
        """Add item to table of contents"""
        self.toc_items.append((title, level))

    def _build_toc(self) -> str:
        """Build the actual table of contents"""
        toc = ""
        for title, level in self.toc_items:
            # Skip the TOC itself
            if "Table of Contents" in title:
                continue
            indent = "  " * (level - 1)
            # Extract number if present
            if title[0].isdigit():
                toc += f"{indent}{title}\n"
            else:
                toc += f"{indent}- {title}\n"
        return toc


def main():
    """Main function for testing the HLD document generator"""
    # This would be used for testing the document generator
    pass


if __name__ == "__main__":
    main()