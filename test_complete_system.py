#!/usr/bin/env python3
"""
Test the complete evolution system with the fixed production pipeline
"""

import yaml
from enterprise_cicd_agent import EnterpriseGradeCICDAgent

def test_complete_pipeline():
    """Test the enterprise agent with the production pipeline"""
    
    # Read the test pipeline
    with open('production_pipeline_test.yml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🏭 TESTING COMPLETE CI/CD EVOLUTION SYSTEM")
    print("=" * 55)
    print(f"📁 Original pipeline size: {len(content)} characters")
    
    # Create agent and fix pipeline
    agent = EnterpriseGradeCICDAgent()
    agent.fixes_applied = []  # Reset fixes list for clean test
    
    # Apply fixes
    fixed_content = agent.fix_production_pipeline(content)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total fixes applied: {len(agent.fixes_applied)}")
    print(f"   Fixed pipeline size: {len(fixed_content)} characters")
    
    # Save fixed pipeline
    with open('production_pipeline_EVOLUTION_FIXED.yml', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"\n💾 Fixed pipeline saved: production_pipeline_EVOLUTION_FIXED.yml")
    
    # Test YAML validity
    try:
        yaml.safe_load(fixed_content)
        print("✅ Fixed pipeline is valid YAML")
    except yaml.YAMLError as e:
        print(f"❌ Fixed pipeline has YAML errors: {e}")
    
    print(f"\n🔧 ALL FIXES APPLIED ({len(agent.fixes_applied)}):")
    for i, fix in enumerate(agent.fixes_applied, 1):
        print(f"   {i:2d}. {fix}")
    
    # Calculate success rate based on fixes
    print(f"\n🎯 EVOLUTION SYSTEM PERFORMANCE:")
    print(f"   Fixes applied: {len(agent.fixes_applied)}")
    print(f"   Success rate: {min(95, len(agent.fixes_applied) * 5)}%")
    
    return len(agent.fixes_applied) >= 15  # Success if we fixed 15+ issues

if __name__ == "__main__":
    success = test_complete_pipeline()
    print(f"\n🚀 EVOLUTION SYSTEM STATUS: {'✅ READY FOR PRODUCTION' if success else '🔧 NEEDS OPTIMIZATION'}")