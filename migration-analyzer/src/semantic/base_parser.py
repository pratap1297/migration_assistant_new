from abc import ABC, abstractmethod
from typing import List
from src.core.models import SemanticCodeMap

class LanguageParser(ABC):
    """Abstract base class for language-specific parsers"""
    
    @abstractmethod
    def parse(self, file_content: str, file_path: str) -> SemanticCodeMap:
        """Parse source code and extract semantic information"""
        pass
    
    @abstractmethod
    def can_parse(self, file_extension: str) -> bool:
        """Check if this parser can handle the given file extension"""
        pass
    
    def extract_imports(self, content: str) -> List[str]:
        """Extract import statements - can be overridden"""
        return []