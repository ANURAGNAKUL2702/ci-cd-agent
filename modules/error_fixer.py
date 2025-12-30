"""
Error Fixer Module
Provides intelligent fix suggestions for common CI/CD errors
"""
from typing import Dict, List, Optional
from loguru import logger
from .log_analyzer import ErrorCategory


class ErrorFixer:
    """Generates fix suggestions based on error categories"""
    
    # Fix suggestions for different error types
    FIX_SUGGESTIONS = {
        ErrorCategory.YAML_SYNTAX_ERROR: {
            "description": "YAML syntax error detected",
            "suggestions": [
                "Check for proper indentation (use spaces, not tabs)",
                "Ensure all quotes are properly closed",
                "Verify that colons are followed by a space",
                "Use YAML validators to identify specific syntax issues"
            ],
            "auto_fixable": True
        },
        ErrorCategory.MISSING_DEPENDENCY: {
            "description": "Missing Python module or dependency",
            "suggestions": [
                "Add the missing package to requirements.txt",
                "Update the 'Install Dependencies' step in your workflow",
                "Verify package name spelling",
                "Check if the package requires specific Python version"
            ],
            "auto_fixable": True
        },
        ErrorCategory.INVALID_ACTION: {
            "description": "Invalid or non-existent GitHub Action",
            "suggestions": [
                "Verify the action name and repository path",
                "Check if the action version/tag exists",
                "Ensure the action repository is public or accessible",
                "Look for typos in the action reference"
            ],
            "auto_fixable": False
        },
        ErrorCategory.DEPRECATED_ACTION: {
            "description": "Using deprecated GitHub Action version",
            "suggestions": [
                "Update to the latest stable version of the action",
                "Check the action's repository for migration guides",
                "Review breaking changes in newer versions"
            ],
            "auto_fixable": True
        },
        ErrorCategory.PERMISSION_ERROR: {
            "description": "Permission or access denied",
            "suggestions": [
                "Check repository permissions and access tokens",
                "Verify GITHUB_TOKEN has required permissions",
                "Review workflow permissions in YAML configuration",
                "Ensure secrets are properly configured"
            ],
            "auto_fixable": False
        },
        ErrorCategory.TIMEOUT_ERROR: {
            "description": "Job or step timed out",
            "suggestions": [
                "Increase timeout-minutes in job or step configuration",
                "Optimize the workflow to reduce execution time",
                "Split long-running jobs into smaller chunks",
                "Use caching to speed up dependency installation"
            ],
            "auto_fixable": True
        },
        ErrorCategory.ENVIRONMENT_VARIABLE_MISSING: {
            "description": "Required environment variable not set",
            "suggestions": [
                "Add the environment variable in the workflow YAML",
                "Set the variable in repository settings",
                "Check for typos in variable names",
                "Ensure the variable is accessible in the current scope"
            ],
            "auto_fixable": True
        },
        ErrorCategory.SECRET_MISSING: {
            "description": "Required secret not found",
            "suggestions": [
                "Add the secret in repository/organization settings",
                "Verify secret name matches the reference in workflow",
                "Check if secret is accessible at the current scope",
                "Ensure proper access for organization secrets"
            ],
            "auto_fixable": False
        },
        ErrorCategory.VERSION_MISMATCH: {
            "description": "Version incompatibility detected",
            "suggestions": [
                "Update dependencies to compatible versions",
                "Pin specific versions in requirements",
                "Check for breaking changes in newer versions",
                "Use version constraints in dependency specifications"
            ],
            "auto_fixable": True
        },
        ErrorCategory.BUILD_ERROR: {
            "description": "Build or compilation failed",
            "suggestions": [
                "Review build logs for specific error messages",
                "Ensure all dependencies are installed",
                "Check for syntax errors in source code",
                "Verify build tool configuration"
            ],
            "auto_fixable": False
        },
        ErrorCategory.TEST_FAILURE: {
            "description": "Tests failed during execution",
            "suggestions": [
                "Review test output for specific failures",
                "Fix failing test cases or code",
                "Ensure test environment is properly configured",
                "Check for flaky tests and stabilize them"
            ],
            "auto_fixable": False
        },
    }
    
    def __init__(self):
        self.fix_suggestions = self.FIX_SUGGESTIONS
    
    def get_fix_suggestions(self, error_category: str) -> Dict[str, any]:
        """
        Get fix suggestions for a specific error category
        
        Args:
            error_category: The error category as string
            
        Returns:
            Dictionary with fix suggestions
        """
        try:
            category_enum = ErrorCategory(error_category)
            suggestions = self.fix_suggestions.get(category_enum, {
                "description": "Unknown error type",
                "suggestions": ["Review logs manually for more details"],
                "auto_fixable": False
            })
            logger.info(f"Generated fix suggestions for category: {error_category}")
            return suggestions
        except ValueError:
            logger.warning(f"Unknown error category: {error_category}")
            return {
                "description": "Unknown error type",
                "suggestions": ["Review logs manually for more details"],
                "auto_fixable": False
            }
    
    def generate_fix_report(self, analysis_result: Dict) -> Dict[str, any]:
        """
        Generate a comprehensive fix report based on log analysis
        
        Args:
            analysis_result: Result from LogAnalyzer.analyze_log()
            
        Returns:
            Dictionary with fix recommendations
        """
        report = {
            "total_errors": len(analysis_result.get("errors", [])),
            "categories": analysis_result.get("categories", []),
            "fixes": {},
            "auto_fixable_count": 0,
            "manual_review_count": 0
        }
        
        # Generate fixes for each category
        for category in analysis_result.get("categories", []):
            fix_info = self.get_fix_suggestions(category)
            report["fixes"][category] = fix_info
            
            if fix_info["auto_fixable"]:
                report["auto_fixable_count"] += 1
            else:
                report["manual_review_count"] += 1
        
        logger.info(f"Generated fix report: {report['auto_fixable_count']} auto-fixable, "
                   f"{report['manual_review_count']} require manual review")
        
        return report
    
    def suggest_dependency_fix(self, missing_module: str) -> str:
        """
        Suggest how to fix a missing dependency
        
        Args:
            missing_module: Name of the missing module
            
        Returns:
            Suggested fix as string
        """
        fix = f"""
To fix the missing dependency '{missing_module}':

1. Add to requirements.txt:
   {missing_module}

2. Update your workflow to install it:
   - name: Install Dependencies
     run: |
       pip install -r requirements.txt

3. Commit and push the changes
"""
        return fix.strip()
    
    def suggest_timeout_fix(self, current_timeout: Optional[int] = None) -> str:
        """
        Suggest how to fix timeout issues
        
        Args:
            current_timeout: Current timeout value in minutes
            
        Returns:
            Suggested fix as string
        """
        recommended_timeout = (current_timeout * 2) if current_timeout else 30
        
        fix = f"""
To fix timeout issues:

1. Increase the timeout in your workflow:
   jobs:
     your-job:
       timeout-minutes: {recommended_timeout}
       
2. Or for specific steps:
   - name: Your Step
     timeout-minutes: {recommended_timeout}
     run: your-command

3. Consider optimizing:
   - Use caching for dependencies
   - Split into parallel jobs
   - Remove unnecessary operations
"""
        return fix.strip()
    
    def suggest_permission_fix(self) -> str:
        """
        Suggest how to fix permission issues
        
        Returns:
            Suggested fix as string
        """
        fix = """
To fix permission issues:

1. Add permissions to your workflow:
   permissions:
     contents: write
     pull-requests: write
     issues: write

2. Or for specific jobs:
   jobs:
     your-job:
       permissions:
         contents: read

3. Verify repository settings:
   - Check if Actions have necessary permissions
   - Review organization/repository access policies
"""
        return fix.strip()
    
    def generate_workflow_fix(self, error_category: str, context: Dict = None) -> Optional[str]:
        """
        Generate specific workflow YAML fix based on error
        
        Args:
            error_category: The error category
            context: Additional context for generating the fix
            
        Returns:
            YAML snippet for the fix or None
        """
        try:
            category_enum = ErrorCategory(error_category)
            
            if category_enum == ErrorCategory.TIMEOUT_ERROR:
                return "timeout-minutes: 30  # Add this to job or step"
            
            elif category_enum == ErrorCategory.PERMISSION_ERROR:
                return """permissions:
  contents: write
  pull-requests: write"""
            
            elif category_enum == ErrorCategory.ENVIRONMENT_VARIABLE_MISSING:
                var_name = context.get("variable_name", "YOUR_VAR") if context else "YOUR_VAR"
                return f"""env:
  {var_name}: ${{{{ secrets.{var_name} }}}}  # Add your variable here"""
            
            else:
                return None
                
        except ValueError:
            return None
