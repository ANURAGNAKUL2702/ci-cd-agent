"""
Unit tests for the LogAnalyzer module
"""
import pytest
from modules.log_analyzer import LogAnalyzer, ErrorCategory


class TestLogAnalyzer:
    """Test cases for LogAnalyzer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = LogAnalyzer()
    
    def test_analyze_empty_log(self):
        """Test analyzing empty log content"""
        result = self.analyzer.analyze_log("")
        assert result["has_errors"] is False
        assert len(result["errors"]) == 0
        assert result["summary"] == "No errors detected in the log"
    
    def test_analyze_log_with_missing_dependency(self):
        """Test detecting missing dependency errors"""
        log_content = """
Error: ModuleNotFoundError: No module named 'requests'
ImportError: cannot import name 'Flask'
"""
        result = self.analyzer.analyze_log(log_content)
        assert result["has_errors"] is True
        assert "missing_dependency" in result["categories"]
        assert len(result["errors"]) >= 2
    
    def test_analyze_log_with_yaml_error(self):
        """Test detecting YAML syntax errors"""
        log_content = """
Error: YAML syntax error on line 10
Invalid YAML: mapping values are not allowed here
"""
        result = self.analyzer.analyze_log(log_content)
        assert result["has_errors"] is True
        assert "yaml_syntax_error" in result["categories"]
    
    def test_analyze_log_with_test_failure(self):
        """Test detecting test failures"""
        log_content = """
FAILED tests/test_example.py::test_fail
AssertionError: Expected True but got False
"""
        result = self.analyzer.analyze_log(log_content)
        assert result["has_errors"] is True
        assert "test_failure" in result["categories"]
    
    def test_analyze_log_with_timeout(self):
        """Test detecting timeout errors"""
        log_content = """
Error: Job timed out after 60 minutes
The operation has exceeded the time limit
"""
        result = self.analyzer.analyze_log(log_content)
        assert result["has_errors"] is True
        assert "timeout_error" in result["categories"]
    
    def test_analyze_log_with_permission_error(self):
        """Test detecting permission errors"""
        log_content = """
Error: Permission denied
Access denied - 403 Forbidden
"""
        result = self.analyzer.analyze_log(log_content)
        assert result["has_errors"] is True
        assert "permission_error" in result["categories"]
    
    def test_categorize_error_unknown(self):
        """Test that unknown errors are categorized correctly"""
        result = self.analyzer._categorize_error("Some random log line")
        assert result == ErrorCategory.UNKNOWN
    
    def test_extract_error_context(self):
        """Test extracting context around an error"""
        log_content = """Line 1
Line 2
Error: Something went wrong
Line 4
Line 5"""
        context = self.analyzer.extract_error_context(log_content, 3, context_lines=1)
        assert "2: Line 2" in context
        assert "3: Error: Something went wrong" in context
        assert "4: Line 4" in context
    
    def test_generate_summary(self):
        """Test summary generation"""
        summary = self.analyzer._generate_summary(["missing_dependency", "yaml_syntax_error"], 5)
        assert "5 error(s)" in summary
        assert "missing_dependency" in summary
