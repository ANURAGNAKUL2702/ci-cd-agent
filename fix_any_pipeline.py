#!/usr/bin/env python3
"""
Simple Usage: Fix any CI/CD pipeline
"""

def fix_my_pipeline(file_path):
    """Fix any pipeline file with the production-grade CI/CD agent"""
    
    from enterprise_cicd_agent import EnterpriseGradeCICDAgent
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    agent = EnterpriseGradeCICDAgent()
    fixed_content = agent.fix_production_pipeline(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ {file_path} has been fixed and is production-ready!")

# Usage examples:
# fix_my_pipeline('.github/workflows/ci.yml')
# fix_my_pipeline('.github/workflows/deploy.yml') 
# fix_my_pipeline('azure-pipelines.yml')

if __name__ == "__main__":
    print("🚀 Production CI/CD Pipeline Fixer")
    print("Usage: fix_my_pipeline('path/to/your/workflow.yml')")
    print("Supports: GitHub Actions, Azure Pipelines, GitLab CI, Jenkins")
