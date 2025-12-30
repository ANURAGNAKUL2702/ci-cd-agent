"""
Unit tests for the YAMLValidator module
"""
import pytest
from modules.yaml_validator import YAMLValidator


class TestYAMLValidator:
    """Test cases for YAMLValidator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.validator = YAMLValidator()
    
    def test_validate_valid_yaml(self):
        """Test validating valid YAML"""
        yaml_content = """
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""
        is_valid, data, issues = self.validator.validate_yaml_syntax(yaml_content)
        assert is_valid is True
        assert data is not None
        assert len(issues) == 0
    
    def test_validate_invalid_yaml(self):
        """Test validating invalid YAML"""
        yaml_content = """
on:
  push
    branches: [main]
"""
        is_valid, data, issues = self.validator.validate_yaml_syntax(yaml_content)
        assert is_valid is False
        assert data is None
        assert len(issues) > 0
    
    def test_validate_workflow_structure_valid(self):
        """Test validating valid workflow structure"""
        yaml_data = {
            "on": {"push": {"branches": ["main"]}},
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": "actions/checkout@v4"}]
                }
            }
        }
        is_valid, issues = self.validator.validate_workflow_structure(yaml_data)
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_workflow_structure_missing_on(self):
        """Test validating workflow missing 'on' field"""
        yaml_data = {
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest"
                }
            }
        }
        is_valid, issues = self.validator.validate_workflow_structure(yaml_data)
        assert is_valid is False
        assert any("on" in issue for issue in issues)
    
    def test_validate_workflow_structure_missing_runs_on(self):
        """Test validating workflow missing 'runs-on' in job"""
        yaml_data = {
            "on": {"push": {}},
            "jobs": {
                "build": {
                    "steps": []
                }
            }
        }
        is_valid, issues = self.validator.validate_workflow_structure(yaml_data)
        assert is_valid is False
        assert any("runs-on" in issue for issue in issues)
    
    def test_detect_deprecated_actions(self):
        """Test detecting deprecated actions"""
        yaml_content = """
steps:
  - uses: actions/checkout@v2
  - uses: actions/setup-python@v3
"""
        deprecated = self.validator.detect_deprecated_actions(yaml_content)
        assert len(deprecated) == 2
        assert any("checkout@v2" in d["deprecated"] for d in deprecated)
        assert any("setup-python@v3" in d["deprecated"] for d in deprecated)
    
    def test_replace_deprecated_actions(self):
        """Test replacing deprecated actions"""
        yaml_content = "uses: actions/checkout@v2"
        updated, count = self.validator.replace_deprecated_actions(yaml_content)
        assert count == 1
        assert "checkout@v4" in updated
        assert "checkout@v2" not in updated
    
    def test_add_missing_required_fields(self):
        """Test adding missing required fields"""
        yaml_data = {}
        updated_data, changes = self.validator.add_missing_required_fields(yaml_data)
        assert "on" in updated_data
        assert "jobs" in updated_data
        assert len(changes) > 0
    
    def test_validate_and_fix_complete_workflow(self):
        """Test complete validation and fix workflow"""
        yaml_content = """
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
"""
        result = self.validator.validate_and_fix(yaml_content)
        assert result["original_valid"] is True
        assert result["fixed_valid"] is True
        assert len(result["deprecated_actions"]) > 0
        assert "checkout@v4" in result["fixed_content"]
