import requests
from github import Github
from loguru import logger

# Authentication token for GitHub
GITHUB_TOKEN = "your_personal_access_token"
REPO_NAME = "your_username/ci-cd-agent"

# Initialize the GitHub API client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def get_failed_workflows():
    """Fetch failing workflows from the repository."""
    logger.info("Fetching workflow runs...")
    workflows = repo.get_workflow_runs(status='failure')  # Get only failed runs
    for workflow in workflows:
        logger.info(f"Found failed workflow: {workflow.name}")
        analyze_error_logs(workflow)

def analyze_error_logs(workflow):
    """Analyze error logs to identify issues."""
    logger.info(f"Analyzing logs for workflow: {workflow.name}")
    logs_url = workflow.logs_url
    response = requests.get(logs_url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
    if response.status_code == 200:
        log_content = response.text
        logger.info("Logs fetched successfully!")
        # Basic analysis: Look for common errors
        if "ModuleNotFoundError" in log_content:
            fix_missing_dependency()
        elif "YAML syntax" in log_content:
            logger.info("Pipeline YAML has syntax issues.")
        else:
            logger.warning("Unknown error type.")
    else:
        logger.error("Failed to fetch logs.")

def fix_missing_dependency():
    """Apply a fix for a missing dependency issue."""
    logger.info("Fixing missing dependency...")
    try:
        with open("requirements.txt", "a") as f:
            f.write("\nnew_dependency\n")  # Example addition
        repo.update_file("requirements.txt", "Added missing dependency", "new_dependency", repo.get_contents("requirements.txt").sha)
        logger.info("Dependency fix pushed to repository.")
    except Exception as e:
        logger.error(f"Failed to apply fix: {str(e)}")

if __name__ == "__main__":
    get_failed_workflows()