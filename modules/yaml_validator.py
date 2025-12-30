"""
YAML Validation and Auto-fixing Module
Validates and fixes YAML syntax in GitHub Actions workflows
"""
import yaml
from typing import Dict, List, Optional, Tuple
from loguru import logger


class YAMLValidator:
    """Validates and fixes YAML syntax in workflow files"""
    
    # Common deprecated actions and their replacements
    DEPRECATED_ACTIONS = {
        "actions/checkout@v1": "actions/checkout@v4",
        "actions/checkout@v2": "actions/checkout@v4",
        "actions/checkout@v3": "actions/checkout@v4",
        "actions/setup-python@v1": "actions/setup-python@v5",
        "actions/setup-python@v2": "actions/setup-python@v5",
        "actions/setup-python@v3": "actions/setup-python@v5",
        "actions/setup-python@v4": "actions/setup-python@v5",
        "actions/setup-node@v1": "actions/setup-node@v4",
        "actions/setup-node@v2": "actions/setup-node@v4",
        "actions/setup-node@v3": "actions/setup-node@v4",
        "actions/cache@v1": "actions/cache@v4",
        "actions/cache@v2": "actions/cache@v4",
        "actions/cache@v3": "actions/cache@v4",
    }
    
    # Required fields for GitHub Actions workflow
    REQUIRED_WORKFLOW_FIELDS = ["on", "jobs"]
    REQUIRED_JOB_FIELDS = ["runs-on"]
    
    def __init__(self):
        self.issues = []
    
    def validate_yaml_syntax(self, yaml_content: str) -> Tuple[bool, Optional[Dict], List[str]]:
        """
        Validate YAML syntax
        
        Args:
            yaml_content: The YAML content as string
            
        Returns:
            Tuple of (is_valid, parsed_data, list of issues)
        """
        self.issues = []
        
        try:
            data = yaml.safe_load(yaml_content)
            logger.info("YAML syntax is valid")
            return True, data, []
        except yaml.YAMLError as e:
            error_msg = str(e)
            self.issues.append(f"YAML syntax error: {error_msg}")
            logger.error(f"YAML syntax error: {error_msg}")
            return False, None, self.issues
    
    def validate_workflow_structure(self, yaml_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate GitHub Actions workflow structure
        
        Args:
            yaml_data: Parsed YAML data as dictionary
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check required workflow fields
        for field in self.REQUIRED_WORKFLOW_FIELDS:
            if field not in yaml_data:
                issues.append(f"Missing required field: '{field}'")
        
        # Validate jobs structure
        if "jobs" in yaml_data:
            for job_name, job_data in yaml_data["jobs"].items():
                if not isinstance(job_data, dict):
                    issues.append(f"Job '{job_name}' is not a valid dictionary")
                    continue
                
                # Check required job fields
                for field in self.REQUIRED_JOB_FIELDS:
                    if field not in job_data:
                        issues.append(f"Job '{job_name}' missing required field: '{field}'")
                
                # Validate steps if present
                if "steps" in job_data:
                    if not isinstance(job_data["steps"], list):
                        issues.append(f"Job '{job_name}': 'steps' must be a list")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info("Workflow structure is valid")
        else:
            logger.warning(f"Workflow structure has {len(issues)} issue(s)")
        
        return is_valid, issues
    
    def detect_deprecated_actions(self, yaml_content: str) -> List[Dict[str, str]]:
        """
        Detect deprecated GitHub Actions
        
        Args:
            yaml_content: The YAML content as string
            
        Returns:
            List of dictionaries with deprecated actions and their replacements
        """
        deprecated = []
        
        for old_action, new_action in self.DEPRECATED_ACTIONS.items():
            if old_action in yaml_content:
                deprecated.append({
                    "deprecated": old_action,
                    "replacement": new_action,
                    "message": f"Action '{old_action}' is deprecated. Use '{new_action}' instead."
                })
        
        if deprecated:
            logger.info(f"Found {len(deprecated)} deprecated action(s)")
        
        return deprecated
    
    def fix_indentation(self, yaml_content: str) -> str:
        """
        Attempt to fix common indentation issues
        
        Args:
            yaml_content: The YAML content as string
            
        Returns:
            Fixed YAML content
        """
        try:
            # Try to parse and re-dump with proper indentation
            data = yaml.safe_load(yaml_content)
            fixed_content = yaml.dump(data, default_flow_style=False, sort_keys=False, indent=2)
            logger.info("Fixed YAML indentation")
            return fixed_content
        except yaml.YAMLError:
            logger.warning("Could not auto-fix indentation due to syntax errors")
            return yaml_content
    
    def replace_deprecated_actions(self, yaml_content: str) -> Tuple[str, int]:
        """
        Replace deprecated actions with newer versions
        
        Args:
            yaml_content: The YAML content as string
            
        Returns:
            Tuple of (updated_content, number of replacements)
        """
        updated_content = yaml_content
        replacement_count = 0
        
        for old_action, new_action in self.DEPRECATED_ACTIONS.items():
            if old_action in updated_content:
                updated_content = updated_content.replace(old_action, new_action)
                replacement_count += 1
                logger.info(f"Replaced '{old_action}' with '{new_action}'")
        
        return updated_content, replacement_count
    
    def add_missing_required_fields(self, yaml_data: Dict) -> Tuple[Dict, List[str]]:
        """
        Add missing required fields with default values
        
        Args:
            yaml_data: Parsed YAML data as dictionary
            
        Returns:
            Tuple of (updated_data, list of changes made)
        """
        changes = []
        
        # Add missing 'on' field with default value
        if "on" not in yaml_data:
            yaml_data["on"] = {"push": {"branches": ["main"]}}
            changes.append("Added default 'on' trigger (push to main)")
        
        # Add missing 'jobs' field
        if "jobs" not in yaml_data:
            yaml_data["jobs"] = {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": "actions/checkout@v4"}]
                }
            }
            changes.append("Added default 'jobs' section")
        
        # Fix jobs missing 'runs-on'
        if "jobs" in yaml_data and isinstance(yaml_data["jobs"], dict):
            for job_name, job_data in yaml_data["jobs"].items():
                if isinstance(job_data, dict) and "runs-on" not in job_data:
                    job_data["runs-on"] = "ubuntu-latest"
                    changes.append(f"Added default 'runs-on' to job '{job_name}'")
        
        if changes:
            logger.info(f"Made {len(changes)} structural fix(es)")
        
        return yaml_data, changes
    
    def validate_and_fix(self, yaml_content: str) -> Dict[str, any]:
        """
        Complete validation and auto-fix workflow
        
        Args:
            yaml_content: The YAML content as string
            
        Returns:
            Dictionary with validation results and fixed content
        """
        result = {
            "original_valid": False,
            "fixed_valid": False,
            "issues": [],
            "deprecated_actions": [],
            "fixes_applied": [],
            "original_content": yaml_content,
            "fixed_content": yaml_content
        }
        
        # Step 1: Validate original syntax
        is_valid, data, syntax_issues = self.validate_yaml_syntax(yaml_content)
        result["original_valid"] = is_valid
        result["issues"].extend(syntax_issues)
        
        # Step 2: Try to fix indentation if there are syntax errors
        if not is_valid:
            fixed_content = self.fix_indentation(yaml_content)
            is_valid, data, _ = self.validate_yaml_syntax(fixed_content)
            if is_valid:
                result["fixed_content"] = fixed_content
                result["fixes_applied"].append("Fixed YAML indentation")
        
        # Step 3: Validate structure if syntax is valid
        if is_valid and data:
            struct_valid, struct_issues = self.validate_workflow_structure(data)
            result["issues"].extend(struct_issues)
            
            # Try to fix structural issues
            if not struct_valid:
                fixed_data, changes = self.add_missing_required_fields(data)
                result["fixed_content"] = yaml.dump(fixed_data, default_flow_style=False, sort_keys=False, indent=2)
                result["fixes_applied"].extend(changes)
        
        # Step 4: Detect and replace deprecated actions
        deprecated = self.detect_deprecated_actions(result["fixed_content"])
        result["deprecated_actions"] = deprecated
        
        if deprecated:
            updated_content, count = self.replace_deprecated_actions(result["fixed_content"])
            result["fixed_content"] = updated_content
            result["fixes_applied"].append(f"Replaced {count} deprecated action(s)")
        
        # Final validation
        is_valid, _, _ = self.validate_yaml_syntax(result["fixed_content"])
        result["fixed_valid"] = is_valid
        
        return result
