"""
Unit tests for the Reporter module
"""
import pytest
from modules.reporter import Reporter


class TestReporter:
    """Test cases for Reporter"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.reporter = Reporter()
    
    def test_generate_analysis_report(self):
        """Test generating analysis report"""
        workflow_info = {
            "name": "CI Pipeline",
            "id": 12345,
            "status": "completed",
            "conclusion": "failure",
            "head_branch": "main",
            "head_sha": "abc123def456"
        }
        
        log_analysis = {
            "categories": ["missing_dependency", "test_failure"],
            "errors": [
                {"line_number": 10, "category": "missing_dependency", "line_content": "ModuleNotFoundError"},
                {"line_number": 20, "category": "test_failure", "line_content": "FAILED test"}
            ]
        }
        
        fix_report = {
            "total_errors": 2,
            "auto_fixable_count": 1,
            "manual_review_count": 1,
            "fixes": {
                "missing_dependency": {
                    "description": "Missing dependency",
                    "suggestions": ["Add to requirements.txt"],
                    "auto_fixable": True
                }
            }
        }
        
        report = self.reporter.generate_analysis_report(workflow_info, log_analysis, fix_report)
        assert "CI/CD Pipeline Analysis Report" in report
        assert "CI Pipeline" in report
        assert "12345" in report
        assert "missing_dependency" in report
    
    def test_generate_yaml_validation_report(self):
        """Test generating YAML validation report"""
        validation_result = {
            "original_valid": False,
            "fixed_valid": True,
            "issues": ["Missing required field: 'on'"],
            "deprecated_actions": [
                {
                    "deprecated": "actions/checkout@v2",
                    "replacement": "actions/checkout@v4",
                    "message": "Use v4"
                }
            ],
            "fixes_applied": ["Fixed indentation", "Replaced deprecated actions"]
        }
        
        report = self.reporter.generate_yaml_validation_report(validation_result)
        assert "YAML Validation Report" in report
        assert "Issues Found" in report
        assert "Deprecated Actions" in report
        assert "checkout@v2" in report
        assert "checkout@v4" in report
    
    def test_generate_pr_description(self):
        """Test generating PR description"""
        workflow_info = {
            "name": "CI Pipeline",
            "id": 12345,
            "head_branch": "main"
        }
        
        fixes_applied = [
            "Updated deprecated actions",
            "Fixed YAML indentation"
        ]
        
        validation_result = {
            "deprecated_actions": [
                {
                    "deprecated": "actions/checkout@v2",
                    "replacement": "actions/checkout@v4"
                }
            ]
        }
        
        pr_desc = self.reporter.generate_pr_description(workflow_info, fixes_applied, validation_result)
        assert "Automated CI/CD Pipeline Fix" in pr_desc
        assert "CI Pipeline" in pr_desc
        assert "Updated deprecated actions" in pr_desc
        assert "checkout@v4" in pr_desc
    
    def test_generate_pr_description_no_fixes(self):
        """Test generating PR description with no fixes"""
        workflow_info = {"name": "Test", "id": 1, "head_branch": "main"}
        pr_desc = self.reporter.generate_pr_description(workflow_info, [])
        assert "No automatic fixes were applied" in pr_desc
    
    def test_generate_issue_description(self):
        """Test generating issue description"""
        workflow_info = {
            "name": "CI Pipeline",
            "id": 12345,
            "status": "failure",
            "html_url": "https://github.com/test"
        }
        
        log_analysis = {
            "categories": ["permission_error"]
        }
        
        fix_report = {
            "total_errors": 1,
            "manual_review_count": 1,
            "fixes": {
                "permission_error": {
                    "description": "Permission denied",
                    "suggestions": ["Check permissions"],
                    "auto_fixable": False
                }
            }
        }
        
        issue_desc = self.reporter.generate_issue_description(workflow_info, log_analysis, fix_report)
        assert "CI/CD Pipeline Failure Detected" in issue_desc
        assert "CI Pipeline" in issue_desc
        assert "Manual Review" in issue_desc
        assert "permission" in issue_desc.lower()
