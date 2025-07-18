#!/usr/bin/env python3
"""
Centralized LLM Configuration
Handles API key loading, model selection, and initialization for all LLM components
"""

import os
from typing import Optional, Any
from pathlib import Path

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    print(f"WARNING [LLM-CONFIG] Google Generative AI not available: {e}")
    print("    Install with: pip install google-generativeai")
    GEMINI_AVAILABLE = False
    genai = None

class LLMConfig:
    """Centralized LLM configuration and management"""
    
    # Default model configuration
    DEFAULT_MODEL = "gemini-2.5-flash-lite-preview-06-17"
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize LLM configuration
        
        Args:
            model_name: Override default model name
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.api_key = None
        self.llm = None
        self.available = False
        
        # Load API key and initialize
        self._load_api_key()
        self._initialize_llm()
    
    def _load_api_key(self) -> None:
        """Load API key from environment or .env file"""
        # First try environment variable
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            # Try to load from .env file in project root
            env_file = self._find_env_file()
            if env_file and env_file.exists():
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('GEMINI_API_KEY='):
                                self.api_key = line.split('=', 1)[1].strip()
                                # Remove quotes if present
                                if self.api_key.startswith('"') and self.api_key.endswith('"'):
                                    self.api_key = self.api_key[1:-1]
                                elif self.api_key.startswith("'") and self.api_key.endswith("'"):
                                    self.api_key = self.api_key[1:-1]
                                break
                    
                    if self.api_key:
                        print(f"OK [LLM-CONFIG] API key loaded from {env_file}")
                        # Set environment variable for other processes
                        os.environ['GEMINI_API_KEY'] = self.api_key
                except Exception as e:
                    print(f"WARNING [LLM-CONFIG] Error reading .env file: {e}")
        
        if not self.api_key:
            print("WARNING [LLM-CONFIG] No GEMINI_API_KEY found in environment or .env file")
    
    def _find_env_file(self) -> Optional[Path]:
        """Find .env file in project hierarchy"""
        current_dir = Path(__file__).parent
        
        # Look for .env file going up the directory tree
        for _ in range(5):  # Limit search depth
            env_file = current_dir / '.env'
            if env_file.exists():
                return env_file
            current_dir = current_dir.parent
        
        return None
    
    def _initialize_llm(self) -> None:
        """Initialize LLM with API key and model"""
        if not GEMINI_AVAILABLE:
            print("WARNING [LLM-CONFIG] Google Generative AI not available")
            return
        
        if not self.api_key:
            print("WARNING [LLM-CONFIG] No API key - LLM features disabled")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.llm = genai.GenerativeModel(self.model_name)
            self.available = True
            print(f"OK [LLM-CONFIG] Initialized {self.model_name} successfully")
        except Exception as e:
            print(f"ERROR [LLM-CONFIG] Failed to initialize LLM: {e}")
            self.available = False
    
    def get_model(self) -> Optional[Any]:
        """Get initialized LLM model"""
        return self.llm if self.available else None
    
    def is_available(self) -> bool:
        """Check if LLM is available and configured"""
        return self.available
    
    def get_api_key(self) -> Optional[str]:
        """Get API key (for backward compatibility)"""
        return self.api_key
    
    def generate_content(self, prompt: str, **kwargs) -> Optional[Any]:
        """Generate content using the LLM"""
        if not self.available:
            return None
        
        try:
            return self.llm.generate_content(prompt, **kwargs)
        except Exception as e:
            print(f"ERROR [LLM-CONFIG] Content generation failed: {e}")
            return None
    
    def create_model_instance(self, model_name: Optional[str] = None) -> Optional[Any]:
        """Create a new model instance with different model name"""
        if not GEMINI_AVAILABLE or not self.api_key:
            return None
        
        try:
            model = model_name or self.model_name
            return genai.GenerativeModel(model)
        except Exception as e:
            print(f"ERROR [LLM-CONFIG] Failed to create model {model}: {e}")
            return None

# Global LLM configuration instance
_llm_config = None

def get_llm_config() -> LLMConfig:
    """Get global LLM configuration instance"""
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config

def get_llm_model() -> Optional[Any]:
    """Get configured LLM model"""
    return get_llm_config().get_model()

def is_llm_available() -> bool:
    """Check if LLM is available"""
    return get_llm_config().is_available()

def get_api_key() -> Optional[str]:
    """Get API key"""
    return get_llm_config().get_api_key()

def generate_content(prompt: str, **kwargs) -> Optional[Any]:
    """Generate content using configured LLM"""
    return get_llm_config().generate_content(prompt, **kwargs)

# Model-specific convenience functions
def get_classification_model() -> Optional[Any]:
    """Get model optimized for classification tasks"""
    return get_llm_config().create_model_instance()

def get_security_model() -> Optional[Any]:
    """Get model optimized for security analysis"""
    return get_llm_config().create_model_instance()

def get_narrative_model() -> Optional[Any]:
    """Get model optimized for narrative generation"""
    return get_llm_config().create_model_instance()