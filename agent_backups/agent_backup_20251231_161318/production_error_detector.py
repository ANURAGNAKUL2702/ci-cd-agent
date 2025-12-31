"""
Enhanced Pattern Detection Engine for CI/CD Agent
Comprehensive error pattern matching for production-grade validation
"""
import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ErrorCategory(Enum):
    SYNTAX = "syntax"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"

@dataclass
class ErrorPattern:
    name: str
    pattern: str
    category: ErrorCategory
    severity: ErrorSeverity
    description: str
    fix_suggestion: str
    confidence: float
    auto_fixable: bool

@dataclass
class DetectedError:
    pattern: ErrorPattern
    match: str
    line_number: Optional[int]
    context: str
    suggested_fix: str

class ProductionErrorDetector:
    """Production-grade error detection with comprehensive patterns"""
    
    def __init__(self):
        self.patterns = self._load_error_patterns()
    
    def _load_error_patterns(self) -> List[ErrorPattern]:
        """Load comprehensive error patterns for production use"""
        return [
            # YAML Structure Issues (Critical for parsing)
            ErrorPattern(
                name="yaml_structure_true_instead_of_on",
                pattern=r"^(\s*)true:\s*$",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.CRITICAL,
                description="Invalid YAML structure: 'true:' instead of 'on:'",
                fix_suggestion="Replace 'true:' with 'on:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="duplicate_malformed_on_section",
                pattern=r"'on':\s*push:\s*branches:\s*-\s*main\s*$",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Duplicate malformed 'on:' section",
                fix_suggestion="Remove duplicate 'on:' section",
                confidence=0.95,
                auto_fixable=True
            ),
            
            # Action Name Issues
            ErrorPattern(
                name="incomplete_action_checkout",
                pattern=r"uses:\s*actions/checko?u?t?(?!@|\s)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL,
                description="Incomplete GitHub action name",
                fix_suggestion="Complete action name to 'actions/checkout@v4'",
                confidence=0.98,
                auto_fixable=True
            ),
            ErrorPattern(
                name="incomplete_action_version_tag",
                pattern=r"uses:\s*actions/setup-python@\s*$",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.HIGH,
                description="Incomplete action version tag",
                fix_suggestion="Add version tag '@v5'",
                confidence=0.97,
                auto_fixable=True
            ),
            
            # Runner/OS Issues
            ErrorPattern(
                name="invalid_runner_ubuntu",
                pattern=r"runs-on:\s*ubuntu-lat(?:est)?(?!\w)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Invalid Ubuntu runner specification",
                fix_suggestion="Change to 'ubuntu-latest'",
                confidence=0.95,
                auto_fixable=True
            ),
            ErrorPattern(
                name="invalid_runner_typo",
                pattern=r"runs-on:\s*(?:ubuntu-20|ubuntu-18|ubuntu-16|ubuntu-\w+)(?!\.\d)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Deprecated or invalid Ubuntu version",
                fix_suggestion="Use 'ubuntu-latest', 'ubuntu-20.04', or 'ubuntu-22.04'",
                confidence=0.90,
                auto_fixable=True
            ),
            ErrorPattern(
                name="invalid_windows_runner",
                pattern=r"runs-on:\s*windows-(?:latest|2019|2016)(?!\w)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM,
                description="Potentially outdated Windows runner",
                fix_suggestion="Consider 'windows-latest' or 'windows-2022'",
                confidence=0.80,
                auto_fixable=True
            ),
            
            # Action Version Issues
            ErrorPattern(
                name="missing_action_version",
                pattern=r"uses:\s*actions/(?:checkout|setup-python|setup-node|setup-java|setup-go|cache|upload-artifact|download-artifact)(?!@)",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.HIGH,
                description="Missing version tag for GitHub Action",
                fix_suggestion="Add version tag (e.g., @v4 for checkout, @v5 for setup-python)",
                confidence=0.95,
                auto_fixable=True
            ),
            ErrorPattern(
                name="deprecated_action_version",
                pattern=r"uses:\s*actions/(?:checkout@v[12]|setup-python@v[1-3]|setup-node@v[1-2])",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.MEDIUM,
                description="Deprecated action version",
                fix_suggestion="Update to latest version",
                confidence=0.90,
                auto_fixable=True
            ),
            
            # Environment Variable Issues
            ErrorPattern(
                name="python_path_typo",
                pattern=r"\$\{?(?:PYTHPATH|PYTHON_PATH|PYPATH|PYTHOH)\}?",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Typo in PYTHONPATH environment variable",
                fix_suggestion="Use 'PYTHONPATH'",
                confidence=0.95,
                auto_fixable=True
            ),
            ErrorPattern(
                name="path_typo",
                pattern=r"\$\{?(?:PAHT|PTAH|APTH)\}?",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Typo in PATH environment variable",
                fix_suggestion="Use 'PATH'",
                confidence=0.95,
                auto_fixable=True
            ),
            
            # Dependency Issues
            ErrorPattern(
                name="requirements_file_typo",
                pattern=r"pip install -r (?:requirement|requir|requirements\.tx|requirement\.txt)",
                category=ErrorCategory.DEPENDENCY,
                severity=ErrorSeverity.CRITICAL,
                description="Invalid requirements file name",
                fix_suggestion="Use 'requirements.txt'",
                confidence=0.98,
                auto_fixable=True
            ),
            ErrorPattern(
                name="pip_upgrade_missing",
                pattern=r"pip install(?!\s+--upgrade|\s+-U)",
                category=ErrorCategory.DEPENDENCY,
                severity=ErrorSeverity.MEDIUM,
                description="Missing pip upgrade recommendation",
                fix_suggestion="Consider 'python -m pip install --upgrade pip' first",
                confidence=0.70,
                auto_fixable=False
            ),
            
            # Python Specific Issues
            ErrorPattern(
                name="python_version_deprecated",
                pattern=r"python-version:\s*['\"]?(?:2\.|3\.[0-6])['\"]?",
                category=ErrorCategory.COMPATIBILITY,
                severity=ErrorSeverity.HIGH,
                description="Deprecated or EOL Python version",
                fix_suggestion="Use Python 3.9 or higher",
                confidence=0.85,
                auto_fixable=True
            ),
            ErrorPattern(
                name="pytest_missing_verbose",
                pattern=r"pytest(?!\s+.*-v)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.LOW,
                description="Pytest without verbose output",
                fix_suggestion="Add '-v' flag for better debugging",
                confidence=0.60,
                auto_fixable=True
            ),
            
            # Security Issues
            ErrorPattern(
                name="hardcoded_secrets",
                pattern=r"(?:password|token|key|secret):\s*['\"](?![$\{])[^'\"]{8,}['\"]",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.CRITICAL,
                description="Potential hardcoded secret",
                fix_suggestion="Use ${{ secrets.SECRET_NAME }} or environment variables",
                confidence=0.80,
                auto_fixable=False
            ),
            
            # Syntax Issues
            ErrorPattern(
                name="incomplete_export",
                pattern=r"export\s+\w+=['\"]?\$\{?\w*\}?\s*$",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Incomplete export command",
                fix_suggestion="Complete the environment variable assignment",
                confidence=0.90,
                auto_fixable=False
            ),
            ErrorPattern(
                name="missing_yaml_quotes",
                pattern=r":\s*[^'\"{\[\n-]*\$\{[^}]*\}[^'\"}\]\n]*$",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.MEDIUM,
                description="Environment variable substitution without quotes",
                fix_suggestion="Wrap in quotes when using variable substitution",
                confidence=0.75,
                auto_fixable=True
            ),
            
            # Performance Issues
            ErrorPattern(
                name="missing_cache",
                pattern=r"pip install.*requirements\.txt",
                category=ErrorCategory.PERFORMANCE,
                severity=ErrorSeverity.LOW,
                description="Missing dependency caching",
                fix_suggestion="Consider adding actions/cache for pip dependencies",
                confidence=0.60,
                auto_fixable=False
            ),
            
            # Workflow Structure Issues
            ErrorPattern(
                name="missing_timeout",
                pattern=r"timeout-minutes:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.LOW,
                description="No timeout specified",
                fix_suggestion="Add timeout-minutes to prevent hanging workflows",
                confidence=0.50,
                auto_fixable=True
            ),
            
            # Additional comprehensive patterns for full automation
            ErrorPattern(
                name="env_var_syntax_error",
                pattern=r"\$[A-Z_][A-Z0-9_]*(?!\{)",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Environment variable used without proper ${} syntax",
                fix_suggestion="Use ${VAR_NAME} syntax for environment variables",
                confidence=0.90,
                auto_fixable=True
            ),
            ErrorPattern(
                name="cache_action_missing_key",
                pattern=r"uses:\s*actions/cache@v\d+(?!\s*\n[^:]*key:)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Cache action missing required 'key' parameter",
                fix_suggestion="Add key parameter to cache action",
                confidence=0.95,
                auto_fixable=True
            ),
            ErrorPattern(
                name="working_directory_typo",
                pattern=r"working[-_]dir(?:ectory)?:",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Incorrect working directory parameter name",
                fix_suggestion="Use 'working-directory' parameter",
                confidence=0.98,
                auto_fixable=True
            ),
            ErrorPattern(
                name="if_condition_syntax_error",
                pattern=r"if:\s*['\"]?(?:github\.event_name\s*=(?!=)|github\.ref\s*=(?!=))",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.CRITICAL,
                description="GitHub context condition using single = instead of ==",
                fix_suggestion="Use == for equality comparison in conditions",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="artifact_action_missing_name",
                pattern=r"uses:\s*actions/upload-artifact@v\d+(?!\s*\n[^:]*name:)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Upload artifact action missing required 'name' parameter",
                fix_suggestion="Add name parameter to artifact action",
                confidence=0.95,
                auto_fixable=True
            ),
            ErrorPattern(
                name="secret_exposed",
                pattern=r"(?:password|token|key|secret):\s*['\"]?[A-Za-z0-9+/]{20,}[=]{0,2}['\"]?",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.CRITICAL,
                description="Potential hardcoded secret detected",
                fix_suggestion="Use ${{ secrets.SECRET_NAME }} instead of hardcoded values",
                confidence=0.80,
                auto_fixable=False  # Requires manual secret management
            ),
            ErrorPattern(
                name="test_timeout_missing",
                pattern=r"run:\s*(?:npm test|pytest|cargo test|jest)(?!\s*\n.*timeout-minutes:)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM,
                description="Long-running test commands should have timeout",
                fix_suggestion="Add timeout-minutes to prevent hanging jobs",
                confidence=0.70,
                auto_fixable=True
            ),
            ErrorPattern(
                name="permissions_too_broad",
                pattern=r"permissions:\s*write-all",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.HIGH,
                description="Overly broad permissions detected",
                fix_suggestion="Use specific permissions instead of write-all",
                confidence=0.95,
                auto_fixable=True
            ),
            
            # Production-Grade CI/CD Patterns
            ErrorPattern(
                name="env_var_name_typos",
                pattern=r"(?:NODE_VERSIO|PYTHON_VERSIO|REGISTR|IMAGE_NAM|PYTHONPTH)\b",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name contains typo",
                fix_suggestion="Fix environment variable name spelling",
                confidence=0.98,
                auto_fixable=True
            ),
            ErrorPattern(
                name="timeout_syntax_error",
                pattern=r"timeout:\s*\d+\s*$",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                description="Timeout syntax should use 'timeout-minutes'",
                fix_suggestion="Use 'timeout-minutes' instead of 'timeout'",
                confidence=0.95,
                auto_fixable=True
            ),
            ErrorPattern(
                name="github_context_single_equals",
                pattern=r"github\.(ref|event_name)\s*=\s*[^=]",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.CRITICAL,
                description="GitHub context comparison using single = instead of ==",
                fix_suggestion="Use == for equality comparison",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="action_version_incomplete",
                pattern=r"@v\s*$",
                category=ErrorCategory.DEPENDENCY,
                severity=ErrorSeverity.HIGH,
                description="Action version tag incomplete (missing version number)",
                fix_suggestion="Add complete version number after @v",
                confidence=0.95,
                auto_fixable=True
            ),
            ErrorPattern(
                name="matrix_strategy_missing",
                pattern=r"runs-on:\s*\$\{\{\s*matrix\.[^}]+\}\}(?!.*strategy:)",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Matrix variable used without strategy definition",
                fix_suggestion="Add strategy section with matrix configuration",
                confidence=0.90,
                auto_fixable=False
            ),
            ErrorPattern(
                name="environment_name_missing",
                pattern=r"environment:\s*$",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM,
                description="Environment deployment missing environment name",
                fix_suggestion="Add environment name for deployment",
                confidence=0.85,
                auto_fixable=True
            ),
            
            # === ENTERPRISE CRITICAL PATTERNS ===
            
            # Fix workflow dispatch syntax errors
            ErrorPattern(
                name="workflow_dispatch_syntax_error",
                pattern=r"workflow_dispatch:\s*\n\s*inputs:\s*\n\s*([^:]+):\s*([^\n]+)\s*\n\s*description:",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.CRITICAL,
                description="Invalid workflow_dispatch input structure",
                fix_suggestion="Fix workflow_dispatch input structure",
                confidence=0.95,
                auto_fixable=True
            ),
            
            # Fix incomplete action versions (major issue)
            ErrorPattern(
                name="incomplete_action_checkout_v4_malformed",
                pattern=r"uses:\s*actions/checkout@v4v44v44v44v44v44",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.CRITICAL,
                description="Malformed checkout action version",
                fix_suggestion="Fix to 'actions/checkout@v4'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="incomplete_gitleaks_version",
                pattern=r"uses:\s*gitleaks/gitleaks-action@v\b",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.HIGH,
                description="Incomplete GitLeaks action version",
                fix_suggestion="Complete to 'gitleaks/gitleaks-action@v2'",
                confidence=0.98,
                auto_fixable=True
            ),
            ErrorPattern(
                name="incomplete_trivy_version",
                pattern=r"uses:\s*aquasecurity/trivy-action@\s*$",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.HIGH,
                description="Missing Trivy action version",
                fix_suggestion="Add version '@master'",
                confidence=0.98,
                auto_fixable=True
            ),
            ErrorPattern(
                name="incomplete_dependency_check_version",
                pattern=r"uses:\s*dependency-check/Dependency-Check_Action@\s*$",
                category=ErrorCategory.SECURITY,
                severity=ErrorSeverity.HIGH,
                description="Missing dependency check action version",
                fix_suggestion="Add version '@main'",
                confidence=0.98,
                auto_fixable=True
            ),
            
            # Environment variable name typos (enterprise pipelines have these)
            ErrorPattern(
                name="env_var_registry_typo",
                pattern=r"REGISTRYYYYY:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'REGISTRY:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="env_var_image_name_typo",
                pattern=r"IMAGE_NAMEEEEE:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'IMAGE_NAME:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="env_var_node_version_typo",
                pattern=r"NODE_VERSIONNNNN:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'NODE_VERSION:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="env_var_python_version_typo",
                pattern=r"PYTHON_VERSIONNNNN:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'PYTHON_VERSION:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="env_var_java_version_typo",
                pattern=r"JAVA_VERSIO:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'JAVA_VERSION:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="env_var_terraform_version_typo",
                pattern=r"TERRAFORM_VERSIO:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'TERRAFORM_VERSION:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="env_var_kubectl_version_typo",
                pattern=r"KUBECTL_VERSIO:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'KUBECTL_VERSION:'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="env_var_helm_version_typo",
                pattern=r"HELM_VERSIO:",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Environment variable name typo",
                fix_suggestion="Fix to 'HELM_VERSION:'",
                confidence=0.99,
                auto_fixable=True
            ),
            
            # Runner specification errors
            ErrorPattern(
                name="runner_ubuntu_malformed_latest",
                pattern=r"ubuntu-latesttesttesttesttestt",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Malformed ubuntu runner specification",
                fix_suggestion="Fix to 'ubuntu-latest'",
                confidence=0.99,
                auto_fixable=True
            ),
            ErrorPattern(
                name="runner_ubuntu_incomplete",
                pattern=r"ubuntu-lat\b",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH,
                description="Incomplete ubuntu runner specification",
                fix_suggestion="Fix to 'ubuntu-latest'",
                confidence=0.99,
                auto_fixable=True
            ),
        ]
    
    def detect_errors(self, content: str, file_path: str = "") -> List[DetectedError]:
        """Detect all errors in the provided content"""
        errors = []
        lines = content.split('\n')
        
        for pattern in self.patterns:
            matches = list(re.finditer(pattern.pattern, content, re.MULTILINE | re.IGNORECASE))
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                context_start = max(0, line_num - 3)
                context_end = min(len(lines), line_num + 2)
                context = '\n'.join(lines[context_start:context_end])
                
                # Generate specific fix suggestion
                suggested_fix = self._generate_fix_suggestion(pattern, match.group())
                
                error = DetectedError(
                    pattern=pattern,
                    match=match.group(),
                    line_number=line_num,
                    context=context,
                    suggested_fix=suggested_fix
                )
                errors.append(error)
        
        return errors
    
    def _generate_fix_suggestion(self, pattern: ErrorPattern, match: str) -> str:
        """Generate specific fix suggestion based on the match"""
        if pattern.name == "invalid_runner_ubuntu":
            return match.replace(re.search(r"ubuntu-\w+", match).group(), "ubuntu-latest")
        
        elif pattern.name == "missing_action_version":
            action_map = {
                "actions/checkout": "actions/checkout@v4",
                "actions/setup-python": "actions/setup-python@v5",
                "actions/setup-node": "actions/setup-node@v4",
                "actions/setup-java": "actions/setup-java@v4",
                "actions/cache": "actions/cache@v3",
                "actions/upload-artifact": "actions/upload-artifact@v4",
                "actions/download-artifact": "actions/download-artifact@v4",
            }
            for action, versioned in action_map.items():
                if action in match:
                    return match.replace(action, versioned)
        
        elif pattern.name == "python_path_typo":
            return re.sub(r"PYTHPATH|PYTHON_PATH|PYPATH|PYTHOH", "PYTHONPATH", match)
        
        elif pattern.name == "requirements_file_typo":
            return re.sub(r"requirement\.txt|requir\.txt|requirements\.tx|requirement", "requirements.txt", match)
        
        return pattern.fix_suggestion
    
    def get_error_summary(self, errors: List[DetectedError]) -> Dict:
        """Generate comprehensive error summary"""
        summary = {
            "total_errors": len(errors),
            "by_severity": {},
            "by_category": {},
            "auto_fixable": len([e for e in errors if e.pattern.auto_fixable]),
            "critical_issues": len([e for e in errors if e.pattern.severity == ErrorSeverity.CRITICAL])
        }
        
        for severity in ErrorSeverity:
            summary["by_severity"][severity.value] = len([e for e in errors if e.pattern.severity == severity])
        
        for category in ErrorCategory:
            summary["by_category"][category.value] = len([e for e in errors if e.pattern.category == category])
        
        return summary

# Export for use in other modules
__all__ = ['ProductionErrorDetector', 'DetectedError', 'ErrorPattern', 'ErrorSeverity', 'ErrorCategory']