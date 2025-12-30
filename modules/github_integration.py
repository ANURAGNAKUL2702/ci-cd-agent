"""
GitHub Integration Module
Handles GitHub API interactions for workflow monitoring and PR creation
"""
import os
from typing import Dict, List, Optional, Tuple
from github import Github, GithubException
from loguru import logger
import requests


class GitHubIntegration:
    """Manages GitHub API interactions"""
    
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize GitHub API client
        
        Args:
            token: GitHub personal access token (or from environment)
            repo_name: Repository name in format 'owner/repo'
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.repo_name = repo_name or os.environ.get("GITHUB_REPOSITORY")
        
        if not self.token:
            logger.warning("No GitHub token provided. Some operations may fail.")
            self.github = None
            self.repo = None
        else:
            try:
                self.github = Github(self.token)
                if self.repo_name:
                    self.repo = self.github.get_repo(self.repo_name)
                    logger.info(f"Connected to repository: {self.repo_name}")
                else:
                    self.repo = None
                    logger.warning("No repository name provided")
            except GithubException as e:
                logger.error(f"Failed to initialize GitHub client: {e}")
                self.github = None
                self.repo = None
    
    def get_workflow_runs(self, status: str = "failure", max_results: int = 10) -> List[Dict]:
        """
        Fetch workflow runs from the repository
        
        Args:
            status: Filter by status (failure, success, in_progress, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of workflow run information
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return []
        
        try:
            runs = self.repo.get_workflow_runs(status=status)
            results = []
            
            for i, run in enumerate(runs):
                if i >= max_results:
                    break
                
                results.append({
                    "id": run.id,
                    "name": run.name,
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "head_branch": run.head_branch,
                    "head_sha": run.head_sha,
                    "created_at": run.created_at.isoformat() if run.created_at else None,
                    "updated_at": run.updated_at.isoformat() if run.updated_at else None,
                    "html_url": run.html_url,
                    "logs_url": run.logs_url
                })
            
            logger.info(f"Retrieved {len(results)} workflow run(s) with status '{status}'")
            return results
            
        except GithubException as e:
            logger.error(f"Failed to fetch workflow runs: {e}")
            return []
    
    def get_workflow_logs(self, run_id: int) -> Optional[str]:
        """
        Fetch logs for a specific workflow run
        
        Args:
            run_id: The workflow run ID
            
        Returns:
            Log content as string or None if failed
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return None
        
        try:
            run = self.repo.get_workflow_run(run_id)
            logs_url = run.logs_url
            
            # Download logs using requests
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(logs_url, headers=headers, allow_redirects=True)
            
            if response.status_code == 200:
                logger.info(f"Successfully fetched logs for run {run_id}")
                # Note: GitHub API returns logs as a zip archive
                # For production use, you would extract and parse the zip file
                # For now, returning the raw content as text for basic analysis
                return response.text
            else:
                logger.error(f"Failed to fetch logs: HTTP {response.status_code}")
                return None
                
        except (GithubException, requests.RequestException) as e:
            logger.error(f"Failed to fetch workflow logs: {e}")
            return None
    
    def get_workflow_jobs(self, run_id: int) -> List[Dict]:
        """
        Get jobs for a specific workflow run
        
        Args:
            run_id: The workflow run ID
            
        Returns:
            List of job information
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return []
        
        try:
            run = self.repo.get_workflow_run(run_id)
            jobs = run.jobs()
            
            results = []
            for job in jobs:
                results.append({
                    "id": job.id,
                    "name": job.name,
                    "status": job.status,
                    "conclusion": job.conclusion,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "steps": [
                        {
                            "name": step.name,
                            "status": step.status,
                            "conclusion": step.conclusion,
                            "number": step.number
                        }
                        for step in job.steps
                    ]
                })
            
            logger.info(f"Retrieved {len(results)} job(s) for run {run_id}")
            return results
            
        except GithubException as e:
            logger.error(f"Failed to fetch workflow jobs: {e}")
            return []
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Optional[Dict]:
        """
        Create a pull request with proposed fixes
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch with fixes
            base_branch: Target branch (default: main)
            
        Returns:
            PR information or None if failed
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return None
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            result = {
                "number": pr.number,
                "html_url": pr.html_url,
                "title": pr.title,
                "state": pr.state
            }
            
            logger.info(f"Created PR #{pr.number}: {title}")
            return result
            
        except GithubException as e:
            logger.error(f"Failed to create pull request: {e}")
            return None
    
    def update_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: Optional[str] = None
    ) -> bool:
        """
        Update a file in the repository
        
        Args:
            file_path: Path to the file in repository
            content: New file content
            commit_message: Commit message
            branch: Branch to commit to (None for default)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return False
        
        try:
            # Get current file to get its SHA
            file = self.repo.get_contents(file_path, ref=branch)
            
            # Update the file
            self.repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=file.sha,
                branch=branch
            )
            
            logger.info(f"Updated file: {file_path}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to update file: {e}")
            return False
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Create an issue for error reporting
        
        Args:
            title: Issue title
            body: Issue description
            labels: List of label names
            
        Returns:
            Issue information or None if failed
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return None
        
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            
            result = {
                "number": issue.number,
                "html_url": issue.html_url,
                "title": issue.title,
                "state": issue.state
            }
            
            logger.info(f"Created issue #{issue.number}: {title}")
            return result
            
        except GithubException as e:
            logger.error(f"Failed to create issue: {e}")
            return None
    
    def add_comment_to_pr(self, pr_number: int, comment: str) -> bool:
        """
        Add a comment to a pull request
        
        Args:
            pr_number: PR number
            comment: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return False
        
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            logger.info(f"Added comment to PR #{pr_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to add comment to PR: {e}")
            return False
