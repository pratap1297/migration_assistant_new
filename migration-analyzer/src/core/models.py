from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class FunctionInfo:
    name: str
    start_line: int
    end_line: int
    calls: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    
@dataclass
class ClassInfo:
    name: str
    start_line: int
    end_line: int
    methods: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)

@dataclass
class DatabaseInteraction:
    operation: str  # SELECT, INSERT, UPDATE, DELETE
    table: Optional[str] = None
    line_number: int = 0
    raw_query: Optional[str] = None

@dataclass
class HttpCall:
    url: str
    method: str  # GET, POST, etc.
    line_number: int
    is_internal: bool = False

@dataclass
class ApiEndpoint:
    path: str
    methods: List[str]
    handler_function: str
    line_number: int

@dataclass
class SemanticCodeMap:
    file_path: str
    language: str
    api_endpoints: List[ApiEndpoint] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    database_interactions: List[DatabaseInteraction] = field(default_factory=list)
    outbound_http_calls: List[HttpCall] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

@dataclass
class SecurityFindings:
    component_name: str
    authentication_mechanisms: List[str] = field(default_factory=list)
    authorization_patterns: List[str] = field(default_factory=list)
    encryption_usage: List[str] = field(default_factory=list)
    potential_vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)
    hardcoded_secrets: List[Dict[str, str]] = field(default_factory=list)

# Sprint 2 Data Structures

@dataclass
class ServiceDependency:
    """Represents a dependency between two services/components"""
    source_component: str
    target_component: str
    dependency_type: str  # "http", "database", "queue", "file", "internal"
    endpoint: Optional[str] = None
    method: Optional[str] = None
    criticality: str = "medium"  # "low", "medium", "high", "critical"
    
@dataclass
class ServiceCriticality:
    """Represents the business criticality assessment of a service"""
    component_name: str
    business_criticality: str  # "low", "medium", "high", "critical"
    technical_complexity: str  # "low", "medium", "high"
    user_impact: str  # "low", "medium", "high"
    data_sensitivity: str  # "low", "medium", "high"
    reasoning: str
    score: float  # 0.0 to 1.0
    
@dataclass
class ComponentInfo:
    """Enhanced component information with metrics and dependencies"""
    name: str
    path: str
    language: str
    files_count: int
    lines_of_code: int
    api_endpoints_count: int
    database_operations_count: int
    http_calls_count: int
    dependencies: List[ServiceDependency] = field(default_factory=list)
    criticality: Optional[ServiceCriticality] = None
    
@dataclass
class RepositoryAnalysis:
    """Complete repository analysis results for Sprint 2"""
    repository_url: str
    analysis_date: datetime
    components: List[ComponentInfo] = field(default_factory=list)
    dependencies: List[ServiceDependency] = field(default_factory=list)
    criticality_assessments: List[ServiceCriticality] = field(default_factory=list)
    semantic_maps: Dict[str, List[SemanticCodeMap]] = field(default_factory=dict)
    security_findings: Dict[str, SecurityFindings] = field(default_factory=dict)
    architecture_insights: List[str] = field(default_factory=list)
    migration_recommendations: List[str] = field(default_factory=list)

# Sprint 3 Data Structures

@dataclass
class AzureServiceMapping:
    """Maps current component to Azure service"""
    component_name: str
    current_technology: str
    target_azure_service: str
    azure_service_tier: str  # Basic, Standard, Premium
    justification: str
    migration_complexity: str  # Low, Medium, High
    estimated_cost_range: str  # $/month

@dataclass
class MigrationPhase:
    """Represents a migration phase"""
    phase_number: int
    phase_name: str
    duration: str  # e.g., "2-3 weeks"
    components: List[str]
    dependencies: List[str]  # Previous phases
    activities: List[str]
    risks: List[str]
    success_criteria: List[str]

@dataclass
class AzureArchitecture:
    """Target Azure architecture design"""
    compute_services: Dict[str, str]  # component -> Azure service
    data_services: Dict[str, str]  # database -> Azure service
    networking: Dict[str, Any]
    security: Dict[str, Any]
    monitoring: Dict[str, Any]
    estimated_monthly_cost: str

@dataclass
class HLDContent:
    """High-Level Design content structure"""
    executive_summary: str
    scope: Dict[str, Any]
    azure_service_mappings: List[AzureServiceMapping]
    target_architecture: AzureArchitecture
    migration_phases: List[MigrationPhase]
    technical_decisions: Dict[str, str]
    risk_mitigation: Dict[str, str]
    cost_analysis: Dict[str, Any]