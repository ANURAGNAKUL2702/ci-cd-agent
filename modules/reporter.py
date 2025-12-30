"""
Reporter Module
Generates detailed reports on detected issues and applied fixes
"""
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class Reporter:
    """Generates reports for CI/CD pipeline analysis and fixes"""
    
    def __init__(self):
        self.report_timestamp = datetime.now()
    
    def generate_analysis_report(
        self,
        workflow_info: Dict,
        log_analysis: Dict,
        fix_report: Dict
    ) -> str:
        """
        Generate a comprehensive analysis report
        
        Args:
            workflow_info: Information about the workflow run
            log_analysis: Result from LogAnalyzer
            fix_report: Result from ErrorFixer
            
        Returns:
            Formatted report as string (Markdown)
        """
        report_lines = [
            "# CI/CD Pipeline Analysis Report",
            "",
            f"**Generated:** {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Workflow Information",
            f"- **Workflow:** {workflow_info.get('name', 'N/A')}",
            f"- **Run ID:** {workflow_info.get('id', 'N/A')}",
            f"- **Status:** {workflow_info.get('status', 'N/A')}",
            f"- **Conclusion:** {workflow_info.get('conclusion', 'N/A')}",
            f"- **Branch:** {workflow_info.get('head_branch', 'N/A')}",
            f"- **Commit:** {workflow_info.get('head_sha', 'N/A')[:7] if workflow_info.get('head_sha') else 'N/A'}",
            "",
            "## Analysis Summary",
            f"- **Total Errors Found:** {fix_report.get('total_errors', 0)}",
            f"- **Auto-fixable Issues:** {fix_report.get('auto_fixable_count', 0)}",
            f"- **Manual Review Required:** {fix_report.get('manual_review_count', 0)}",
            "",
        ]
        
        # Add error categories
        if log_analysis.get("categories"):
            report_lines.extend([
                "## Error Categories Detected",
                ""
            ])
            for category in log_analysis["categories"]:
                report_lines.append(f"- `{category}`")
            report_lines.append("")
        
        # Add fix suggestions
        if fix_report.get("fixes"):
            report_lines.extend([
                "## Fix Recommendations",
                ""
            ])
            
            for category, fix_info in fix_report["fixes"].items():
                auto_fix_badge = "🔧 Auto-fixable" if fix_info["auto_fixable"] else "👁️ Manual Review"
                report_lines.extend([
                    f"### {category.replace('_', ' ').title()}",
                    f"**{auto_fix_badge}**",
                    "",
                    f"**Description:** {fix_info['description']}",
                    "",
                    "**Suggestions:**"
                ])
                
                for i, suggestion in enumerate(fix_info["suggestions"], 1):
                    report_lines.append(f"{i}. {suggestion}")
                
                report_lines.append("")
        
        # Add error details
        if log_analysis.get("errors"):
            report_lines.extend([
                "## Error Details",
                "",
                "| Line | Category | Content |",
                "|------|----------|---------|"
            ])
            
            for error in log_analysis["errors"][:10]:  # Limit to first 10
                line_num = error.get("line_number", "?")
                category = error.get("category", "unknown")
                content = error.get("line_content", "")[:100]  # Truncate long lines
                report_lines.append(f"| {line_num} | {category} | {content} |")
            
            if len(log_analysis["errors"]) > 10:
                report_lines.append(f"\n*...and {len(log_analysis['errors']) - 10} more errors*")
            
            report_lines.append("")
        
        report = "\n".join(report_lines)
        logger.info("Generated analysis report")
        return report
    
    def generate_yaml_validation_report(self, validation_result: Dict) -> str:
        """
        Generate a report for YAML validation results
        
        Args:
            validation_result: Result from YAMLValidator.validate_and_fix()
            
        Returns:
            Formatted report as string (Markdown)
        """
        report_lines = [
            "# YAML Validation Report",
            "",
            f"**Generated:** {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Validation Status",
            f"- **Original Valid:** {'✅ Yes' if validation_result['original_valid'] else '❌ No'}",
            f"- **Fixed Valid:** {'✅ Yes' if validation_result['fixed_valid'] else '❌ No'}",
            "",
        ]
        
        # Add issues if any
        if validation_result.get("issues"):
            report_lines.extend([
                "## Issues Found",
                ""
            ])
            for issue in validation_result["issues"]:
                report_lines.append(f"- {issue}")
            report_lines.append("")
        
        # Add deprecated actions
        if validation_result.get("deprecated_actions"):
            report_lines.extend([
                "## Deprecated Actions",
                ""
            ])
            for dep in validation_result["deprecated_actions"]:
                report_lines.append(f"- ⚠️ `{dep['deprecated']}` → `{dep['replacement']}`")
                report_lines.append(f"  - {dep['message']}")
            report_lines.append("")
        
        # Add fixes applied
        if validation_result.get("fixes_applied"):
            report_lines.extend([
                "## Fixes Applied",
                ""
            ])
            for fix in validation_result["fixes_applied"]:
                report_lines.append(f"- ✅ {fix}")
            report_lines.append("")
        
        report = "\n".join(report_lines)
        logger.info("Generated YAML validation report")
        return report
    
    def generate_pr_description(
        self,
        workflow_info: Dict,
        fixes_applied: List[str],
        validation_result: Optional[Dict] = None
    ) -> str:
        """
        Generate a pull request description for proposed fixes
        
        Args:
            workflow_info: Information about the workflow run
            fixes_applied: List of fixes that were applied
            validation_result: Optional YAML validation result
            
        Returns:
            PR description as string (Markdown)
        """
        pr_lines = [
            "# 🤖 Automated CI/CD Pipeline Fix",
            "",
            "This PR contains automated fixes for issues detected in the CI/CD pipeline.",
            "",
            "## 📋 Workflow Information",
            f"- **Failed Workflow:** {workflow_info.get('name', 'N/A')}",
            f"- **Run ID:** {workflow_info.get('id', 'N/A')}",
            f"- **Branch:** {workflow_info.get('head_branch', 'N/A')}",
            "",
            "## 🔧 Fixes Applied",
            ""
        ]
        
        if fixes_applied:
            for fix in fixes_applied:
                pr_lines.append(f"- {fix}")
        else:
            pr_lines.append("- No automatic fixes were applied")
        
        pr_lines.append("")
        
        # Add YAML validation info if available
        if validation_result:
            if validation_result.get("deprecated_actions"):
                pr_lines.extend([
                    "## 📦 Action Updates",
                    ""
                ])
                for dep in validation_result["deprecated_actions"]:
                    pr_lines.append(f"- Updated `{dep['deprecated']}` to `{dep['replacement']}`")
                pr_lines.append("")
        
        pr_lines.extend([
            "## ✅ Review Checklist",
            "",
            "- [ ] Review all changes carefully",
            "- [ ] Verify fixes address the root cause",
            "- [ ] Test the workflow after merging",
            "- [ ] Check for any breaking changes",
            "",
            "---",
            "*This PR was generated automatically by the CI/CD Agent*"
        ])
        
        pr_description = "\n".join(pr_lines)
        logger.info("Generated PR description")
        return pr_description
    
    def generate_issue_description(
        self,
        workflow_info: Dict,
        log_analysis: Dict,
        fix_report: Dict
    ) -> str:
        """
        Generate an issue description for errors requiring manual review
        
        Args:
            workflow_info: Information about the workflow run
            log_analysis: Result from LogAnalyzer
            fix_report: Result from ErrorFixer
            
        Returns:
            Issue description as string (Markdown)
        """
        issue_lines = [
            "# 🚨 CI/CD Pipeline Failure Detected",
            "",
            "The CI/CD agent detected failures that require manual review.",
            "",
            "## 📋 Workflow Information",
            f"- **Workflow:** {workflow_info.get('name', 'N/A')}",
            f"- **Run ID:** {workflow_info.get('id', 'N/A')}",
            f"- **Status:** {workflow_info.get('status', 'N/A')}",
            f"- **URL:** {workflow_info.get('html_url', 'N/A')}",
            "",
            "## 🔍 Analysis Summary",
            f"- **Total Errors:** {fix_report.get('total_errors', 0)}",
            f"- **Manual Review Required:** {fix_report.get('manual_review_count', 0)}",
            "",
        ]
        
        # Add categories requiring manual review
        if fix_report.get("fixes"):
            manual_fixes = [
                (cat, info) for cat, info in fix_report["fixes"].items()
                if not info["auto_fixable"]
            ]
            
            if manual_fixes:
                issue_lines.extend([
                    "## 👁️ Issues Requiring Manual Review",
                    ""
                ])
                
                for category, fix_info in manual_fixes:
                    issue_lines.extend([
                        f"### {category.replace('_', ' ').title()}",
                        f"{fix_info['description']}",
                        "",
                        "**Recommended Actions:**"
                    ])
                    
                    for suggestion in fix_info["suggestions"]:
                        issue_lines.append(f"- {suggestion}")
                    
                    issue_lines.append("")
        
        issue_lines.extend([
            "---",
            "*This issue was generated automatically by the CI/CD Agent*"
        ])
        
        issue_description = "\n".join(issue_lines)
        logger.info("Generated issue description")
        return issue_description
