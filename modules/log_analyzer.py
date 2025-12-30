"""
Log Analysis Module for GitHub Actions Workflows
Parses logs and categorizes errors
"""
import re
from enum import Enum
from typing import Dict, List, Optional
from loguru import logger


class ErrorCategory(Enum):
    """Error categories for CI/CD pipeline issues"""
    YAML_SYNTAX_ERROR = "yaml_syntax_error"
    MISSING_DEPENDENCY = "missing_dependency"
    INVALID_ACTION = "invalid_action"
    DEPRECATED_ACTION = "deprecated_action"
    PERMISSION_ERROR = "permission_error"
    TIMEOUT_ERROR = "timeout_error"
    ENVIRONMENT_VARIABLE_MISSING = "environment_variable_missing"
    SECRET_MISSING = "secret_missing"
    VERSION_MISMATCH = "version_mismatch"
    BUILD_ERROR = "build_error"
    TEST_FAILURE = "test_failure"
    UNKNOWN = "unknown"


class ErrorPattern:
    """Patterns for identifying different error types"""
    
    PATTERNS = {
        ErrorCategory.YAML_SYNTAX_ERROR: [
            r"yaml.*syntax.*error",
            r"invalid.*yaml",
            r"could not find expected",
            r"mapping values are not allowed here",
        ],
        ErrorCategory.MISSING_DEPENDENCY: [
            r"ModuleNotFoundError",
            r"ImportError",
            r"No module named",
            r"cannot find package",
            r"package.*not found",
        ],
        ErrorCategory.INVALID_ACTION: [
            r"Unable to resolve action",
            r"Invalid action reference",
            r"action.*not found",
        ],
        ErrorCategory.DEPRECATED_ACTION: [
            r"deprecated",
            r"is deprecated",
            r"will be removed",
        ],
        ErrorCategory.PERMISSION_ERROR: [
            r"permission denied",
            r"Access denied",
            r"Forbidden",
            r"403",
        ],
        ErrorCategory.TIMEOUT_ERROR: [
            r"timeout",
            r"timed out",
            r"exceeded.*time",
        ],
        ErrorCategory.ENVIRONMENT_VARIABLE_MISSING: [
            r"environment variable.*not set",
            r"missing.*environment variable",
        ],
        ErrorCategory.SECRET_MISSING: [
            r"secret.*not found",
            r"missing.*secret",
        ],
        ErrorCategory.VERSION_MISMATCH: [
            r"version.*mismatch",
            r"incompatible.*version",
            r"requires.*version",
        ],
        ErrorCategory.BUILD_ERROR: [
            r"build.*failed",
            r"compilation.*error",
            r"failed.*to.*build",
        ],
        ErrorCategory.TEST_FAILURE: [
            r"test.*failed",
            r"assertion.*error",
            r"AssertionError",
            r"FAILED.*tests",
        ],
    }


class LogAnalyzer:
    """Analyzes workflow logs to identify and categorize errors"""
    
    def __init__(self):
        self.error_patterns = ErrorPattern.PATTERNS
    
    def analyze_log(self, log_content: str) -> Dict[str, any]:
        """
        Analyze log content and identify errors
        
        Args:
            log_content: The raw log content from workflow run
            
        Returns:
            Dictionary containing error analysis results
        """
        result = {
            "has_errors": False,
            "errors": [],
            "categories": set(),
            "summary": ""
        }
        
        if not log_content:
            logger.warning("Empty log content provided")
            result["summary"] = "No errors detected in the log"
            return result
        
        # Split log into lines for analysis
        log_lines = log_content.split('\n')
        
        # Analyze each line
        for line_num, line in enumerate(log_lines, 1):
            category = self._categorize_error(line)
            if category != ErrorCategory.UNKNOWN:
                result["has_errors"] = True
                result["errors"].append({
                    "line_number": line_num,
                    "line_content": line.strip(),
                    "category": category.value,
                })
                result["categories"].add(category.value)
        
        # Convert set to list for JSON serialization
        result["categories"] = list(result["categories"])
        
        # Generate summary
        if result["has_errors"]:
            result["summary"] = self._generate_summary(result["categories"], len(result["errors"]))
        else:
            result["summary"] = "No errors detected in the log"
        
        logger.info(f"Log analysis complete: {result['summary']}")
        return result
    
    def _categorize_error(self, line: str) -> ErrorCategory:
        """
        Categorize an error based on the line content
        
        Args:
            line: A single line from the log
            
        Returns:
            ErrorCategory enum value
        """
        line_lower = line.lower()
        
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    return category
        
        return ErrorCategory.UNKNOWN
    
    def _generate_summary(self, categories: List[str], error_count: int) -> str:
        """Generate a summary of detected errors"""
        if not categories:
            return "No specific errors categorized"
        
        category_str = ", ".join(categories)
        return f"Found {error_count} error(s) in categories: {category_str}"
    
    def extract_error_context(self, log_content: str, error_line: int, context_lines: int = 3) -> str:
        """
        Extract context around an error line
        
        Args:
            log_content: The raw log content
            error_line: The line number where error occurred
            context_lines: Number of lines before and after to include
            
        Returns:
            String containing the error context
        """
        lines = log_content.split('\n')
        start = max(0, error_line - context_lines - 1)
        end = min(len(lines), error_line + context_lines)
        
        context = lines[start:end]
        return '\n'.join(f"{i+start+1}: {line}" for i, line in enumerate(context))
