"""
Migration Analyzer - Analyzers Module
"""

# Core analyzers
from .component_discovery import ComponentDiscoveryAnalyzer
from .enhanced_component_discovery import EnhancedComponentDiscoveryAnalyzer
from .documentation_analyzer import DocumentationAnalyzer
from .git_history_analyzer import GitHistoryAnalyzer
from .enhanced_git_history_analyzer import EnhancedGitHistoryAnalyzer
from .vulnerability_analyzer import VulnerabilityAnalyzer
from .enhanced_synthesis_engine import EnhancedSynthesisEngine
from .comprehensive_llm_synthesizer import ComprehensiveLLMSynthesizer
from .cross_artifact_correlator import CrossArtifactCorrelator
from .directory_structure_analyzer import DirectoryStructureAnalyzer
from .unified_correlation_engine import UnifiedCorrelationEngine

# LLM-enhanced analyzers
try:
    from .llm_enhanced_classifier import LLMEnhancedClassifier
    from .llm_security_synthesizer import LLMSecuritySynthesizer
except ImportError:
    # Graceful fallback if LLM dependencies are missing
    LLMEnhancedClassifier = None
    LLMSecuritySynthesizer = None

__all__ = [
    'ComponentDiscoveryAnalyzer',
    'EnhancedComponentDiscoveryAnalyzer', 
    'DocumentationAnalyzer',
    'GitHistoryAnalyzer',
    'EnhancedGitHistoryAnalyzer',
    'VulnerabilityAnalyzer',
    'EnhancedSynthesisEngine',
    'ComprehensiveLLMSynthesizer',
    'CrossArtifactCorrelator',
    'DirectoryStructureAnalyzer',
    'UnifiedCorrelationEngine',
    'LLMEnhancedClassifier',
    'LLMSecuritySynthesizer',
]