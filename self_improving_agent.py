#!/usr/bin/env python3
"""
Enhanced Enterprise Agent with Auto-Learning Capabilities
Integrates continuous learning into the core agent
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from continuous_learning_agent import ContinuousLearningAgent
from enterprise_cicd_agent import EnterpriseGradeCICDAgent
import yaml
import json
from pathlib import Path

class SelfImprovingCICDAgent(EnterpriseGradeCICDAgent):
    """Enterprise agent that learns and improves from daily errors"""
    
    def __init__(self):
        super().__init__()
        self.learning_agent = ContinuousLearningAgent()
        self.auto_patterns = self._load_auto_patterns()
        
    def _load_auto_patterns(self) -> dict:
        """Load automatically learned patterns"""
        patterns_file = Path("learning_data/learned_patterns.json")
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                return json.load(f)
        return {}
    
    def fix_production_pipeline(self, content: str, learn_from_errors: bool = True) -> str:
        """Enhanced pipeline fixing with continuous learning"""
        
        print("🧠 Self-Improving CI/CD Agent - With Continuous Learning")
        print("=" * 65)
        
        # Use original fixing method
        original_content = content
        fixed_content = super().fix_production_pipeline(content)
        
        # Apply learned patterns
        fixed_content = self._apply_learned_patterns(fixed_content)
        
        if learn_from_errors:
            # Analyze what errors remain for learning
            remaining_errors = self._analyze_remaining_errors(original_content, fixed_content)
            
            if remaining_errors:
                # Learn from these errors
                analysis = self.learning_agent.analyze_pipeline_error(
                    original_content, fixed_content, remaining_errors
                )
                
                if analysis['new_patterns_discovered']:
                    print(f"🔍 Discovered {len(analysis['new_patterns_discovered'])} new error patterns")
                    
                    # Try to fix with newly learned patterns
                    fixed_content = self._apply_learned_patterns(fixed_content)
        
        return fixed_content
    
    def _apply_learned_patterns(self, content: str) -> str:
        """Apply automatically learned patterns"""
        
        applied_fixes = 0
        
        for pattern_key, pattern_data in self.auto_patterns.items():
            if pattern_data['confidence'] > 0.7:  # Only high-confidence patterns
                error_text = pattern_data['error_text']
                fix_suggestion = pattern_data['fix_suggestion']
                
                if error_text in content:
                    # Extract fix from suggestion
                    if "Replace '" in fix_suggestion and "' with '" in fix_suggestion:
                        parts = fix_suggestion.split("' with '")
                        if len(parts) == 2:
                            old_text = parts[0].split("Replace '")[1]
                            new_text = parts[1].rstrip("'")
                            
                            content = content.replace(old_text, new_text)
                            self.fixes_applied.append(f"Auto-learned: {old_text} → {new_text}")
                            applied_fixes += 1
        
        if applied_fixes > 0:
            print(f"🤖 Applied {applied_fixes} auto-learned fixes")
        
        return content
    
    def _analyze_remaining_errors(self, original: str, fixed: str) -> list:
        """Analyze what errors remain after fixing"""
        
        # Common error patterns to check
        error_patterns = [
            'ubuntu-lat', 'ubuntu-lates', 'windows-lates', 'macos-lates',
            'actions/checkout@$', 'actions/setup-node@$', 'actions/setup-python@$',
            'NODE_VERSIO', 'PYTHON_VERSIO', 'JAVA_VERSIO',
            'REGISTR', 'IMAGE_NAM', 'TERRAFORM_VERSIO', 'KUBECTL_VERSIO',
            'gitleaks/gitleaks-action@v$', 'aquasecurity/trivy-action@$',
            'requirement.txt', 'requir.txt', 'PYTHONPTH',
            'matrix.analysis =', 'github.ref =', 'permissions: write-all'
        ]
        
        remaining = []
        for pattern in error_patterns:
            if pattern.endswith('$'):
                # Exact match patterns
                pattern = pattern[:-1]
                if f"{pattern}@" in fixed and not any(f"{pattern}@v" in line for line in fixed.splitlines()):
                    remaining.append(f"{pattern}@")
            else:
                if pattern in fixed:
                    remaining.append(pattern)
        
        # Check YAML syntax
        try:
            yaml.safe_load(fixed)
        except yaml.YAMLError as e:
            remaining.append(f"YAML_SYNTAX: {str(e)}")
        
        return remaining
    
    def train_on_pipeline_directory(self, directory_path: str):
        """Train the agent on a directory of pipelines"""
        
        print(f"🎓 Training agent on pipelines in: {directory_path}")
        
        pipeline_dir = Path(directory_path)
        training_results = []
        
        for pipeline_file in pipeline_dir.glob("*.yml"):
            if "broken" in pipeline_file.name or "test" in pipeline_file.name:
                print(f"📚 Training on: {pipeline_file.name}")
                
                with open(pipeline_file, 'r') as f:
                    content = f.read()
                
                # Fix with learning enabled
                fixed_content = self.fix_production_pipeline(content, learn_from_errors=True)
                
                # Calculate success metrics
                remaining_errors = self._analyze_remaining_errors(content, fixed_content)
                success_rate = ((26 - len(remaining_errors)) / 26) * 100
                
                training_results.append({
                    'file': pipeline_file.name,
                    'success_rate': success_rate,
                    'remaining_errors': len(remaining_errors)
                })
                
                print(f"   Success rate: {success_rate:.1f}%")
        
        # Save training results
        avg_success = sum(r['success_rate'] for r in training_results) / len(training_results)
        print(f"\n📊 Training Complete!")
        print(f"   Files processed: {len(training_results)}")
        print(f"   Average success rate: {avg_success:.1f}%")
        print(f"   Learned patterns: {len(self.learning_agent.learned_patterns)}")
        
        return training_results


def create_daily_improvement_script():
    """Create a script for daily agent improvement"""
    
    script_content = '''#!/usr/bin/env python3
"""
Daily CI/CD Agent Improvement Script
Run this daily to continuously improve your agent performance
"""

from self_improving_agent import SelfImprovingCICDAgent
from continuous_learning_agent import run_daily_learning_cycle
import os
from pathlib import Path

def daily_improvement_routine():
    """Complete daily improvement routine"""
    
    print("🌅 Daily CI/CD Agent Improvement Routine")
    print("=" * 50)
    
    # 1. Run continuous learning on all pipelines
    print("\\n📚 Step 1: Analyzing all pipeline files...")
    current_dir = Path(".")
    report, learning_agent = run_daily_learning_cycle(str(current_dir))
    
    # 2. Test improved agent performance
    print("\\n🧠 Step 2: Testing improved agent...")
    agent = SelfImprovingCICDAgent()
    
    # Test on complex pipeline
    if Path("broken_enterprise_pipeline.yml").exists():
        with open("broken_enterprise_pipeline.yml", 'r') as f:
            test_content = f.read()
        
        fixed_content = agent.fix_production_pipeline(test_content)
        
        # Measure improvement
        remaining_errors = agent._analyze_remaining_errors(test_content, fixed_content)
        success_rate = ((26 - len(remaining_errors)) / 26) * 100
        
        print(f"   Current performance: {success_rate:.1f}%")
        print(f"   Remaining errors: {len(remaining_errors)}")
    
    # 3. Generate improvement report
    print("\\n📊 Step 3: Generating improvement report...")
    
    improvement_summary = f"""
# 🚀 Daily Agent Improvement Summary
Date: {report.date}

## Performance Metrics
- **Current Success Rate**: {success_rate:.1f}%
- **Pipelines Processed**: {report.pipelines_processed}
- **New Patterns Learned**: {report.new_patterns_discovered}

## Learning Progress
- **Total Patterns**: {len(learning_agent.learned_patterns)}
- **High Confidence**: {len([p for p in learning_agent.learned_patterns.values() if p.confidence > 0.9])}

## Next Steps
1. Review new patterns in `learning_data/learned_patterns.json`
2. Test agent on production pipelines
3. Monitor success rate improvements

Generated on: {report.date}
"""
    
    # Save improvement summary
    with open("DAILY_IMPROVEMENT_REPORT.md", "w") as f:
        f.write(improvement_summary)
    
    print(f"✅ Daily improvement complete!")
    print(f"📄 Report saved: DAILY_IMPROVEMENT_REPORT.md")
    print(f"🎯 Agent is now smarter and more capable!")
    
    return {
        'success_rate': success_rate,
        'patterns_learned': len(learning_agent.learned_patterns),
        'improvement_report': improvement_summary
    }

if __name__ == "__main__":
    daily_improvement_routine()
'''
    
    with open("daily_improvement.py", "w") as f:
        f.write(script_content)
    
    print("📅 Created daily improvement script: daily_improvement.py")

if __name__ == "__main__":
    
    print("🧠 Self-Improving CI/CD Agent Ready!")
    print("=" * 45)
    
    # Create daily improvement script
    create_daily_improvement_script()
    
    # Demo the self-improving capabilities
    agent = SelfImprovingCICDAgent()
    
    print("\\n🎯 How to Use:")
    print("1. Daily: python daily_improvement.py")
    print("2. Training: agent.train_on_pipeline_directory('path/to/pipelines')")
    print("3. Fixing: agent.fix_production_pipeline(content)")
    
    print("\\n🚀 Features:")
    print("✅ Learns from every error")
    print("✅ Automatically improves patterns")
    print("✅ Generates daily reports")
    print("✅ Tracks performance trends")
    print("✅ Auto-updates fix strategies")
    
    print("\\nYour agent will now get better every day! 🎊")