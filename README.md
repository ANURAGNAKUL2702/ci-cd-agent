# CI/CD Agent 🤖

An AI-powered agent that automatically analyzes, detects, and fixes GitHub Actions pipeline issues.

## 🌟 Features

- **Log Analysis**: Parse and categorize errors from failed GitHub Actions workflows
- **YAML Validation**: Validate and auto-fix workflow YAML files
- **Intelligent Error Detection**: Identify common issues like:
  - Missing dependencies
  - YAML syntax errors
  - Deprecated actions
  - Permission errors
  - Timeout issues
  - Missing environment variables/secrets
  - Version mismatches
- **Automated Fixes**: Apply automatic fixes where possible
- **GitHub Integration**: 
  - Fetch workflow runs and logs via GitHub API
  - Create pull requests with fixes
  - Create issues for manual review
- **Comprehensive Reporting**: Generate detailed Markdown reports

## 📋 Requirements

- Python 3.9+
- GitHub Personal Access Token with appropriate permissions

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/ANURAGNAKUL2702/ci-cd-agent.git
cd ci-cd-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPOSITORY="owner/repo"
```

## 💻 Usage

### Analyze Failed Workflows

Analyze recent failed workflow runs in your repository:

```bash
python ci_cd_agent.py analyze
```

This will:
- Fetch failed workflow runs
- Analyze error logs
- Generate fix recommendations
- Save detailed reports

### Validate Workflow YAML

Validate a workflow file for syntax and structural issues:

```bash
python ci_cd_agent.py validate .github/workflows/ci.yml
```

To automatically apply fixes:

```bash
python ci_cd_agent.py validate .github/workflows/ci.yml --fix
```

## 🏗️ Architecture

The agent is built with a modular architecture:

```
ci-cd-agent/
├── ci_cd_agent.py          # Main entry point
├── modules/
│   ├── log_analyzer.py     # Log parsing and error categorization
│   ├── yaml_validator.py   # YAML validation and auto-fixing
│   ├── error_fixer.py      # Error fix suggestions
│   ├── github_integration.py  # GitHub API interactions
│   └── reporter.py         # Report generation
└── tests/                  # Unit tests
```

### Modules

#### LogAnalyzer
- Parses workflow logs
- Categorizes errors using regex patterns
- Extracts error context

#### YAMLValidator
- Validates YAML syntax
- Checks workflow structure
- Detects deprecated actions
- Auto-fixes common issues

#### ErrorFixer
- Generates fix suggestions based on error categories
- Provides auto-fix recommendations
- Creates workflow snippets for fixes

#### GitHubIntegration
- Fetches workflow runs and logs
- Creates pull requests
- Creates issues
- Updates files in repository

#### Reporter
- Generates analysis reports
- Creates PR descriptions
- Creates issue descriptions
- Formats output as Markdown

## 🔍 Error Categories

The agent can detect and categorize the following error types:

- `yaml_syntax_error` - YAML syntax issues
- `missing_dependency` - Missing Python packages or dependencies
- `invalid_action` - Invalid or non-existent GitHub Actions
- `deprecated_action` - Deprecated action versions
- `permission_error` - Access or permission issues
- `timeout_error` - Job or step timeouts
- `environment_variable_missing` - Missing environment variables
- `secret_missing` - Missing secrets
- `version_mismatch` - Version incompatibilities
- `build_error` - Build or compilation failures
- `test_failure` - Test failures

## 📊 Example Output

### Analysis Report

```markdown
# CI/CD Pipeline Analysis Report

**Generated:** 2025-12-30 17:30:00

## Workflow Information
- **Workflow:** CI Pipeline
- **Run ID:** 12345
- **Status:** completed
- **Conclusion:** failure

## Analysis Summary
- **Total Errors Found:** 3
- **Auto-fixable Issues:** 2
- **Manual Review Required:** 1

## Error Categories Detected
- `missing_dependency`
- `deprecated_action`

## Fix Recommendations

### Missing Dependency
🔧 Auto-fixable

**Description:** Missing Python module or dependency

**Suggestions:**
1. Add the missing package to requirements.txt
2. Update the 'Install Dependencies' step in your workflow
3. Verify package name spelling
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=modules --cov-report=html
```

## 🔐 Security

- Never commit your GitHub token to the repository
- Use environment variables or GitHub Secrets for sensitive data
- The agent only analyzes and suggests fixes; manual review is recommended

## 🛠️ Configuration

Set the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes |
| `GITHUB_REPOSITORY` | Repository in format `owner/repo` | Yes |

### GitHub Token Permissions

Your token needs the following permissions:
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows
- `read:org` - Read organization data (if analyzing org repos)

## 📚 API Reference

### CICDAgent Class

Main agent class that orchestrates all modules.

```python
agent = CICDAgent(github_token, repo_name)

# Analyze failed workflows
agent.analyze_failed_workflows(max_workflows=5)

# Validate YAML file
result = agent.validate_workflow_yaml(yaml_file_path, apply_fixes=True)

# Create fix PR
pr = agent.create_fix_pr(workflow_info, fixes_applied, head_branch)

# Create error issue
issue = agent.create_error_issue(workflow_info, log_analysis, fix_report)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure to run from the project root with PYTHONPATH set
PYTHONPATH=. python ci_cd_agent.py
```

**GitHub API Rate Limiting**
- Use an authenticated token to increase rate limits
- Reduce the number of workflow runs analyzed

**Missing Logs**
- Logs are only available for a limited time
- Ensure workflow runs are recent

## 📞 Support

For issues, questions, or contributions, please:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## 🎯 Roadmap

- [ ] Add support for more CI/CD platforms (GitLab CI, CircleCI)
- [ ] Implement machine learning for better error detection
- [ ] Add webhook listener for real-time monitoring
- [ ] Create web dashboard for visualization
- [ ] Add support for more programming languages
- [ ] Implement fix verification before applying changes

## ✨ Acknowledgments

Built with:
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API wrapper
- [PyYAML](https://pyyaml.org/) - YAML parser
- [Loguru](https://github.com/Delgan/loguru) - Logging library
- [Pytest](https://pytest.org/) - Testing framework
