import re
try:
    import esprima
    ESPRIMA_AVAILABLE = True
except ImportError:
    ESPRIMA_AVAILABLE = False

from typing import List
from src.semantic.base_parser import LanguageParser
from src.core.models import *

class JavaScriptParser(LanguageParser):
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.js', '.jsx', '.ts', '.tsx']
    
    def parse(self, file_content: str, file_path: str) -> SemanticCodeMap:
        code_map = SemanticCodeMap(
            file_path=file_path,
            language="javascript"
        )
        
        try:
            # Use regex for patterns esprima might miss
            self._extract_express_routes(file_content, code_map)
            self._extract_database_operations(file_content, code_map)
            self._extract_http_calls(file_content, code_map)
            
            # Try AST parsing for functions
            if ESPRIMA_AVAILABLE:
                try:
                    tree = esprima.parseScript(file_content, {'loc': True, 'range': True})
                    self._extract_functions_from_ast(tree, code_map)
                except:
                    # Fallback to regex if AST fails
                    self._extract_functions_regex(file_content, code_map)
            else:
                code_map.notes.append("esprima not available, using regex fallback")
                self._extract_functions_regex(file_content, code_map)
                
        except Exception as e:
            code_map.notes.append(f"Error parsing JavaScript: {str(e)}")
        
        return code_map
    
    def _extract_express_routes(self, content: str, code_map: SemanticCodeMap):
        # Express route patterns
        patterns = [
            (r'app\.get\s*\(\s*[\'"]([^\'"]+)[\'"]', 'GET'),
            (r'app\.post\s*\(\s*[\'"]([^\'"]+)[\'"]', 'POST'),
            (r'app\.put\s*\(\s*[\'"]([^\'"]+)[\'"]', 'PUT'),
            (r'app\.delete\s*\(\s*[\'"]([^\'"]+)[\'"]', 'DELETE'),
            (r'router\.get\s*\(\s*[\'"]([^\'"]+)[\'"]', 'GET'),
            (r'router\.post\s*\(\s*[\'"]([^\'"]+)[\'"]', 'POST'),
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
        # PostgreSQL client patterns
        pg_patterns = [
            r'client\.query\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'pool\.query\s*\(\s*[\'"]([^\'"]+)[\'"]',
        ]
        
        for pattern in pg_patterns:
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
        
        # MongoDB patterns
        mongo_patterns = [
            (r'\.find\s*\(', 'FIND'),
            (r'\.findOne\s*\(', 'FINDONE'),
            (r'\.insert\s*\(', 'INSERT'),
            (r'\.update\s*\(', 'UPDATE'),
            (r'\.delete\s*\(', 'DELETE'),
        ]
        
        for pattern, operation in mongo_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                db_interaction = DatabaseInteraction(
                    operation=f'MONGO_{operation}',
                    line_number=line_num
                )
                code_map.database_interactions.append(db_interaction)
    
    def _extract_http_calls(self, content: str, code_map: SemanticCodeMap):
        # Axios/fetch patterns
        patterns = [
            (r'axios\.get\s*\(\s*[\'"]([^\'"]+)[\'"]', 'GET'),
            (r'axios\.post\s*\(\s*[\'"]([^\'"]+)[\'"]', 'POST'),
            (r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]', 'GET'),
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
    
    def _extract_functions_from_ast(self, tree, code_map: SemanticCodeMap):
        # This would require more complex AST traversal with esprima
        # For now, fallback to regex
        self._extract_functions_regex("", code_map)
    
    def _extract_functions_regex(self, content: str, code_map: SemanticCodeMap):
        # Function patterns
        patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'const\s+(\w+)\s*=\s*async\s*\([^)]*\)\s*=>',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                func_info = FunctionInfo(
                    name=func_name,
                    start_line=line_num,
                    end_line=line_num  # Can't determine easily with regex
                )
                code_map.functions.append(func_info)