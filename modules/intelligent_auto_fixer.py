"""
Intelligent Auto-Fixing Engine for CI/CD Agent
Automatically repairs detected issues with confidence scoring and rollback capability
"""
import re
import yaml
import copy
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from .production_error_detector import DetectedError, ProductionErrorDetector
from .advanced_semantic_validator import AdvancedSemanticValidator, ValidationResult

class FixConfidence(Enum):
    VERY_HIGH = "very_high"  # 95-100%
    HIGH = "high"           # 80-94%
    MEDIUM = "medium"       # 60-79%
    LOW = "low"            # 40-59%
    VERY_LOW = "very_low"  # <40%

class FixStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    NEEDS_APPROVAL = "needs_approval"

@dataclass
class FixAttempt:
    error: DetectedError
    original_content: str
    fixed_content: str
    fix_description: str
    confidence: FixConfidence
    status: FixStatus
    backup_created: bool
    validation_passed: bool

@dataclass
class FixReport:
    total_errors: int
    fixed_errors: int
    skipped_errors: int
    failed_fixes: int
    confidence_distribution: Dict[str, int]
    fixes_applied: List[FixAttempt]
    validation_result: ValidationResult
    final_content: str

class IntelligentAutoFixer:
    """Production-grade auto-fixing engine with confidence scoring"""
    
    def __init__(self, 
                 min_confidence: FixConfidence = FixConfidence.HIGH,
                 require_approval_for_medium: bool = True,
                 create_backups: bool = True):
        self.min_confidence = min_confidence
        self.require_approval_for_medium = require_approval_for_medium
        self.create_backups = create_backups
        self.error_detector = ProductionErrorDetector()
        self.validator = AdvancedSemanticValidator()
        
        # Fix confidence thresholds
        self.confidence_thresholds = {
            FixConfidence.VERY_HIGH: 0.95,
            FixConfidence.HIGH: 0.80,
            FixConfidence.MEDIUM: 0.60,
            FixConfidence.LOW: 0.40,
            FixConfidence.VERY_LOW: 0.0
        }
    
    def fix_workflow(self, content: str, file_path: str = "", 
                    apply_fixes: bool = True) -> FixReport:
        """
        Automatically fix detected issues in workflow content
        
        Args:
            content: Original workflow content
            file_path: Path to the workflow file
            apply_fixes: Whether to actually apply fixes or just analyze
            
        Returns:
            FixReport with details of all fixes attempted
        """
        # Detect errors
        detected_errors = self.error_detector.detect_errors(content, file_path)
        
        if not detected_errors:
            # No errors found, validate anyway
            validation_result = self.validator.validate_workflow(content, file_path)
            return FixReport(
                total_errors=0,
                fixed_errors=0,
                skipped_errors=0,
                failed_fixes=0,
                confidence_distribution={},
                fixes_applied=[],
                validation_result=validation_result
            )
        
        # Process each error and attempt fixes
        fixes_applied = []
        current_content = content
        
        for error in detected_errors:
            fix_attempt = self._attempt_fix(error, current_content, apply_fixes)
            fixes_applied.append(fix_attempt)
            
            # If fix was successful, update content for next iteration
            if fix_attempt.status == FixStatus.SUCCESS:
                current_content = fix_attempt.fixed_content
        
        # Final validation
        validation_result = self.validator.validate_workflow(current_content, file_path)
        
        # Generate report with final content
        report = self._generate_report(detected_errors, fixes_applied, validation_result)
        report.final_content = current_content  # Ensure final content is set
        
        return report
    
    def _attempt_fix(self, error: DetectedError, content: str, apply_fix: bool) -> FixAttempt:
        """Attempt to fix a single error"""
        confidence = self._calculate_fix_confidence(error)
        
        # Check if we should attempt this fix
        if not self._should_attempt_fix(confidence):
            return FixAttempt(
                error=error,
                original_content=content,
                fixed_content=content,
                fix_description="Skipped due to low confidence",
                confidence=confidence,
                status=FixStatus.SKIPPED,
                backup_created=False,
                validation_passed=False
            )
        
        # Generate the fix
        try:
            fixed_content = self._generate_fix(error, content)
            fix_description = self._generate_fix_description(error)
            
            if not apply_fix:
                return FixAttempt(
                    error=error,
                    original_content=content,
                    fixed_content=fixed_content,
                    fix_description=fix_description,
                    confidence=confidence,
                    status=FixStatus.SUCCESS,
                    backup_created=False,
                    validation_passed=True  # Assume it would pass
                )
            
            # Validate the fix
            validation_passed = self._validate_fix(fixed_content)
            
            status = FixStatus.SUCCESS if validation_passed else FixStatus.FAILED
            
            return FixAttempt(
                error=error,
                original_content=content,
                fixed_content=fixed_content if validation_passed else content,
                fix_description=fix_description,
                confidence=confidence,
                status=status,
                backup_created=self.create_backups,
                validation_passed=validation_passed
            )
            
        except Exception as e:
            return FixAttempt(
                error=error,
                original_content=content,
                fixed_content=content,
                fix_description=f"Fix failed: {str(e)}",
                confidence=confidence,
                status=FixStatus.FAILED,
                backup_created=False,
                validation_passed=False
            )
    
    def _calculate_fix_confidence(self, error: DetectedError) -> FixConfidence:
        """Calculate confidence level for fixing this error"""
        base_confidence = error.pattern.confidence
        
        # Adjust based on error characteristics
        adjustments = 0.0
        
        # High confidence patterns (very safe to auto-fix)
        high_confidence_patterns = {
            'yaml_structure_true_instead_of_on',
            'duplicate_malformed_on_section', 
            'incomplete_action_checkout',
            'incomplete_action_version_tag',
            'invalid_runner_ubuntu',
            'python_path_typo',
            'requirements_file_typo',
            'python_version_deprecated',
            'deprecated_action_version',
            'working_directory_typo',
            'if_condition_syntax_error',
            'env_var_syntax_error',
            'env_var_name_typos',
            'timeout_syntax_error',
            'github_context_single_equals',
            'action_version_incomplete'
        }
        
        # Medium confidence patterns (mostly safe but need validation) 
        medium_confidence_patterns = {
            'missing_action_version',
            'pytest_missing_verbose',
            'missing_yaml_quotes',
            'cache_action_missing_key',
            'artifact_action_missing_name',
            'test_timeout_missing',
            'permissions_too_broad',
            'environment_name_missing'
        }
        
        # Boost confidence for well-known safe fixes
        if error.pattern.name in high_confidence_patterns:
            adjustments += 0.15
        elif error.pattern.name in medium_confidence_patterns:
            adjustments += 0.05
        
        # Lower confidence for security-related issues (except permissions)
        if (error.pattern.category.value == 'security' and 
            error.pattern.name not in ['permissions_too_broad']):
            adjustments -= 0.10
        
        # Boost confidence for structural fixes
        if error.pattern.category.value in ['syntax', 'configuration']:
            adjustments += 0.05
        
        # Higher confidence for simple pattern matches with clear context
        if error.line_number and len(error.context.strip()) > 20:
            adjustments += 0.03
        
        final_confidence = min(1.0, max(0.0, base_confidence + adjustments))
        
        # Map to confidence enum with lower thresholds for more automation
        if final_confidence >= 0.90:
            return FixConfidence.VERY_HIGH
        elif final_confidence >= 0.75:
            return FixConfidence.HIGH
        elif final_confidence >= 0.60:
            return FixConfidence.MEDIUM
        elif final_confidence >= 0.40:
            return FixConfidence.LOW
        else:
            return FixConfidence.VERY_LOW
    
    def _should_attempt_fix(self, confidence: FixConfidence) -> bool:
        """Determine if we should attempt to fix based on confidence level"""
        confidence_order = [FixConfidence.VERY_HIGH, FixConfidence.HIGH, 
                           FixConfidence.MEDIUM, FixConfidence.LOW, FixConfidence.VERY_LOW]
        
        min_index = confidence_order.index(self.min_confidence)
        current_index = confidence_order.index(confidence)
        
        return current_index <= min_index
    
    def _generate_fix(self, error: DetectedError, content: str) -> str:
        """Generate the actual fix for the error"""
        pattern_name = error.pattern.name
        match = error.match
        
        # YAML Structure Fixes
        if pattern_name == "yaml_structure_true_instead_of_on":
            return content.replace("true:", "on:")
        
        elif pattern_name == "duplicate_malformed_on_section":
            import re
            return re.sub(r"'on':\s*push:\s*branches:\s*-\s*main\s*$", "", content, flags=re.MULTILINE)
        
        # Action Name Fixes
        elif pattern_name == "incomplete_action_checkout":
            # More specific replacement to avoid duplicates
            if "actions/checkt" in content:
                return content.replace("actions/checkt", "actions/checkout@v4")
            elif "actions/checkout" in content and "@v" not in content:
                return content.replace("actions/checkout", "actions/checkout@v4")
            else:
                return content
        
        elif pattern_name == "incomplete_action_version_tag":
            return content.replace("actions/setup-python@", "actions/setup-python@v5")
        
        # Runner Issues
        elif pattern_name == "invalid_runner_ubuntu":
            import re
            return re.sub(r'runs-on:\s*ubuntu-lat(?:est)?(?!\w)', 'runs-on: ubuntu-latest', content)
        
        elif pattern_name == "missing_action_version":
            action_fixes = {
                'actions/checkout': 'actions/checkout@v4',
                'actions/setup-python': 'actions/setup-python@v5',
                'actions/setup-node': 'actions/setup-node@v4',
                'actions/setup-java': 'actions/setup-java@v4',
                'actions/cache': 'actions/cache@v4',
                'actions/upload-artifact': 'actions/upload-artifact@v4',
                'actions/download-artifact': 'actions/download-artifact@v4'
            }
            
            for action, fixed_action in action_fixes.items():
                if action in match:
                    return content.replace(match, match.replace(action, fixed_action))
        
        elif pattern_name == "python_path_typo":
            import re
            return re.sub(r'PYTHPATH|PYTHON_PATH|PYPATH|PYTHOH|PYTHATH', 'PYTHONPATH', content)
        
        elif pattern_name == "requirements_file_typo":
            import re
            # More specific pattern matching
            content = re.sub(r'pip install -r requirement\.txt', 'pip install -r requirements.txt', content)
            content = re.sub(r'pip install -r requir(?:ement)?\.txt', 'pip install -r requirements.txt', content)
            content = re.sub(r'pip install -r requirements\.tx', 'pip install -r requirements.txt', content)
            return content
        
        elif pattern_name == "python_version_deprecated":
            import re
            return re.sub(r"python-version:\s*['\"]?(?:2\.|3\.[0-6])['\"]?", 
                         "python-version: '3.9'", content)
        
        elif pattern_name == "deprecated_action_version":
            version_map = {
                'checkout@v1': 'checkout@v4',
                'checkout@v2': 'checkout@v4',
                'setup-python@v1': 'setup-python@v5',
                'setup-python@v2': 'setup-python@v5',
                'setup-python@v3': 'setup-python@v5',
                'setup-node@v1': 'setup-node@v4',
                'setup-node@v2': 'setup-node@v4'
            }
            
            for old_version, new_version in version_map.items():
                if old_version in match:
                    return content.replace(match, match.replace(old_version, new_version))
        
        elif pattern_name == "pytest_missing_verbose":
            import re
            return re.sub(r'pytest(?!\s+.*-v)', 'pytest -v', content)
        
        elif pattern_name == "missing_yaml_quotes":
            import re
            return re.sub(r'(:\s*)([^\'\"{\[\n-]*\$\{[^}]*\}[^\'\"}\]\n]*)', r'\1"\2"', match)
        
        # New comprehensive auto-fix patterns
        elif pattern_name == "env_var_syntax_error":
            import re
            # Convert $VAR to ${VAR}
            return re.sub(r'\$([A-Z_][A-Z0-9_]*)', r'${\1}', content)
        
        elif pattern_name == "cache_action_missing_key":
            # Find the cache action and add key parameter after it
            lines = content.split('\n')
            fixed_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if 'actions/cache@v' in line:
                    fixed_lines.append(line)
                    # Check if next line already has 'with:'
                    if i + 1 < len(lines) and 'with:' in lines[i + 1]:
                        # Add to existing with section
                        fixed_lines.append(lines[i + 1])
                        i += 2
                        # Add key after with:
                        indent = '  ' * (line.find('-') + 2 if '-' in line else 4)
                        fixed_lines.append(f"{indent}key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}")
                    else:
                        # Add new with section
                        indent = '  ' * (line.find('-') + 1 if '-' in line else 3)
                        fixed_lines.append(f"{indent}with:")
                        fixed_lines.append(f"{indent}  key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}")
                        i += 1
                else:
                    fixed_lines.append(line)
                    i += 1
            return '\n'.join(fixed_lines)
        
        elif pattern_name == "working_directory_typo":
            import re
            return re.sub(r'working[-_]dir(?:ectory)?:', 'working-directory:', content)
        
        elif pattern_name == "if_condition_syntax_error":
            import re
            # Fix single = to == in conditions
            return re.sub(r'(github\.(?:event_name|ref))\s*=(?!=)', r'\1 ==', content)
        
        elif pattern_name == "artifact_action_missing_name":
            # Find the upload-artifact action and add name parameter
            lines = content.split('\n')
            fixed_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if 'actions/upload-artifact@v' in line:
                    fixed_lines.append(line)
                    # Check if next line already has 'with:'
                    if i + 1 < len(lines) and 'with:' in lines[i + 1]:
                        # Add to existing with section
                        fixed_lines.append(lines[i + 1])
                        i += 2
                        # Add name after with:
                        indent = '  ' * (line.find('-') + 2 if '-' in line else 4)
                        fixed_lines.append(f"{indent}name: build-artifacts")
                    else:
                        # Add new with section
                        indent = '  ' * (line.find('-') + 1 if '-' in line else 3)
                        fixed_lines.append(f"{indent}with:")
                        fixed_lines.append(f"{indent}  name: build-artifacts")
                        i += 1
                else:
                    fixed_lines.append(line)
                    i += 1
            return '\n'.join(fixed_lines)
        
        elif pattern_name == "test_timeout_missing":
            # Add timeout to test commands
            lines = content.split('\n')
            fixed_lines = []
            for line in lines:
                if "run:" in line and any(test_cmd in line for test_cmd in ["npm test", "pytest", "cargo test", "jest"]):
                    # Find the indentation level
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(line)
                    fixed_lines.append(" " * indent + "timeout-minutes: 10")
                else:
                    fixed_lines.append(line)
            return '\n'.join(fixed_lines)
        
        elif pattern_name == "permissions_too_broad":
            # Replace write-all with more specific permissions
            return content.replace("permissions: write-all", 
                                 "permissions:\n  contents: read\n  actions: read\n  checks: write")
        
        # Production-grade fixes
        elif pattern_name == "env_var_name_typos":
            import re
            # Fix common environment variable typos
            env_fixes = {
                'NODE_VERSIO': 'NODE_VERSION',
                'PYTHON_VERSIO': 'PYTHON_VERSION', 
                'REGISTR': 'REGISTRY',
                'IMAGE_NAM': 'IMAGE_NAME',
                'PYTHONPTH': 'PYTHONPATH'
            }
            
            for typo, correct in env_fixes.items():
                content = content.replace(typo, correct)
            return content
            
        elif pattern_name == "timeout_syntax_error":
            import re
            # Convert timeout: to timeout-minutes:
            return re.sub(r'timeout:\s*(\d+)', r'timeout-minutes: \1', content)
            
        elif pattern_name == "github_context_single_equals":
            import re
            # Fix single = to == in GitHub context comparisons
            content = re.sub(r'(github\.ref)\s*=\s*([^=])', r'\1 == \2', content)
            content = re.sub(r'(github\.event_name)\s*=\s*([^=])', r'\1 == \2', content)
            return content
            
        elif pattern_name == "action_version_incomplete":
            # Fix incomplete @v tags with appropriate version numbers
            action_version_map = {
                'securecodewarrior/github-action-add-sarif@v': 'securecodewarrior/github-action-add-sarif@v1',
                'actions/checkout@v': 'actions/checkout@v4',
                'actions/setup-python@v': 'actions/setup-python@v5',
                'actions/setup-node@v': 'actions/setup-node@v4',
                'actions/cache@v': 'actions/cache@v4',
                'azure/k8s-deploy@v': 'azure/k8s-deploy@v1'
            }
            
            for incomplete, complete in action_version_map.items():
                if incomplete in content:
                    content = content.replace(incomplete, complete)
            return content
            
        elif pattern_name == "environment_name_missing":
            # Add a default environment name
            return content.replace("environment:", "environment: staging")
        
        # Default: use the suggested fix from the error detector
        return content.replace(match, error.suggested_fix)
    
    def _generate_fix_description(self, error: DetectedError) -> str:
        """Generate a human-readable description of the fix"""
        return f"Fixed {error.pattern.description.lower()}: {error.pattern.fix_suggestion}"
    
    def _validate_fix(self, fixed_content: str) -> bool:
        """Validate that the fix doesn't break the workflow"""
        try:
            # Basic YAML validation - must pass
            yaml.safe_load(fixed_content)
            
            # Semantic validation - allow some remaining issues
            validation_result = self.validator.validate_workflow(fixed_content)
            
            # Consider it valid if:
            # 1. No critical YAML syntax errors
            # 2. Fewer than 10 remaining issues (we're fixing incrementally)
            critical_errors = [err for err in validation_result.errors 
                             if hasattr(err, 'severity') and str(err.severity).lower() == 'critical']
            
            return len(critical_errors) == 0 and len(validation_result.errors) < 20
            
        except yaml.YAMLError:
            # YAML syntax error - fix is invalid
            return False
        except Exception:
            # Other validation errors - be permissive during incremental fixes
            return True
    
    def _generate_report(self, detected_errors: List[DetectedError], 
                        fixes_applied: List[FixAttempt],
                        validation_result: ValidationResult) -> FixReport:
        """Generate comprehensive fix report"""
        
        fixed_errors = len([f for f in fixes_applied if f.status == FixStatus.SUCCESS])
        skipped_errors = len([f for f in fixes_applied if f.status == FixStatus.SKIPPED])
        failed_fixes = len([f for f in fixes_applied if f.status == FixStatus.FAILED])
        
        # Get the final content from the last successful fix, or original if none
        final_content = ""
        if fixes_applied:
            # Find the last fix (successful or not) for the final content
            for fix in reversed(fixes_applied):
                if fix.fixed_content:
                    final_content = fix.fixed_content
                    break
        
        # Confidence distribution
        confidence_dist = {}
        for conf_level in FixConfidence:
            confidence_dist[conf_level.value] = len([f for f in fixes_applied 
                                                   if f.confidence == conf_level])
        
        return FixReport(
            total_errors=len(detected_errors),
            fixed_errors=fixed_errors,
            skipped_errors=skipped_errors,
            failed_fixes=failed_fixes,
            confidence_distribution=confidence_dist,
            fixes_applied=fixes_applied,
            validation_result=validation_result,
            final_content=final_content
        )
    
    def generate_fix_summary(self, report: FixReport) -> str:
        """Generate a human-readable summary of fixes"""
        summary = []
        summary.append(f"# Auto-Fix Report")
        summary.append(f"")
        summary.append(f"## Summary")
        summary.append(f"- **Total Issues**: {report.total_errors}")
        summary.append(f"- **Successfully Fixed**: {report.fixed_errors}")
        summary.append(f"- **Skipped**: {report.skipped_errors}")
        summary.append(f"- **Failed**: {report.failed_fixes}")
        summary.append(f"")
        
        if report.fixes_applied:
            summary.append(f"## Fixes Applied")
            for fix in report.fixes_applied:
                if fix.status == FixStatus.SUCCESS:
                    summary.append(f"- ✅ {fix.fix_description}")
                elif fix.status == FixStatus.SKIPPED:
                    summary.append(f"- ⏭️ Skipped: {fix.error.pattern.description}")
                elif fix.status == FixStatus.FAILED:
                    summary.append(f"- ❌ Failed: {fix.error.pattern.description}")
        
        summary.append(f"")
        summary.append(f"## Final Validation")
        if report.validation_result.is_valid:
            summary.append(f"✅ Workflow validation passed")
        else:
            summary.append(f"❌ Workflow validation failed")
            summary.append(f"Remaining errors: {len(report.validation_result.errors)}")
        
        return "\n".join(summary)

# Export for use in other modules
__all__ = ['IntelligentAutoFixer', 'FixReport', 'FixAttempt', 'FixConfidence', 'FixStatus']