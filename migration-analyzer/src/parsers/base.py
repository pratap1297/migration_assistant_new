"""
Base parser interface for extensible parser system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ParseResult:
    """Standard result from any parser"""
    parser_type: str
    file_path: str
    success: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class AbstractParser(ABC):
    """Base class for all parsers in the system"""
    
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file"""
        pass
    
    @abstractmethod
    def parse(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """Parse the file and return structured data"""
        pass
    
    @abstractmethod
    def get_parser_type(self) -> str:
        """Return the type of parser (e.g., 'dockerfile', 'compose', 'github-actions')"""
        pass
    
    def read_file(self, file_path: Path) -> str:
        """Helper to read file content"""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {str(e)}")