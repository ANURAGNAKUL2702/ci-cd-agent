"""
Unit tests for the ErrorFixer module
"""
import pytest
from modules.error_fixer import ErrorFixer
from modules.log_analyzer import ErrorCategory


class TestErrorFixer:
    """Test cases for ErrorFixer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.fixer = ErrorFixer()
    
    def test_get_fix_suggestions_missing_dependency(self):
        """Test getting fix suggestions for missing dependency"""
        suggestions = self.fixer.get_fix_suggestions("missing_dependency")
        assert suggestions["description"] is not None
        assert len(suggestions["suggestions"]) > 0
        assert suggestions["auto_fixable"] is True
    
    def test_get_fix_suggestions_yaml_error(self):
        """Test getting fix suggestions for YAML error"""
        suggestions = self.fixer.get_fix_suggestions("yaml_syntax_error")
        assert suggestions["description"] is not None
        assert suggestions["auto_fixable"] is True
    
    def test_get_fix_suggestions_permission_error(self):
        """Test getting fix suggestions for permission error"""
        suggestions = self.fixer.get_fix_suggestions("permission_error")
        assert suggestions["description"] is not None
        assert suggestions["auto_fixable"] is False
    
    def test_get_fix_suggestions_unknown_category(self):
        """Test getting fix suggestions for unknown category"""
        suggestions = self.fixer.get_fix_suggestions("unknown_error_type")
        assert "Unknown error type" in suggestions["description"]
        assert suggestions["auto_fixable"] is False
    
    def test_generate_fix_report(self):
        """Test generating a fix report"""
        analysis_result = {
            "errors": [
                {"category": "missing_dependency"},
                {"category": "yaml_syntax_error"}
            ],
            "categories": ["missing_dependency", "yaml_syntax_error"]
        }
        
        report = self.fixer.generate_fix_report(analysis_result)
        assert report["total_errors"] == 2
        assert len(report["categories"]) == 2
        assert "missing_dependency" in report["fixes"]
        assert "yaml_syntax_error" in report["fixes"]
        assert report["auto_fixable_count"] == 2
        assert report["manual_review_count"] == 0
    
    def test_suggest_dependency_fix(self):
        """Test suggesting dependency fix"""
        fix = self.fixer.suggest_dependency_fix("requests")
        assert "requests" in fix
        assert "requirements.txt" in fix
    
    def test_suggest_timeout_fix(self):
        """Test suggesting timeout fix"""
        fix = self.fixer.suggest_timeout_fix(15)
        assert "30" in fix  # Should suggest double the current timeout
        assert "timeout-minutes" in fix
    
    def test_suggest_timeout_fix_no_current(self):
        """Test suggesting timeout fix without current value"""
        fix = self.fixer.suggest_timeout_fix()
        assert "timeout-minutes" in fix
    
    def test_suggest_permission_fix(self):
        """Test suggesting permission fix"""
        fix = self.fixer.suggest_permission_fix()
        assert "permissions" in fix
        assert "contents" in fix
    
    def test_generate_workflow_fix_timeout(self):
        """Test generating workflow fix for timeout"""
        fix = self.fixer.generate_workflow_fix("timeout_error")
        assert fix is not None
        assert "timeout-minutes" in fix
    
    def test_generate_workflow_fix_permission(self):
        """Test generating workflow fix for permission error"""
        fix = self.fixer.generate_workflow_fix("permission_error")
        assert fix is not None
        assert "permissions" in fix
    
    def test_generate_workflow_fix_unknown(self):
        """Test generating workflow fix for unknown error"""
        fix = self.fixer.generate_workflow_fix("unknown_error")
        assert fix is None
