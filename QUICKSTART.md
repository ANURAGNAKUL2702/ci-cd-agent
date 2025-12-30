# Quick Start Guide

Get started with the CI/CD Agent in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- A GitHub account
- A GitHub repository with Actions enabled

## Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/ANURAGNAKUL2702/ci-cd-agent.git
cd ci-cd-agent

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Setup GitHub Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token" > "Generate new token (classic)"
3. Give it a name like "CI/CD Agent"
4. Select these permissions:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

## Step 3: Configure Environment

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# Set your repository (format: owner/repo)
export GITHUB_REPOSITORY="username/repository-name"
```

Or create a `.env` file (don't commit it!):
```bash
cp .env.example .env
# Edit .env and add your values
```

## Step 4: Run Your First Analysis

### Analyze Failed Workflows

```bash
python ci_cd_agent.py analyze
```

This will:
- ✅ Fetch recent failed workflow runs
- ✅ Analyze error logs
- ✅ Categorize issues
- ✅ Generate fix recommendations
- ✅ Save detailed reports

### Validate a Workflow File

```bash
python ci_cd_agent.py validate .github/workflows/ci.yml
```

Output example:
```
✅ YAML syntax is valid
⚠️  Found 1 deprecated action
   actions/checkout@v2 → actions/checkout@v4
```

### Auto-fix Workflow Issues

```bash
python ci_cd_agent.py validate .github/workflows/ci.yml --fix
```

This will automatically:
- Fix YAML indentation
- Update deprecated actions
- Add missing required fields

## Step 5: Review Results

Analysis reports are saved as Markdown files:
```bash
ls -la workflow_analysis_*.md
cat workflow_analysis_12345.md
```

## Common Use Cases

### 1. Monitor CI/CD Health

Schedule regular checks:
```bash
# Run every hour
0 * * * * cd /path/to/ci-cd-agent && python ci_cd_agent.py analyze
```

### 2. Pre-commit Validation

Add to your pre-commit hook:
```bash
#!/bin/bash
python ci_cd_agent.py validate .github/workflows/*.yml
```

### 3. Automated PR Creation

After fixing issues, create a PR:
```python
from modules.github_integration import GitHubIntegration

github = GitHubIntegration(token, repo)
github.create_pull_request(
    title="Fix: Update deprecated actions",
    body="Automated fixes by CI/CD Agent",
    head_branch="fix/update-actions",
    base_branch="main"
)
```

## Error Categories

The agent detects these issue types:

| Category | Auto-fix | Example |
|----------|----------|---------|
| YAML Syntax Error | ✅ Yes | Indentation, missing colons |
| Missing Dependency | ✅ Yes | ModuleNotFoundError |
| Deprecated Action | ✅ Yes | actions/checkout@v1 |
| Timeout Error | ✅ Yes | Job exceeded time limit |
| Permission Error | ❌ Manual | Access denied, 403 |
| Test Failure | ❌ Manual | Assertion errors |

## Testing

Run the test suite to verify installation:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_log_analyzer.py -v

# Run with coverage
pytest tests/ --cov=modules --cov-report=html
```

Expected output:
```
================================ 36 passed in 0.10s ================================
```

## Troubleshooting

### "No module named 'modules'"

```bash
# Set PYTHONPATH before running
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python ci_cd_agent.py analyze
```

### "GITHUB_TOKEN not set"

```bash
# Make sure token is exported
echo $GITHUB_TOKEN

# Re-export if empty
export GITHUB_TOKEN="your_token"
```

### "Failed to fetch workflow runs"

Check:
1. Token has correct permissions
2. Repository name is correct format: `owner/repo`
3. You have access to the repository

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🧪 Explore the [tests/](tests/) directory for usage examples
- 🛠️ Check [modules/](modules/) for API reference
- 🤝 Contribute improvements via Pull Requests

## Need Help?

- 📝 [Open an issue](https://github.com/ANURAGNAKUL2702/ci-cd-agent/issues)
- 💬 Check existing issues for solutions
- 📚 Review code examples in tests/

Happy CI/CD fixing! 🚀
