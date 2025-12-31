#!/usr/bin/env python3
"""
In-place auto-correction test - fixes the original file directly
"""

from enterprise_cicd_agent import EnterpriseGradeCICDAgent
import yaml

def auto_correct_original_file():
    """Auto-correct the original production_pipeline_test.yml file in place"""
    
    filename = 'production_pipeline_test.yml'
    
    print("🤖 AUTO-CORRECTION SYSTEM - IN-PLACE FIXING")
    print("=" * 55)
    
    # Read original file
    with open(filename, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    print(f"📁 Target file: {filename}")
    print(f"📊 Original size: {len(original_content)} characters")
    
    # Check for errors before fixing
    errors_found = []
    if "ubuntu-lat" in original_content:
        errors_found.append("ubuntu-lat (runner error)")
    if "NODE_VERSIO" in original_content:
        errors_found.append("NODE_VERSIO (env var error)")
    if "actions/checkout@\n" in original_content or "actions/checkout@ " in original_content:
        errors_found.append("actions/checkout@ (missing version)")
    
    print(f"\n🔍 ERRORS DETECTED: {len(errors_found)}")
    for error in errors_found:
        print(f"   ❌ {error}")
    
    # Create agent and auto-correct
    agent = EnterpriseGradeCICDAgent()
    
    print(f"\n🔄 APPLYING AUTO-CORRECTION...")
    fixed_content = agent.fix_production_pipeline(original_content)
    
    # Write back to ORIGINAL file  
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"\n✅ ORIGINAL FILE AUTO-CORRECTED!")
    print(f"📊 Fixed size: {len(fixed_content)} characters")
    print(f"🔧 Total fixes: {len(agent.fixes_applied)}")
    
    # Verify YAML validity
    try:
        yaml.safe_load(fixed_content)
        print("✅ File is valid YAML")
    except yaml.YAMLError as e:
        print(f"❌ YAML error: {e}")
    
    # Show fixes applied
    print(f"\n🛠️ AUTO-CORRECTIONS APPLIED:")
    for i, fix in enumerate(agent.fixes_applied[:10], 1):  # Show first 10
        print(f"   {i:2d}. {fix}")
    if len(agent.fixes_applied) > 10:
        print(f"   ... and {len(agent.fixes_applied) - 10} more fixes")
    
    return len(agent.fixes_applied) > 0

if __name__ == "__main__":
    success = auto_correct_original_file()
    print(f"\n{'🎉 AUTO-CORRECTION SUCCESSFUL!' if success else '❌ No corrections needed'}")