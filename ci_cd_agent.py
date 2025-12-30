"""
CI/CD Agent - Main Entry Point
Analyzes, detects, and fixes damaged GitHub Actions pipelines
"""
import os
import sys
from typing import Dict, Optional
from loguru import logger

from modules.log_analyzer import LogAnalyzer
from modules.yaml_validator import YAMLValidator
from modules.error_fixer import ErrorFixer
from modules.github_integration import GitHubIntegration
from modules.reporter import Reporter


class CICDAgent:
    """Main CI/CD Agent class that orchestrates all modules"""
    
    def __init__(self, github_token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize the CI/CD Agent
        
        Args:
            github_token: GitHub personal access token
            repo_name: Repository name in format 'owner/repo'
        """
        self.github = GitHubIntegration(github_token, repo_name)
        self.log_analyzer = LogAnalyzer()
        self.yaml_validator = YAMLValidator()
        self.error_fixer = ErrorFixer()
        self.reporter = Reporter()
        
        logger.info("CI/CD Agent initialized")
    
    def analyze_failed_workflows(self, max_workflows: int = 5) -> None:
        """
        Analyze failed workflows and generate reports
        
        Args:
            max_workflows: Maximum number of failed workflows to analyze
        """
        logger.info("Starting workflow analysis...")
        
        # Fetch failed workflow runs
        failed_runs = self.github.get_workflow_runs(status="failure", max_results=max_workflows)
        
        if not failed_runs:
            logger.info("No failed workflows found")
            return
        
        logger.info(f"Found {len(failed_runs)} failed workflow(s)")
        
        # Analyze each failed workflow
        for workflow_info in failed_runs:
            logger.info(f"Analyzing workflow: {workflow_info['name']} (ID: {workflow_info['id']})")
            
            # Get workflow logs
            logs = self.github.get_workflow_logs(workflow_info['id'])
            
            if logs:
                # Analyze logs
                log_analysis = self.log_analyzer.analyze_log(logs)
                
                # Generate fix recommendations
                fix_report = self.error_fixer.generate_fix_report(log_analysis)
                
                # Generate and display report
                report = self.reporter.generate_analysis_report(
                    workflow_info, log_analysis, fix_report
                )
                
                logger.info(f"\n{report}")
                
                # Save report to file
                report_filename = f"workflow_analysis_{workflow_info['id']}.md"
                with open(report_filename, 'w') as f:
                    f.write(report)
                logger.info(f"Report saved to {report_filename}")
    
    def validate_workflow_yaml(self, yaml_file_path: str, apply_fixes: bool = False) -> Dict:
        """
        Validate and optionally fix a workflow YAML file
        
        Args:
            yaml_file_path: Path to the YAML file
            apply_fixes: Whether to apply fixes automatically
            
        Returns:
            Validation result dictionary
        """
        logger.info(f"Validating YAML file: {yaml_file_path}")
        
        try:
            with open(yaml_file_path, 'r') as f:
                yaml_content = f.read()
            
            # Validate and get fix suggestions
            result = self.yaml_validator.validate_and_fix(yaml_content)
            
            # Generate validation report
            report = self.reporter.generate_yaml_validation_report(result)
            logger.info(f"\n{report}")
            
            # Apply fixes if requested
            if apply_fixes and result['fixed_content'] != result['original_content']:
                with open(yaml_file_path, 'w') as f:
                    f.write(result['fixed_content'])
                logger.info(f"Fixes applied to {yaml_file_path}")
            
            return result
            
        except FileNotFoundError:
            logger.error(f"File not found: {yaml_file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error validating YAML: {e}")
            return {}
    
    def create_fix_pr(
        self,
        workflow_info: Dict,
        fixes_applied: list,
        head_branch: str,
        base_branch: str = "main"
    ) -> Optional[Dict]:
        """
        Create a pull request with proposed fixes
        
        Args:
            workflow_info: Information about the failed workflow
            fixes_applied: List of fixes that were applied
            head_branch: Branch with fixes
            base_branch: Target branch
            
        Returns:
            PR information or None
        """
        title = f"Fix CI/CD pipeline issues from workflow run #{workflow_info.get('id')}"
        body = self.reporter.generate_pr_description(workflow_info, fixes_applied)
        
        return self.github.create_pull_request(title, body, head_branch, base_branch)
    
    def create_error_issue(
        self,
        workflow_info: Dict,
        log_analysis: Dict,
        fix_report: Dict
    ) -> Optional[Dict]:
        """
        Create an issue for errors requiring manual review
        
        Args:
            workflow_info: Information about the failed workflow
            log_analysis: Log analysis results
            fix_report: Fix report results
            
        Returns:
            Issue information or None
        """
        title = f"CI/CD Pipeline Failure: {workflow_info.get('name')} #{workflow_info.get('id')}"
        body = self.reporter.generate_issue_description(workflow_info, log_analysis, fix_report)
        labels = ["ci-cd", "automated-detection"]
        
        return self.github.create_issue(title, body, labels)


def main():
    """Main entry point for the CI/CD Agent"""
    # Configure logging
    logger.add(
        "cicd_agent.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )
    
    # Get configuration from environment variables
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    
    if not github_token:
        logger.warning("GITHUB_TOKEN not set. Using limited functionality.")
    
    if not repo_name:
        logger.warning("GITHUB_REPOSITORY not set. Some features may not work.")
    
    # Initialize agent
    agent = CICDAgent(github_token, repo_name)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "analyze":
            # Analyze failed workflows
            agent.analyze_failed_workflows()
        
        elif command == "validate" and len(sys.argv) > 2:
            # Validate a specific YAML file
            yaml_file = sys.argv[2]
            apply_fixes = "--fix" in sys.argv
            agent.validate_workflow_yaml(yaml_file, apply_fixes)
        
        else:
            logger.error(f"Unknown command: {command}")
            print_usage()
    else:
        # Default: analyze failed workflows
        agent.analyze_failed_workflows()


def print_usage():
    """Print usage information"""
    usage = """
CI/CD Agent - GitHub Actions Pipeline Analyzer and Fixer

Usage:
    python ci_cd_agent.py [command] [options]

Commands:
    analyze              Analyze failed workflow runs (default)
    validate <file>      Validate a workflow YAML file
    validate <file> --fix    Validate and apply fixes to a workflow YAML file

Environment Variables:
    GITHUB_TOKEN        GitHub personal access token (required for most operations)
    GITHUB_REPOSITORY   Repository name in format 'owner/repo'

Examples:
    python ci_cd_agent.py analyze
    python ci_cd_agent.py validate .github/workflows/ci.yml
    python ci_cd_agent.py validate .github/workflows/ci.yml --fix
"""
    print(usage)


if __name__ == "__main__":
    main()