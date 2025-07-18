import re
try:
    import javalang
    JAVALANG_AVAILABLE = True
except ImportError:
    JAVALANG_AVAILABLE = False

from typing import List
from src.semantic.base_parser import LanguageParser
from src.core.models import *

class JavaParser(LanguageParser):
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.java']
    
    def parse(self, file_content: str, file_path: str) -> SemanticCodeMap:
        code_map = SemanticCodeMap(
            file_path=file_path,
            language="java"
        )
        
        try:
            if JAVALANG_AVAILABLE:
                tree = javalang.parse.parse(file_content)
                self._extract_classes_and_methods(tree, code_map)
            else:
                code_map.notes.append("javalang not available, using regex fallback")
                self._extract_classes_regex(file_content, code_map)
                
            self._extract_spring_endpoints(file_content, code_map)
            self._extract_database_operations(file_content, code_map)
            self._extract_http_calls(file_content, code_map)
        except Exception as e:
            code_map.notes.append(f"Error parsing Java: {str(e)}")
        
        return code_map
    
    def _extract_classes_and_methods(self, tree, code_map: SemanticCodeMap):
        if not JAVALANG_AVAILABLE:
            return
            
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_info = ClassInfo(
                name=node.name,
                start_line=node.position.line if node.position else 0,
                end_line=0,  # javalang doesn't provide end line
                methods=[],
                base_classes=[]
            )
            
            # Extract methods
            for method in node.methods:
                class_info.methods.append(method.name)
                
                # Create function info for each method
                func_info = FunctionInfo(
                    name=f"{node.name}.{method.name}",
                    start_line=method.position.line if method.position else 0,
                    end_line=0
                )
                code_map.functions.append(func_info)
            
            code_map.classes.append(class_info)
    
    def _extract_classes_regex(self, content: str, code_map: SemanticCodeMap):
        # Fallback regex-based class extraction
        class_pattern = r'(?:public\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            base_class = match.group(2) if match.group(2) else None
            line_num = content[:match.start()].count('\n') + 1
            
            class_info = ClassInfo(
                name=class_name,
                start_line=line_num,
                end_line=line_num,
                methods=[],
                base_classes=[base_class] if base_class else []
            )
            code_map.classes.append(class_info)
    
    def _extract_spring_endpoints(self, content: str, code_map: SemanticCodeMap):
        # Spring REST patterns
        patterns = [
            (r'@GetMapping\s*\(\s*["\']([^"\']+)["\']\s*\)', 'GET'),
            (r'@PostMapping\s*\(\s*["\']([^"\']+)["\']\s*\)', 'POST'),
            (r'@PutMapping\s*\(\s*["\']([^"\']+)["\']\s*\)', 'PUT'),
            (r'@DeleteMapping\s*\(\s*["\']([^"\']+)["\']\s*\)', 'DELETE'),
            (r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']\s*\)', 'GET'),
        ]
        
        for pattern, method in patterns:
            for match in re.finditer(pattern, content):
                path = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                endpoint = ApiEndpoint(
                    path=path,
                    methods=[method],
                    handler_function="",
                    line_number=line_num
                )
                code_map.api_endpoints.append(endpoint)
    
    def _extract_database_operations(self, content: str, code_map: SemanticCodeMap):
        # JDBC patterns
        jdbc_patterns = [
            r'prepareStatement\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'executeQuery\s*\(\s*["\']([^"\']+)["\']\s*\)',
            r'executeUpdate\s*\(\s*["\']([^"\']+)["\']\s*\)',
        ]
        
        for pattern in jdbc_patterns:
            for match in re.finditer(pattern, content):
                query = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                # Extract operation type
                operation = "UNKNOWN"
                if query:
                    first_word = query.strip().split()[0].upper()
                    if first_word in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']:
                        operation = first_word
                
                db_interaction = DatabaseInteraction(
                    operation=operation,
                    line_number=line_num,
                    raw_query=query[:100]
                )
                code_map.database_interactions.append(db_interaction)
        
        # Redis/Jedis patterns
        redis_patterns = [
            r'jedis\.\w+\s*\(',
            r'redis\.\w+\s*\(',
        ]
        
        for pattern in redis_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                db_interaction = DatabaseInteraction(
                    operation='REDIS_OP',
                    line_number=line_num
                )
                code_map.database_interactions.append(db_interaction)
    
    def _extract_http_calls(self, content: str, code_map: SemanticCodeMap):
        # HttpClient patterns
        patterns = [
            (r'HttpGet\s*\(\s*["\']([^"\']+)["\']\s*\)', 'GET'),
            (r'HttpPost\s*\(\s*["\']([^"\']+)["\']\s*\)', 'POST'),
            (r'\.get\s*\(\s*["\']([^"\']+)["\']\s*\)', 'GET'),
            (r'\.post\s*\(\s*["\']([^"\']+)["\']\s*\)', 'POST'),
        ]
        
        for pattern, method in patterns:
            for match in re.finditer(pattern, content):
                url = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                http_call = HttpCall(
                    url=url,
                    method=method,
                    line_number=line_num
                )
                code_map.outbound_http_calls.append(http_call)