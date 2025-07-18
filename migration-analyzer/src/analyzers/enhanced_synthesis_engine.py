"""
Enhanced synthesis engine that provides clear inference indicators and removes vague labels
This addresses the overstated conclusions and vague labels issue
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ConfidenceLevel(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFERRED = "INFERRED"

@dataclass
class InferenceIndicator:
    """Indicates how a conclusion was reached"""
    value: str
    confidence: ConfidenceLevel
    evidence: List[str]
    reasoning: str
    limitations: List[str]

@dataclass
class ArchitectureAssessment:
    """Enhanced architecture assessment with confidence indicators"""
    style: InferenceIndicator
    patterns: List[InferenceIndicator]
    complexity: InferenceIndicator
    maturity: InferenceIndicator
    scalability: InferenceIndicator

@dataclass
class BusinessCriticalityAssessment:
    """Enhanced business criticality assessment"""
    level: InferenceIndicator
    reasoning: str
    factors: List[str]
    confidence_notes: List[str]

class EnhancedSynthesisEngine:
    """Enhanced synthesis engine with clear inference indicators"""
    
    def __init__(self):
        # Architecture pattern detection
        self.architecture_patterns = {
            'microservices': {
                'indicators': [
                    'multiple_deployable_components',
                    'independent_databases',
                    'api_communication',
                    'container_deployment',
                    'separate_build_processes'
                ],
                'min_confidence_indicators': 3
            },
            'monolithic': {
                'indicators': [
                    'single_deployable_unit',
                    'shared_database',
                    'direct_method_calls',
                    'single_build_process'
                ],
                'min_confidence_indicators': 2
            },
            'service_oriented': {
                'indicators': [
                    'web_services',
                    'service_contracts',
                    'enterprise_service_bus',
                    'soap_interfaces'
                ],
                'min_confidence_indicators': 2
            },
            'event_driven': {
                'indicators': [
                    'message_queues',
                    'event_publishers',
                    'event_subscribers',
                    'async_processing'
                ],
                'min_confidence_indicators': 2
            }
        }
        
        # Business criticality indicators
        self.criticality_indicators = {
            'CRITICAL': [
                'customer_facing', 'revenue_generating', 'mission_critical',
                'real_time_processing', 'financial_transactions', 'user_authentication'
            ],
            'HIGH': [
                'core_business_logic', 'user_management', 'data_processing',
                'api_gateway', 'primary_service'
            ],
            'MEDIUM': [
                'internal_tools', 'reporting', 'analytics', 'monitoring',
                'support_services'
            ],
            'LOW': [
                'development_tools', 'testing', 'experimental', 'poc',
                'prototype', 'sample', 'demo', 'example'
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            'HIGH': [
                'multiple_languages', 'complex_dependencies', 'large_codebase',
                'many_integrations', 'legacy_components'
            ],
            'MEDIUM': [
                'moderate_size', 'some_dependencies', 'standard_patterns',
                'few_integrations'
            ],
            'LOW': [
                'simple_structure', 'minimal_dependencies', 'single_purpose',
                'clear_patterns'
            ]
        }
    
    def assess_architecture(self, components: Dict[str, Any], 
                          infrastructure: Dict[str, Any],
                          deployment_configs: Dict[str, Any]) -> ArchitectureAssessment:
        """Assess architecture with confidence indicators"""
        
        # Detect architecture style
        style = self._detect_architecture_style(components, infrastructure, deployment_configs)
        
        # Detect patterns
        patterns = self._detect_architecture_patterns(components, infrastructure)
        
        # Assess complexity
        complexity = self._assess_complexity(components, infrastructure)
        
        # Assess maturity
        maturity = self._assess_maturity(components, infrastructure, deployment_configs)
        
        # Assess scalability
        scalability = self._assess_scalability(components, infrastructure)
        
        return ArchitectureAssessment(
            style=style,
            patterns=patterns,
            complexity=complexity,
            maturity=maturity,
            scalability=scalability
        )
    
    def _detect_architecture_style(self, components: Dict[str, Any], 
                                 infrastructure: Dict[str, Any],
                                 deployment_configs: Dict[str, Any]) -> InferenceIndicator:
        """Detect architecture style with evidence"""
        
        evidence = []
        scores = {}
        
        # Analyze components
        component_count = len(components)
        evidence.append(f"Found {component_count} components")
        
        # Check for microservices indicators
        microservices_score = 0
        if component_count > 1:
            microservices_score += 2
            evidence.append("Multiple deployable components detected")
        
        # Check for containerization
        containerized_components = 0
        for comp_name, comp_data in components.items():
            if hasattr(comp_data, 'docker_files') and comp_data.docker_files:
                containerized_components += 1
            elif hasattr(comp_data, 'packaging') and comp_data.packaging == 'docker':
                containerized_components += 1
        
        if containerized_components > 0:
            microservices_score += 1
            evidence.append(f"{containerized_components} containerized components")
        
        # Check for independent deployment
        if len(deployment_configs) > 1:
            microservices_score += 1
            evidence.append("Multiple deployment configurations")
        
        scores['microservices'] = microservices_score
        
        # Check for monolithic indicators
        monolithic_score = 0
        if component_count == 1:
            monolithic_score += 2
            evidence.append("Single deployable component")
        
        if containerized_components == 0:
            monolithic_score += 1
            evidence.append("No containerization detected")
        
        scores['monolithic'] = monolithic_score
        
        # Determine style
        if scores['microservices'] >= 3:
            confidence = ConfidenceLevel.HIGH if scores['microservices'] >= 4 else ConfidenceLevel.MEDIUM
            return InferenceIndicator(
                value="microservices",
                confidence=confidence,
                evidence=evidence,
                reasoning="Multiple components with independent deployment characteristics",
                limitations=["Cannot determine communication patterns without runtime analysis"]
            )
        elif scores['monolithic'] >= 2:
            confidence = ConfidenceLevel.HIGH if scores['monolithic'] >= 3 else ConfidenceLevel.MEDIUM
            return InferenceIndicator(
                value="monolithic",
                confidence=confidence,
                evidence=evidence,
                reasoning="Single deployable unit with unified deployment",
                limitations=["Internal structure not analyzed"]
            )
        else:
            return InferenceIndicator(
                value="unknown",
                confidence=ConfidenceLevel.LOW,
                evidence=evidence,
                reasoning="Insufficient evidence to determine architecture style",
                limitations=["Need runtime analysis and communication patterns"]
            )
    
    def _detect_architecture_patterns(self, components: Dict[str, Any], 
                                    infrastructure: Dict[str, Any]) -> List[InferenceIndicator]:
        """Detect architecture patterns with evidence"""
        patterns = []
        
        # API Gateway pattern
        api_gateway_evidence = []
        for comp_name, comp_data in components.items():
            if 'gateway' in comp_name.lower() or 'proxy' in comp_name.lower():
                api_gateway_evidence.append(f"Component '{comp_name}' suggests API Gateway")
        
        if api_gateway_evidence:
            patterns.append(InferenceIndicator(
                value="api_gateway",
                confidence=ConfidenceLevel.MEDIUM,
                evidence=api_gateway_evidence,
                reasoning="Component naming suggests API Gateway pattern",
                limitations=["Cannot confirm without configuration analysis"]
            ))
        
        # Database per service pattern
        database_evidence = []
        database_count = 0
        for comp_name, comp_data in components.items():
            if hasattr(comp_data, 'external_dependencies'):
                for dep in comp_data.external_dependencies:
                    if any(db in dep.lower() for db in ['database', 'db', 'postgresql', 'mysql', 'mongodb']):
                        database_count += 1
                        database_evidence.append(f"Component '{comp_name}' has database dependency")
        
        if database_count > 1:
            patterns.append(InferenceIndicator(
                value="database_per_service",
                confidence=ConfidenceLevel.MEDIUM,
                evidence=database_evidence,
                reasoning="Multiple database dependencies suggest database per service pattern",
                limitations=["Cannot confirm database isolation without runtime analysis"]
            ))
        
        return patterns
    
    def _assess_complexity(self, components: Dict[str, Any], 
                         infrastructure: Dict[str, Any]) -> InferenceIndicator:
        """Assess complexity with evidence"""
        
        evidence = []
        complexity_score = 0
        
        # Component count factor
        component_count = len(components)
        evidence.append(f"Component count: {component_count}")
        
        if component_count > 5:
            complexity_score += 2
        elif component_count > 2:
            complexity_score += 1
        
        # Language diversity
        languages = set()
        for comp_name, comp_data in components.items():
            if hasattr(comp_data, 'language') and comp_data.language != 'unknown':
                languages.add(comp_data.language)
        
        language_count = len(languages)
        evidence.append(f"Programming languages: {language_count} ({', '.join(languages)})")
        
        if language_count > 3:
            complexity_score += 2
        elif language_count > 1:
            complexity_score += 1
        
        # Infrastructure complexity
        infra_count = len(infrastructure)
        evidence.append(f"Infrastructure components: {infra_count}")
        
        if infra_count > 3:
            complexity_score += 1
        
        # Determine complexity level
        if complexity_score >= 4:
            level = "HIGH"
            confidence = ConfidenceLevel.HIGH
        elif complexity_score >= 2:
            level = "MEDIUM"
            confidence = ConfidenceLevel.MEDIUM
        else:
            level = "LOW"
            confidence = ConfidenceLevel.HIGH
        
        return InferenceIndicator(
            value=level,
            confidence=confidence,
            evidence=evidence,
            reasoning=f"Complexity score: {complexity_score}/6 based on component count, language diversity, and infrastructure",
            limitations=["Does not account for code complexity or business logic complexity"]
        )
    
    def _assess_maturity(self, components: Dict[str, Any], 
                        infrastructure: Dict[str, Any],
                        deployment_configs: Dict[str, Any]) -> InferenceIndicator:
        """Assess maturity with evidence"""
        
        evidence = []
        maturity_score = 0
        
        # Containerization
        containerized_count = 0
        for comp_name, comp_data in components.items():
            if hasattr(comp_data, 'packaging') and comp_data.packaging == 'docker':
                containerized_count += 1
        
        if containerized_count > 0:
            maturity_score += 1
            evidence.append(f"{containerized_count} containerized components")
        
        # Deployment automation
        if deployment_configs:
            maturity_score += 1
            evidence.append("Deployment configurations present")
        
        # Build automation
        build_automation_count = 0
        for comp_name, comp_data in components.items():
            if hasattr(comp_data, 'build_tool') and comp_data.build_tool != 'unknown':
                build_automation_count += 1
        
        if build_automation_count > 0:
            maturity_score += 1
            evidence.append(f"{build_automation_count} components have build automation")
        
        # Determine maturity level
        if maturity_score >= 3:
            level = "HIGH"
            confidence = ConfidenceLevel.MEDIUM
        elif maturity_score >= 2:
            level = "MEDIUM"
            confidence = ConfidenceLevel.MEDIUM
        else:
            level = "LOW"
            confidence = ConfidenceLevel.HIGH
        
        return InferenceIndicator(
            value=level,
            confidence=confidence,
            evidence=evidence,
            reasoning=f"Maturity score: {maturity_score}/3 based on containerization, deployment, and build automation",
            limitations=["Does not assess testing maturity, monitoring, or operational practices"]
        )
    
    def _assess_scalability(self, components: Dict[str, Any], 
                          infrastructure: Dict[str, Any]) -> InferenceIndicator:
        """Assess scalability with evidence"""
        
        evidence = []
        scalability_score = 0
        
        # Microservices architecture
        if len(components) > 1:
            scalability_score += 1
            evidence.append("Multiple services enable horizontal scaling")
        
        # Containerization
        containerized_count = sum(1 for comp_name, comp_data in components.items()
                                if hasattr(comp_data, 'packaging') and comp_data.packaging == 'docker')
        
        if containerized_count > 0:
            scalability_score += 1
            evidence.append("Containerization enables easy scaling")
        
        # Stateless services (inferred)
        stateless_indicators = 0
        for comp_name, comp_data in components.items():
            if hasattr(comp_data, 'external_dependencies'):
                for dep in comp_data.external_dependencies:
                    if any(db in dep.lower() for db in ['database', 'redis', 'cache']):
                        stateless_indicators += 1
                        break
        
        if stateless_indicators > 0:
            scalability_score += 1
            evidence.append("External data storage suggests stateless services")
        
        # Determine scalability level
        if scalability_score >= 3:
            level = "HIGH"
            confidence = ConfidenceLevel.MEDIUM
        elif scalability_score >= 2:
            level = "MEDIUM"
            confidence = ConfidenceLevel.MEDIUM
        else:
            level = "LOW"
            confidence = ConfidenceLevel.HIGH
        
        return InferenceIndicator(
            value=level,
            confidence=confidence,
            evidence=evidence,
            reasoning=f"Scalability score: {scalability_score}/3 based on architecture, containerization, and state management",
            limitations=["Cannot assess actual performance characteristics without load testing"]
        )
    
    def assess_business_criticality(self, components: Dict[str, Any], 
                                  documentation: Dict[str, Any],
                                  repository_context: Dict[str, Any]) -> BusinessCriticalityAssessment:
        """Assess business criticality with clear inference indicators"""
        
        evidence_factors = []
        confidence_notes = []
        
        # Check documentation for criticality indicators
        doc_text = ""
        if documentation:
            doc_text = str(documentation).lower()
        
        # Check repository context
        repo_name = repository_context.get('name', '').lower()
        
        # Look for criticality indicators
        criticality_scores = {level: 0 for level in self.criticality_indicators.keys()}
        
        for level, indicators in self.criticality_indicators.items():
            for indicator in indicators:
                if indicator in doc_text or indicator in repo_name:
                    criticality_scores[level] += 1
                    evidence_factors.append(f"'{indicator}' found in documentation/repository name")
        
        # Determine criticality level
        max_score = max(criticality_scores.values())
        if max_score == 0:
            level = "MEDIUM"
            confidence = ConfidenceLevel.INFERRED
            reasoning = "No clear criticality indicators found, defaulting to MEDIUM"
            confidence_notes.append("Business criticality cannot be determined from technical artifacts alone")
            confidence_notes.append("Requires business stakeholder input for accurate assessment")
        else:
            level = max(criticality_scores.keys(), key=lambda k: criticality_scores[k])
            confidence = ConfidenceLevel.MEDIUM if max_score > 2 else ConfidenceLevel.LOW
            reasoning = f"Inferred from keywords and context (score: {max_score})"
            confidence_notes.append("Assessment based on limited technical indicators")
        
        return BusinessCriticalityAssessment(
            level=InferenceIndicator(
                value=level,
                confidence=confidence,
                evidence=evidence_factors,
                reasoning=reasoning,
                limitations=["Technical analysis cannot determine actual business impact"]
            ),
            reasoning=reasoning,
            factors=evidence_factors,
            confidence_notes=confidence_notes
        )
    
    def generate_confidence_summary(self, assessment: ArchitectureAssessment,
                                  criticality: BusinessCriticalityAssessment) -> Dict[str, Any]:
        """Generate a summary of confidence levels"""
        return {
            'architecture_style': {
                'value': assessment.style.value,
                'confidence': assessment.style.confidence.value,
                'evidence_count': len(assessment.style.evidence)
            },
            'business_criticality': {
                'value': criticality.level.value,
                'confidence': criticality.level.confidence.value,
                'is_inferred': criticality.level.confidence == ConfidenceLevel.INFERRED
            },
            'complexity': {
                'value': assessment.complexity.value,
                'confidence': assessment.complexity.confidence.value
            },
            'overall_confidence': self._calculate_overall_confidence(assessment, criticality)
        }
    
    def _calculate_overall_confidence(self, assessment: ArchitectureAssessment,
                                    criticality: BusinessCriticalityAssessment) -> str:
        """Calculate overall confidence level"""
        confidence_values = [
            assessment.style.confidence,
            assessment.complexity.confidence,
            assessment.maturity.confidence,
            criticality.level.confidence
        ]
        
        high_count = sum(1 for c in confidence_values if c == ConfidenceLevel.HIGH)
        medium_count = sum(1 for c in confidence_values if c == ConfidenceLevel.MEDIUM)
        inferred_count = sum(1 for c in confidence_values if c == ConfidenceLevel.INFERRED)
        
        if high_count >= 3:
            return "HIGH"
        elif medium_count >= 2 and inferred_count == 0:
            return "MEDIUM"
        else:
            return "LOW"