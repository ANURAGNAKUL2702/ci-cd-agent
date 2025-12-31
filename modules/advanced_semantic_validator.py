"""
Advanced Semantic Validation for CI/CD Workflows
Deep analysis beyond basic YAML syntax checking
"""
import yaml
import re
import requests
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import semver
from packaging import version

class ValidationLevel(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    severity_score: int  # 0-100, higher is worse

class AdvancedSemanticValidator:
    """Production-grade semantic validation for GitHub Actions workflows"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.ADVANCED):
        self.validation_level = validation_level
        self.github_actions_registry = self._load_action_registry()
        self.runner_specifications = self._load_runner_specs()
        self.python_versions = self._get_supported_python_versions()
    
    def _load_action_registry(self) -> Dict[str, Dict]:
        """Load known GitHub Actions with their latest versions and specs"""
        return {
            "actions/checkout": {
                "latest_version": "v4",
                "supported_versions": ["v3", "v4"],
                "deprecated_versions": ["v1", "v2"],
                "required_inputs": [],
                "optional_inputs": ["repository", "ref", "token", "ssh-key", "ssh-known-hosts", "ssh-strict", "persist-credentials", "path", "clean", "fetch-depth", "lfs", "submodules", "set-safe-directory"]
            },
            "actions/setup-python": {
                "latest_version": "v5",
                "supported_versions": ["v4", "v5"],
                "deprecated_versions": ["v1", "v2", "v3"],
                "required_inputs": [],
                "optional_inputs": ["python-version", "python-version-file", "cache", "architecture", "check-latest", "token", "cache-dependency-path", "update-environment", "allow-prereleases"]
            },
            "actions/setup-node": {
                "latest_version": "v4",
                "supported_versions": ["v3", "v4"],
                "deprecated_versions": ["v1", "v2"],
                "required_inputs": [],
                "optional_inputs": ["always-auth", "node-version", "node-version-file", "architecture", "check-latest", "registry-url", "scope", "token", "cache", "cache-dependency-path"]
            },
            "actions/cache": {
                "latest_version": "v4",
                "supported_versions": ["v3", "v4"],
                "deprecated_versions": ["v1", "v2"],
                "required_inputs": ["key", "path"],
                "optional_inputs": ["restore-keys", "upload-chunk-size", "enableCrossOsArchive", "fail-on-cache-miss", "lookup-only"]
            },
            "actions/upload-artifact": {
                "latest_version": "v4",
                "supported_versions": ["v3", "v4"],
                "deprecated_versions": ["v1", "v2"],
                "required_inputs": ["name"],
                "optional_inputs": ["path", "if-no-files-found", "retention-days", "compression-level", "overwrite"]
            }
        }
    
    def _load_runner_specs(self) -> Dict[str, Dict]:
        """Load runner specifications and their capabilities"""
        return {
            "ubuntu-latest": {"alias_for": "ubuntu-22.04", "os": "linux", "arch": "x64"},
            "ubuntu-22.04": {"os": "linux", "arch": "x64", "supported": True},
            "ubuntu-20.04": {"os": "linux", "arch": "x64", "supported": True, "deprecated_soon": True},
            "ubuntu-18.04": {"os": "linux", "arch": "x64", "supported": False, "reason": "EOL"},
            "windows-latest": {"alias_for": "windows-2022", "os": "windows", "arch": "x64"},
            "windows-2022": {"os": "windows", "arch": "x64", "supported": True},
            "windows-2019": {"os": "windows", "arch": "x64", "supported": True, "deprecated_soon": True},
            "macos-latest": {"alias_for": "macos-14", "os": "macos", "arch": "arm64"},
            "macos-14": {"os": "macos", "arch": "arm64", "supported": True},
            "macos-13": {"os": "macos", "arch": "x64", "supported": True},
            "macos-12": {"os": "macos", "arch": "x64", "supported": True, "deprecated_soon": True},
            "macos-11": {"os": "macos", "arch": "x64", "supported": False, "reason": "EOL"}
        }
    
    def _get_supported_python_versions(self) -> List[str]:
        """Get currently supported Python versions"""
        return ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
    
    def validate_workflow(self, workflow_content: str, file_path: str = "") -> ValidationResult:
        """Comprehensive workflow validation"""
        errors = []
        warnings = []
        suggestions = []
        severity_score = 0
        
        try:
            # Parse YAML
            workflow = yaml.safe_load(workflow_content)
            
            # Core validations
            errors.extend(self._validate_workflow_structure(workflow))
            errors.extend(self._validate_triggers(workflow.get('on', {})))
            errors.extend(self._validate_jobs(workflow.get('jobs', {})))
            
            # Warnings and suggestions
            warnings.extend(self._check_best_practices(workflow))
            suggestions.extend(self._suggest_improvements(workflow))
            
            # Calculate severity score
            severity_score = len(errors) * 20 + len(warnings) * 5
            severity_score = min(severity_score, 100)
            
        except yaml.YAMLError as e:
            errors.append(f"YAML syntax error: {str(e)}")
            severity_score = 100
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            severity_score=severity_score
        )
    
    def _validate_workflow_structure(self, workflow: Dict[str, Any]) -> List[str]:
        """Validate basic workflow structure"""
        errors = []
        
        required_fields = ['name', 'on', 'jobs']
        for field in required_fields:
            if field not in workflow:
                errors.append(f"Missing required field: '{field}'")
        
        return errors
    
    def _validate_triggers(self, triggers: Dict[str, Any]) -> List[str]:
        """Validate workflow triggers"""
        errors = []
        
        if not triggers:
            errors.append("Workflow has no triggers defined")
            return errors
        
        # Validate trigger types
        valid_triggers = [
            'push', 'pull_request', 'pull_request_target', 'release', 
            'schedule', 'workflow_dispatch', 'workflow_call', 'repository_dispatch'
        ]
        
        for trigger in triggers:
            if trigger not in valid_triggers:
                errors.append(f"Unknown trigger type: '{trigger}'")
        
        # Validate push/pull_request configurations
        if 'push' in triggers:
            push_config = triggers['push']
            if isinstance(push_config, dict):
                self._validate_branch_config(push_config, 'push', errors)
        
        if 'pull_request' in triggers:
            pr_config = triggers['pull_request']
            if isinstance(pr_config, dict):
                self._validate_branch_config(pr_config, 'pull_request', errors)
        
        return errors
    
    def _validate_branch_config(self, config: Dict, trigger_type: str, errors: List[str]):
        """Validate branch configuration for triggers"""
        if 'branches' in config:
            branches = config['branches']
            if isinstance(branches, list):
                for branch in branches:
                    if not isinstance(branch, str):
                        errors.append(f"Invalid branch specification in {trigger_type}: {branch}")
    
    def _validate_jobs(self, jobs: Dict[str, Any]) -> List[str]:
        """Validate workflow jobs"""
        errors = []
        
        if not jobs:
            errors.append("Workflow has no jobs defined")
            return errors
        
        for job_name, job_config in jobs.items():
            errors.extend(self._validate_single_job(job_name, job_config))
        
        return errors
    
    def _validate_single_job(self, job_name: str, job_config: Dict[str, Any]) -> List[str]:
        """Validate a single job configuration"""
        errors = []
        
        # Required fields
        if 'runs-on' not in job_config:
            errors.append(f"Job '{job_name}': Missing required field 'runs-on'")
        else:
            errors.extend(self._validate_runner(job_config['runs-on']))
        
        # Validate steps
        if 'steps' in job_config:
            errors.extend(self._validate_steps(job_config['steps'], job_name))
        
        # Validate strategy matrix
        if 'strategy' in job_config:
            errors.extend(self._validate_strategy(job_config['strategy'], job_name))
        
        return errors
    
    def _validate_runner(self, runner: str) -> List[str]:
        """Validate runner specification"""
        errors = []
        
        if runner not in self.runner_specifications:
            errors.append(f"Unknown runner: '{runner}'")
            # Suggest similar runners
            suggestions = [r for r in self.runner_specifications.keys() if runner.lower() in r.lower()]
            if suggestions:
                errors.append(f"Did you mean: {', '.join(suggestions[:3])}?")
        else:
            runner_spec = self.runner_specifications[runner]
            if not runner_spec.get('supported', True):
                reason = runner_spec.get('reason', 'deprecated')
                errors.append(f"Runner '{runner}' is no longer supported: {reason}")
        
        return errors
    
    def _validate_steps(self, steps: List[Dict], job_name: str) -> List[str]:
        """Validate job steps"""
        errors = []
        
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"Job '{job_name}': Step {i+1} is not a valid object")
                continue
            
            errors.extend(self._validate_single_step(step, job_name, i+1))
        
        return errors
    
    def _validate_single_step(self, step: Dict[str, Any], job_name: str, step_num: int) -> List[str]:
        """Validate a single step"""
        errors = []
        prefix = f"Job '{job_name}', Step {step_num}"
        
        # Either 'uses' or 'run' is required
        if 'uses' not in step and 'run' not in step:
            errors.append(f"{prefix}: Must have either 'uses' or 'run'")
        
        # Validate action usage
        if 'uses' in step:
            errors.extend(self._validate_action_usage(step['uses'], step.get('with', {}), prefix))
        
        # Validate shell commands
        if 'run' in step:
            errors.extend(self._validate_run_commands(step['run'], prefix))
        
        return errors
    
    def _validate_action_usage(self, action: str, inputs: Dict, prefix: str) -> List[str]:
        """Validate GitHub Action usage"""
        errors = []
        
        # Parse action reference
        if '@' not in action:
            errors.append(f"{prefix}: Action '{action}' missing version tag")
            return errors
        
        action_name, version = action.split('@', 1)
        
        if action_name in self.github_actions_registry:
            action_spec = self.github_actions_registry[action_name]
            
            # Check if version is supported
            if version in action_spec.get('deprecated_versions', []):
                latest = action_spec.get('latest_version', 'latest')
                errors.append(f"{prefix}: Action version '{version}' is deprecated. Use '{latest}'")
            
            # Validate required inputs
            required_inputs = action_spec.get('required_inputs', [])
            for required_input in required_inputs:
                if required_input not in inputs:
                    errors.append(f"{prefix}: Missing required input '{required_input}' for {action}")
            
            # Check for invalid inputs
            valid_inputs = action_spec.get('required_inputs', []) + action_spec.get('optional_inputs', [])
            for input_name in inputs:
                if input_name not in valid_inputs:
                    errors.append(f"{prefix}: Unknown input '{input_name}' for {action}")
        
        return errors
    
    def _validate_run_commands(self, commands: str, prefix: str) -> List[str]:
        """Validate shell commands in run steps"""
        errors = []
        
        lines = commands.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for common issues
            if re.search(r'pip install.*requirements\.tx', line):
                errors.append(f"{prefix}, Line {line_num}: Invalid requirements file 'requirements.tx'")
            
            if re.search(r'export\s+\w+=["\']?\$\{\w*\}\s*$', line):
                errors.append(f"{prefix}, Line {line_num}: Incomplete environment variable export")
            
            # Check for unquoted variables with special characters
            if re.search(r'\$\{[^}]*[:\s][^}]*\}', line) and not re.search(r'["\'].*\$\{[^}]*[:\s][^}]*\}.*["\']', line):
                errors.append(f"{prefix}, Line {line_num}: Environment variable with special characters should be quoted")
        
        return errors
    
    def _validate_strategy(self, strategy: Dict[str, Any], job_name: str) -> List[str]:
        """Validate strategy matrix"""
        errors = []
        
        if 'matrix' not in strategy:
            return errors
        
        matrix = strategy['matrix']
        if not isinstance(matrix, dict):
            errors.append(f"Job '{job_name}': Strategy matrix must be an object")
            return errors
        
        # Validate matrix size
        total_combinations = 1
        for key, values in matrix.items():
            if isinstance(values, list):
                total_combinations *= len(values)
        
        if total_combinations > 256:
            errors.append(f"Job '{job_name}': Matrix has {total_combinations} combinations, exceeding GitHub's 256 limit")
        
        return errors
    
    def _check_best_practices(self, workflow: Dict[str, Any]) -> List[str]:
        """Check for best practice violations"""
        warnings = []
        
        # Check for missing timeout
        for job_name, job_config in workflow.get('jobs', {}).items():
            if 'timeout-minutes' not in job_config:
                warnings.append(f"Job '{job_name}': Consider adding timeout-minutes to prevent hanging")
        
        return warnings
    
    def _suggest_improvements(self, workflow: Dict[str, Any]) -> List[str]:
        """Suggest workflow improvements"""
        suggestions = []
        
        # Suggest caching for dependency installation
        for job_name, job_config in workflow.get('jobs', {}).items():
            steps = job_config.get('steps', [])
            has_pip_install = any('pip install' in step.get('run', '') for step in steps)
            has_cache = any('actions/cache' in step.get('uses', '') for step in steps)
            
            if has_pip_install and not has_cache:
                suggestions.append(f"Job '{job_name}': Consider adding actions/cache for pip dependencies")
        
        return suggestions

# Export for use in other modules
__all__ = ['AdvancedSemanticValidator', 'ValidationResult', 'ValidationLevel']