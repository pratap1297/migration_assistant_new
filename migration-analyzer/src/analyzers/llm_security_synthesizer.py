#!/usr/bin/env python3
"""
LLM-Enhanced Security Synthesizer
Acts as a "Senior Security Analyst" to review and synthesize findings from automated scanners
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Use centralized LLM configuration
from ..config import get_llm_config, is_llm_available, get_security_model

@dataclass
class SynthesizedSecurityFinding:
    """Synthesized security finding from LLM analysis"""
    id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: str = ""
    confidence: float = 0.0
    reasoning: str = ""

@dataclass
class SecuritySynthesis:
    """Complete security synthesis"""
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings: List[SynthesizedSecurityFinding]
    priority_recommendation: str
    summary: str
    confidence_notes: List[str]

class LLMSecuritySynthesizer:
    """LLM-powered security analysis synthesizer"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the LLM security synthesizer"""
        # Use centralized LLM configuration
        self.llm_config = get_llm_config()
        self.llm = get_security_model()
        self.gemini_available = is_llm_available()
        
        if self.gemini_available:
            print("OK [LLM-SECURITY] Gemini LLM initialized successfully")
        else:
            print("WARNING [LLM-SECURITY] LLM not available - falling back to rule-based analysis")
    
    def synthesize_security_findings(self, 
                                   vulnerability_findings: List[Any],
                                   base_image_risks: List[Dict[str, Any]],
                                   manual_findings: List[Any],
                                   summary_count: int = 0) -> SecuritySynthesis:
        """
        Synthesize security findings from multiple sources using LLM analysis
        
        Args:
            vulnerability_findings: List of VulnerabilityFinding objects
            base_image_risks: List of base image risk dictionaries
            manual_findings: List of manual scan findings
            summary_count: Count from summary (to detect inconsistencies)
            
        Returns:
            SecuritySynthesis with consistent, prioritized findings
        """
        
        if not self.gemini_available or not self.llm:
            return self._fallback_synthesis(vulnerability_findings, base_image_risks, manual_findings)
        
        try:
            # Build raw findings context
            raw_findings = self._build_raw_findings_context(
                vulnerability_findings, base_image_risks, manual_findings, summary_count
            )
            
            # Generate LLM prompt
            prompt = self._create_synthesis_prompt(raw_findings)
            
            print(f"LLM [LLM-SECURITY] Synthesizing {len(raw_findings)} security findings...")
            
            # Get LLM response
            response = self.llm.generate_content(prompt)
            
            # Parse response
            synthesis = self._parse_synthesis_response(response.text)
            
            return synthesis
            
        except Exception as e:
            print(f"WARNING [LLM-SECURITY] Error synthesizing findings: {e}")
            return self._fallback_synthesis(vulnerability_findings, base_image_risks, manual_findings)
    
    def _build_raw_findings_context(self, 
                                   vulnerability_findings: List[Any],
                                   base_image_risks: List[Dict[str, Any]],
                                   manual_findings: List[Any],
                                   summary_count: int) -> List[Dict[str, Any]]:
        """Build context of raw findings for LLM analysis"""
        
        raw_findings = []
        
        # Add vulnerability findings
        for finding in vulnerability_findings:
            raw_findings.append({
                'source': 'vulnerability_scanner',
                'id': getattr(finding, 'id', 'unknown'),
                'severity': getattr(finding, 'severity', 'UNKNOWN'),
                'title': getattr(finding, 'title', 'Unknown vulnerability'),
                'description': getattr(finding, 'description', ''),
                'file_path': getattr(finding, 'file_path', None),
                'line_number': getattr(finding, 'line_number', None),
                'package': getattr(finding, 'package', None),
                'cve_id': getattr(finding, 'cve_id', None)
            })
        
        # Add base image risks
        for risk in base_image_risks:
            raw_findings.append({
                'source': 'base_image_scanner',
                'id': f"BASE_IMAGE_{risk.get('component', 'unknown')}",
                'severity': risk.get('risk_level', 'UNKNOWN'),
                'title': f"Vulnerable Base Image: {risk.get('base_image', 'unknown')}",
                'description': risk.get('description', ''),
                'file_path': f"{risk.get('component', 'unknown')}/Dockerfile",
                'line_number': 1,
                'package': risk.get('base_image', ''),
                'recommendation': risk.get('recommendation', '')
            })
        
        # Add manual findings
        for finding in manual_findings:
            raw_findings.append({
                'source': 'manual_scanner',
                'id': getattr(finding, 'id', 'unknown'),
                'severity': getattr(finding, 'severity', 'UNKNOWN'),
                'title': getattr(finding, 'title', 'Manual finding'),
                'description': getattr(finding, 'description', ''),
                'file_path': getattr(finding, 'file_path', None),
                'line_number': getattr(finding, 'line_number', None)
            })
        
        # Add summary inconsistency context
        if summary_count != len(raw_findings):
            raw_findings.append({
                'source': 'summary_validation',
                'id': 'SUMMARY_INCONSISTENCY',
                'severity': 'INFO',
                'title': 'Summary Count Inconsistency',
                'description': f'Summary reports {summary_count} findings but detailed scan found {len(raw_findings)} findings',
                'file_path': None,
                'line_number': None
            })
        
        return raw_findings
    
    def _create_synthesis_prompt(self, raw_findings: List[Dict[str, Any]]) -> str:
        """Create LLM prompt for security synthesis"""
        
        findings_json = json.dumps(raw_findings, indent=2)
        
        return f"""You are a Senior Security Analyst reviewing findings from multiple automated security scanners. Your job is to synthesize these raw findings into a consistent, prioritized security assessment.

**Raw Findings from Scanners:**
{findings_json}

**Analysis Requirements:**

1. **Prioritization**: Rank findings by actual risk level:
   - Prioritize specific, verifiable findings (like outdated software versions with CVEs)
   - Deprioritize generic findings without context (like regex matches without file paths)
   - Ignore summary inconsistencies in your final count

2. **Validation**: 
   - Flag findings that lack actionable information (missing file paths, line numbers)
   - Identify the most critical, verifiable risks
   - Note any contradictions between different scanners

3. **Consolidation**:
   - Remove duplicate findings
   - Combine related findings (e.g., multiple vulnerabilities in same base image)
   - Provide accurate final counts

**Required JSON Response Format:**
{{
    "total_findings": 2,
    "critical_count": 1,
    "high_count": 1,
    "medium_count": 0,
    "low_count": 0,
    "findings": [
        {{
            "id": "BASE_IMAGE_RESULT",
            "title": "Critical: End-of-Life Base Image",
            "severity": "CRITICAL",
            "description": "The result component uses node:10-slim base image which is past End-of-Life and contains numerous unpatched vulnerabilities",
            "file_path": "result/Dockerfile",
            "line_number": 1,
            "recommendation": "Update to node:18-slim or node:20-slim immediately",
            "confidence": 0.95,
            "reasoning": "Base image version is verifiable and EOL status is confirmed"
        }}
    ],
    "priority_recommendation": "CRITICAL: Update the node:10-slim base image in the result component immediately - this is the highest priority security risk.",
    "summary": "Security analysis identified 2 findings: 1 critical End-of-Life base image requiring immediate attention, and 1 potential issue requiring validation.",
    "confidence_notes": [
        "Base image vulnerabilities are verified and actionable",
        "Generic pattern matches require manual validation"
    ]
}}

**Critical Instructions:**
- Your final count must match the number of findings in your "findings" array
- Focus on actionable, specific risks over generic patterns
- Provide clear, immediate next steps in recommendations
- Only include findings that can be acted upon by developers"""
    
    def _parse_synthesis_response(self, response_text: str) -> SecuritySynthesis:
        """Parse LLM response into SecuritySynthesis"""
        
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Parse findings
                findings = []
                for finding_data in data.get('findings', []):
                    finding = SynthesizedSecurityFinding(
                        id=finding_data.get('id', 'unknown'),
                        title=finding_data.get('title', 'Unknown'),
                        severity=finding_data.get('severity', 'UNKNOWN'),
                        description=finding_data.get('description', ''),
                        file_path=finding_data.get('file_path'),
                        line_number=finding_data.get('line_number'),
                        recommendation=finding_data.get('recommendation', ''),
                        confidence=finding_data.get('confidence', 0.0),
                        reasoning=finding_data.get('reasoning', '')
                    )
                    findings.append(finding)
                
                return SecuritySynthesis(
                    total_findings=data.get('total_findings', 0),
                    critical_count=data.get('critical_count', 0),
                    high_count=data.get('high_count', 0),
                    medium_count=data.get('medium_count', 0),
                    low_count=data.get('low_count', 0),
                    findings=findings,
                    priority_recommendation=data.get('priority_recommendation', ''),
                    summary=data.get('summary', ''),
                    confidence_notes=data.get('confidence_notes', [])
                )
            
        except json.JSONDecodeError as e:
            print(f"WARNING [LLM-SECURITY] Error parsing JSON: {e}")
        except Exception as e:
            print(f"WARNING [LLM-SECURITY] Error parsing response: {e}")
        
        # Fallback parsing
        return self._fallback_parse(response_text)
    
    def _fallback_parse(self, response_text: str) -> SecuritySynthesis:
        """Fallback parsing when JSON parsing fails"""
        
        text_lower = response_text.lower()
        
        # Extract basic info from text
        critical_count = text_lower.count('critical')
        high_count = text_lower.count('high')
        total_findings = critical_count + high_count
        
        return SecuritySynthesis(
            total_findings=total_findings,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=0,
            low_count=0,
            findings=[],
            priority_recommendation="Review security findings and prioritize based on severity",
            summary=f"Found {total_findings} security findings requiring attention",
            confidence_notes=["Fallback parsing - manual review recommended"]
        )
    
    def _fallback_synthesis(self, 
                          vulnerability_findings: List[Any],
                          base_image_risks: List[Dict[str, Any]],
                          manual_findings: List[Any]) -> SecuritySynthesis:
        """Fallback synthesis when LLM is not available"""
        
        all_findings = []
        
        # Process base image risks (highest priority)
        for risk in base_image_risks:
            if risk.get('risk_level') in ['HIGH', 'CRITICAL']:
                finding = SynthesizedSecurityFinding(
                    id=f"BASE_IMAGE_{risk.get('component', 'unknown')}",
                    title=f"Vulnerable Base Image: {risk.get('base_image', 'unknown')}",
                    severity=risk.get('risk_level', 'HIGH'),
                    description=risk.get('description', ''),
                    file_path=f"{risk.get('component', 'unknown')}/Dockerfile",
                    line_number=1,
                    recommendation=risk.get('recommendation', ''),
                    confidence=0.9,
                    reasoning="Base image vulnerability verified"
                )
                all_findings.append(finding)
        
        # Count by severity
        critical_count = sum(1 for f in all_findings if f.severity == 'CRITICAL')
        high_count = sum(1 for f in all_findings if f.severity == 'HIGH')
        
        return SecuritySynthesis(
            total_findings=len(all_findings),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=0,
            low_count=0,
            findings=all_findings,
            priority_recommendation="Update vulnerable base images to supported versions",
            summary=f"Security analysis identified {len(all_findings)} findings requiring attention",
            confidence_notes=["Rule-based synthesis - LLM analysis recommended for better accuracy"]
        )