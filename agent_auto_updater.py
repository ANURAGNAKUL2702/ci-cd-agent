#!/usr/bin/env python3
"""
Auto-Update System for CI/CD Agent
Automatically updates agent patterns and capabilities based on learning
"""

import os
import json
import datetime
import shutil
from pathlib import Path
from typing import Dict, List
import importlib.util

class AgentAutoUpdater:
    """Automatically updates agent code with learned patterns"""
    
    def __init__(self, agent_modules_dir: str = "modules"):
        self.modules_dir = Path(agent_modules_dir)
        self.learning_dir = Path("learning_data")
        self.backup_dir = Path("agent_backups")
        
        # Create directories if they don't exist
        self.backup_dir.mkdir(exist_ok=True)
        
    def update_agent_patterns(self) -> bool:
        """Update agent with new learned patterns"""
        
        print("🔄 Auto-Updating CI/CD Agent Patterns...")
        
        # Load learned patterns
        patterns_file = self.learning_dir / "learned_patterns.json"
        if not patterns_file.exists():
            print("❌ No learned patterns found")
            return False
        
        with open(patterns_file, 'r') as f:
            learned_patterns = json.load(f)
        
        if not learned_patterns:
            print("ℹ️  No patterns to update")
            return False
        
        # Create backup of current agent
        self._backup_current_agent()
        
        # Generate new pattern code
        new_fixes = self._generate_pattern_fixes(learned_patterns)
        
        # Update agent modules
        success = self._update_agent_modules(new_fixes)
        
        if success:
            print(f"✅ Agent updated with {len(learned_patterns)} new patterns")
            self._log_update(learned_patterns)
        else:
            print("❌ Failed to update agent")
            self._restore_from_backup()
        
        return success
    
    def _backup_current_agent(self):
        """Create backup of current agent code"""
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"agent_backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Backup key files
        files_to_backup = [
            "enterprise_cicd_agent.py",
            "self_improving_agent.py",
            "modules/production_error_detector.py"
        ]
        
        for file_path in files_to_backup:
            if Path(file_path).exists():
                shutil.copy2(file_path, backup_path / Path(file_path).name)
        
        print(f"💾 Backup created: {backup_path}")
    
    def _generate_pattern_fixes(self, patterns: Dict) -> List[str]:
        """Generate Python code for new pattern fixes"""
        
        fix_methods = []
        
        for pattern_key, pattern_data in patterns.items():
            if pattern_data['confidence'] < 0.7:
                continue  # Skip low-confidence patterns
            
            method_name = self._generate_method_name(pattern_data)
            fix_code = self._generate_fix_method(pattern_data, method_name)
            
            fix_methods.append(fix_code)
        
        return fix_methods
    
    def _generate_method_name(self, pattern_data: Dict) -> str:
        """Generate a valid Python method name from pattern"""
        
        error_text = pattern_data['error_text']
        category = pattern_data['category']
        
        # Clean up for method name
        clean_name = error_text.replace('-', '_').replace('/', '_').replace('@', '_').replace('.', '_')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        
        return f"_fix_{category}_{clean_name}"[:50]  # Limit length
    
    def _generate_fix_method(self, pattern_data: Dict, method_name: str) -> str:
        """Generate complete fix method code"""
        
        error_text = pattern_data['error_text']
        fix_suggestion = pattern_data['fix_suggestion']
        
        # Extract replacement from fix suggestion
        if "Replace '" in fix_suggestion and "' with '" in fix_suggestion:
            parts = fix_suggestion.split("' with '")
            old_text = parts[0].split("Replace '")[1]
            new_text = parts[1].rstrip("'")
        else:
            old_text = error_text
            new_text = f"FIXED_{error_text}"
        
        return f'''
    def {method_name}(self, content: str) -> str:
        """Auto-generated fix for {error_text} (confidence: {pattern_data['confidence']:.1f})"""
        if '{old_text}' in content:
            content = content.replace('{old_text}', '{new_text}')
            self.fixes_applied.append("Auto-learned: {old_text} → {new_text}")
        return content'''
    
    def _update_agent_modules(self, new_fixes: List[str]) -> bool:
        """Update agent modules with new fix methods"""
        
        try:
            # Create enhanced error detector module
            enhanced_module_path = self.modules_dir / "auto_learned_fixes.py"
            
            module_content = f'''"""
Auto-generated fixes based on continuous learning
Generated: {datetime.datetime.now().isoformat()}
Total patterns: {len(new_fixes)}
"""

class AutoLearnedFixes:
    """Auto-generated fix methods from continuous learning"""
    
    def __init__(self):
        self.fixes_applied = []
    
    def apply_all_learned_fixes(self, content: str) -> str:
        """Apply all auto-learned fixes"""
        for method_name in dir(self):
            if method_name.startswith('_fix_'):
                method = getattr(self, method_name)
                content = method(content)
        return content
{''.join(new_fixes)}
'''
            
            with open(enhanced_module_path, 'w', encoding='utf-8') as f:
                f.write(module_content)
            
            # Update main enterprise agent to include auto-learned fixes
            self._integrate_learned_fixes()
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating modules: {e}")
            return False
    
    def _integrate_learned_fixes(self):
        """Integrate learned fixes into main agent"""
        
        agent_file = Path("enterprise_cicd_agent.py")
        if not agent_file.exists():
            return
        
        # Read current agent code
        with open(agent_file, 'r') as f:
            agent_code = f.read()
        
        # Check if auto-learned fixes are already integrated
        if "auto_learned_fixes" in agent_code.lower():
            return
        
        # Find the class definition and add import
        import_line = "from modules.auto_learned_fixes import AutoLearnedFixes"
        if import_line not in agent_code:
            # Add import after existing imports
            lines = agent_code.splitlines()
            import_inserted = False
            
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    continue
                else:
                    lines.insert(i, import_line)
                    import_inserted = True
                    break
            
            if import_inserted:
                agent_code = '\n'.join(lines)
        
        # Add initialization in __init__ method
        init_line = "        self.auto_fixes = AutoLearnedFixes()"
        if init_line not in agent_code:
            agent_code = agent_code.replace(
                "self.fixes_applied = []",
                "self.fixes_applied = []\n" + init_line
            )
        
        # Add auto-learned fixes to fix_production_pipeline method
        auto_fix_call = "            current_content = self._apply_auto_learned_fixes,"
        if auto_fix_call not in agent_code:
            # Find the fixes list and add our method
            agent_code = agent_code.replace(
                "fixes = [",
                "fixes = [\n                self._apply_auto_learned_fixes,"
            )
        
        # Add the method if it doesn't exist
        auto_fix_method = '''
    def _apply_auto_learned_fixes(self, content: str) -> str:
        """Apply automatically learned fixes"""
        try:
            before_content = content
            content = self.auto_fixes.apply_all_learned_fixes(content)
            
            # Merge fix logs
            if hasattr(self.auto_fixes, 'fixes_applied'):
                self.fixes_applied.extend(self.auto_fixes.fixes_applied)
                self.auto_fixes.fixes_applied = []
            
            return content
        except Exception as e:
            print(f"⚠️  Auto-learned fixes failed: {e}")
            return content
'''
        
        if "_apply_auto_learned_fixes" not in agent_code:
            # Add method before the last method or end of class
            agent_code = agent_code.replace(
                "    def _enterprise_cleanup",
                auto_fix_method + "\n    def _enterprise_cleanup"
            )
        
        # Write updated agent code
        with open(agent_file, 'w') as f:
            f.write(agent_code)
    
    def _restore_from_backup(self):
        """Restore agent from backup in case of failure"""
        
        # Find latest backup
        backups = sorted(self.backup_dir.glob("agent_backup_*"))
        if not backups:
            print("❌ No backups found for restoration")
            return
        
        latest_backup = backups[-1]
        
        # Restore files
        for backup_file in latest_backup.glob("*.py"):
            original_path = Path(backup_file.name)
            if original_path.exists():
                shutil.copy2(backup_file, original_path)
        
        print(f"🔄 Restored from backup: {latest_backup}")
    
    def _log_update(self, patterns: Dict):
        """Log the update for tracking"""
        
        update_log = {
            'timestamp': datetime.datetime.now().isoformat(),
            'patterns_count': len(patterns),
            'patterns': list(patterns.keys()),
            'version': self._get_next_version()
        }
        
        log_file = self.learning_dir / "update_history.json"
        
        # Load existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(update_log)
        
        # Save updated log
        with open(log_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"📝 Update logged: Version {update_log['version']}")
    
    def _get_next_version(self) -> str:
        """Get next version number for the agent"""
        
        log_file = self.learning_dir / "update_history.json"
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                history = json.load(f)
            
            if history:
                last_version = history[-1]['version']
                # Simple version increment
                version_parts = last_version.split('.')
                version_parts[-1] = str(int(version_parts[-1]) + 1)
                return '.'.join(version_parts)
        
        return "1.0.0"  # Initial version
    
    def schedule_auto_updates(self, enabled: bool = True) -> bool:
        """Enable/disable scheduled auto-updates"""
        
        config = {
            'auto_updates_enabled': enabled,
            'last_update_check': datetime.datetime.now().isoformat(),
            'update_frequency_hours': 24  # Check daily
        }
        
        config_file = self.learning_dir / "auto_update_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        status = "enabled" if enabled else "disabled"
        print(f"🔧 Auto-updates {status}")
        
        return True
    
    def check_for_updates(self) -> Dict:
        """Check if agent needs updates based on new patterns"""
        
        patterns_file = self.learning_dir / "learned_patterns.json"
        update_log_file = self.learning_dir / "update_history.json"
        
        if not patterns_file.exists():
            return {'needs_update': False, 'reason': 'No patterns found'}
        
        # Load patterns
        with open(patterns_file, 'r') as f:
            patterns = json.load(f)
        
        # Load update history
        if update_log_file.exists():
            with open(update_log_file, 'r') as f:
                history = json.load(f)
            last_update = history[-1]['timestamp'] if history else None
        else:
            last_update = None
        
        # Check if there are new high-confidence patterns
        high_confidence_patterns = [
            p for p in patterns.values() 
            if p['confidence'] >= 0.7 and p['frequency'] >= 3
        ]
        
        if len(high_confidence_patterns) >= 5:  # Threshold for update
            return {
                'needs_update': True,
                'reason': f'{len(high_confidence_patterns)} high-confidence patterns ready',
                'patterns_ready': len(high_confidence_patterns),
                'last_update': last_update
            }
        
        return {'needs_update': False, 'reason': 'Insufficient patterns for update'}


def create_auto_update_script():
    """Create script for automated agent updates"""
    
    script_content = '''#!/usr/bin/env python3
"""
Automated Agent Update Script
Runs automatic updates based on learned patterns
"""

import time
import schedule
from agent_auto_updater import AgentAutoUpdater

def run_auto_update_check():
    """Run automatic update check and update if needed"""
    
    print("🔍 Checking for agent updates...")
    
    updater = AgentAutoUpdater()
    
    # Check if updates are needed
    update_status = updater.check_for_updates()
    
    if update_status['needs_update']:
        print(f"🚀 Update needed: {update_status['reason']}")
        
        # Perform update
        success = updater.update_agent_patterns()
        
        if success:
            print("✅ Agent successfully updated!")
            
            # Test updated agent
            print("🧪 Testing updated agent...")
            test_updated_agent()
        else:
            print("❌ Update failed - agent restored from backup")
    else:
        print(f"ℹ️  No update needed: {update_status['reason']}")

def test_updated_agent():
    """Test the updated agent to ensure it works"""
    
    try:
        from self_improving_agent import SelfImprovingCICDAgent
        from pathlib import Path
        
        agent = SelfImprovingCICDAgent()
        
        # Test with a simple pipeline
        test_content = """
name: Test Pipeline
on: push
jobs:
  test:
    runs-on: ubuntu-lat
    steps:
      - uses: actions/checkout@
"""
        
        fixed_content = agent.fix_production_pipeline(test_content, learn_from_errors=False)
        
        if 'ubuntu-latest' in fixed_content and 'actions/checkout@v4' in fixed_content:
            print("✅ Updated agent working correctly")
        else:
            print("⚠️  Updated agent may have issues")
            
    except Exception as e:
        print(f"❌ Error testing updated agent: {e}")

def schedule_auto_updates():
    """Schedule automatic updates"""
    
    # Schedule daily updates at 2 AM
    schedule.every().day.at("02:00").do(run_auto_update_check)
    
    # Schedule weekly comprehensive updates
    schedule.every().sunday.at("03:00").do(run_comprehensive_update)
    
    print("📅 Auto-updates scheduled:")
    print("   Daily check: 2:00 AM")
    print("   Weekly comprehensive: Sunday 3:00 AM")
    
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

def run_comprehensive_update():
    """Run comprehensive weekly update"""
    
    print("🔄 Running comprehensive weekly update...")
    
    # Run learning cycle
    from continuous_learning_agent import run_daily_learning_cycle
    run_daily_learning_cycle()
    
    # Run performance monitoring
    from performance_monitoring import run_performance_monitoring
    run_performance_monitoring()
    
    # Run auto update
    run_auto_update_check()
    
    print("✅ Comprehensive update complete!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "schedule":
            schedule_auto_updates()
        elif sys.argv[1] == "check":
            run_auto_update_check()
        elif sys.argv[1] == "comprehensive":
            run_comprehensive_update()
    else:
        print("Usage: python auto_update_script.py [schedule|check|comprehensive]")
'''
    
    with open("auto_update_script.py", "w") as f:
        f.write(script_content)
    
    print("🤖 Created auto-update script: auto_update_script.py")

if __name__ == "__main__":
    
    print("🤖 Agent Auto-Updater Ready!")
    print("=" * 35)
    
    # Create auto-update script
    create_auto_update_script()
    
    # Demo the auto-updater
    updater = AgentAutoUpdater()
    
    print("\\n🎯 How to Use:")
    print("1. Check: python auto_update_script.py check")
    print("2. Schedule: python auto_update_script.py schedule")
    print("3. Manual: updater.update_agent_patterns()")
    
    print("\\n🚀 Features:")
    print("✅ Automatic pattern integration")
    print("✅ Backup and restore")
    print("✅ Version tracking")
    print("✅ Scheduled updates")
    print("✅ Safety checks and testing")
    
    print("\\nYour agent will automatically improve itself! 🎊")