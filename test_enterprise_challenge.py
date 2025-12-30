#!/usr/bin/env python3
"""
Test script to analyze the broken enterprise pipeline and show agent capabilities
"""

from enterprise_cicd_agent import EnterpriseGradeCICDAgent
import yaml

def analyze_broken_pipeline():
    """Analyze the broken enterprise pipeline"""
    
    print("🏭 ENTERPRISE PIPELINE CHALLENGE")
    print("Testing with Fortune 500 grade production pipeline")
    print("=" * 65)
    
    # Read the broken pipeline
    with open('broken_enterprise_pipeline.yml', 'r') as f:
        broken_content = f.read()
    
    print("📋 Broken Pipeline Analysis:")
    print(f"   Lines of code: {len(broken_content.splitlines())}")
    print(f"   File size: {len(broken_content)} characters")
    
    # Count issues manually
    issues = [
        "'on':", "ubuntu-lat", "actions/checkt", "actions/checkout@",
        "gitleaks/gitleaks-action@v", "aquasecurity/trivy-action@",
        "dependency-check/Dependency-Check_Action@", "actions/setup-node@",
        "actions/setup-python@", "NODE_VERSIO", "PYTHON_VERSIO", "REGISTR",
        "IMAGE_NAM", "TERRAFORM_VERSIO", "KUBECTL_VERSIO", "HELM_VERSIO",
        "requirement.txt", "requir.txt", "PYTHONPTH", "matrix.analysis =",
        "needs.security-gate.outputs.security-passed =", "github.ref =",
        "github.event_name =", "timeout:", "actions/cache@", "actions/setup-java@",
        "docker/setup-buildx-action@", "docker/login-action@", "docker/build-push-action@",
        "hashicorp/setup-terraform@", "anchore/sbom-action@", "actions/upload-artifact@",
        "permissions: write-all"
    ]
    
    issues_found = [issue for issue in issues if issue in broken_content]
    
    print(f"   Known issues: {len(issues_found)}")
    print("   Pipeline complexity: ENTERPRISE GRADE")
    print("   Features:")
    print("     ✅ Multi-cloud deployment (AWS, Azure, GCP)")
    print("     ✅ Security scanning (Trivy, GitLeaks, OWASP)")
    print("     ✅ Matrix builds (OS, Node, Python, Java)")
    print("     ✅ Performance testing (K6, Artillery)")
    print("     ✅ Blue-green deployments")
    print("     ✅ Kubernetes + Helm")
    print("     ✅ Infrastructure as Code (Terraform)")
    print("     ✅ Compliance reporting (SBOM, SOC2)")
    print()
    
    # Test our agent
    print("🤖 Testing Enterprise CI/CD Agent...")
    agent = EnterpriseGradeCICDAgent()
    
    try:
        fixed_content = agent.fix_production_pipeline(broken_content)
        
        # Count remaining issues
        issues_remaining = [issue for issue in issues if issue in fixed_content]
        issues_fixed = len(issues_found) - len(issues_remaining)
        success_rate = (issues_fixed / len(issues_found) * 100) if issues_found else 0
        
        print(f"\n📊 Enterprise Agent Results:")
        print(f"   Issues detected: {len(issues_found)}")
        print(f"   Issues fixed: {issues_fixed}")
        print(f"   Issues remaining: {len(issues_remaining)}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        if len(issues_remaining) > 0:
            print(f"\n   Remaining issues:")
            for issue in issues_remaining[:5]:  # Show first 5
                print(f"     ❌ {issue}")
        
        # Validate YAML
        try:
            yaml.safe_load(fixed_content)
            print(f"   ✅ YAML syntax: VALID")
        except yaml.YAMLError as e:
            print(f"   ❌ YAML syntax: INVALID ({e})")
        
        # Save fixed version
        with open('fixed_enterprise_pipeline.yml', 'w') as f:
            f.write(fixed_content)
        
        print(f"\n💾 Fixed pipeline saved as: fixed_enterprise_pipeline.yml")
        
        if success_rate >= 80:
            print("\n🎊 SUCCESS: Agent handles enterprise-grade pipelines!")
            return True
        else:
            print("\n⚠️  Agent needs more work for full enterprise readiness")
            return False
            
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        return False

def show_pipeline_features():
    """Show what makes this an enterprise-grade pipeline"""
    
    print("\n🏢 ENTERPRISE FEATURES IN THIS PIPELINE:")
    print("=" * 50)
    
    features = [
        "🔒 Multi-layer Security Scanning",
        "   - GitLeaks secret detection",
        "   - Trivy vulnerability scanning", 
        "   - OWASP dependency check",
        "   - Container security scanning",
        "   - Snyk security analysis",
        "",
        "🎯 Comprehensive Testing Strategy",
        "   - Matrix builds across OS/languages",
        "   - Unit, integration, performance tests",
        "   - K6 load testing",
        "   - Artillery performance testing",
        "   - Database benchmarking",
        "",
        "☁️ Multi-Cloud Infrastructure",
        "   - AWS, Azure, GCP support",
        "   - Terraform Infrastructure as Code",
        "   - Multi-region deployments",
        "   - Blue-green deployment strategy",
        "",
        "⚙️ Production Operations",
        "   - Kubernetes orchestration",
        "   - Helm package management", 
        "   - Database migrations",
        "   - Health checks & monitoring",
        "   - Compliance reporting (SOC2)",
        "   - Software Bill of Materials (SBOM)",
        "",
        "📊 Enterprise Governance",
        "   - Environment approvals",
        "   - Workflow dispatch controls",
        "   - Scheduled security scans",
        "   - Audit trail & compliance",
        "   - Proper RBAC permissions"
    ]
    
    for feature in features:
        print(f"   {feature}")

if __name__ == "__main__":
    success = analyze_broken_pipeline()
    show_pipeline_features()
    
    print(f"\n🎯 CHALLENGE READY!")
    print(f"   File: broken_enterprise_pipeline.yml")
    print(f"   Complexity: Fortune 500 Enterprise Grade")
    print(f"   Test your agent: python fix_any_pipeline.py")
    print(f"   Agent readiness: {'✅ PRODUCTION READY' if success else '❌ NEEDS ENHANCEMENT'}")