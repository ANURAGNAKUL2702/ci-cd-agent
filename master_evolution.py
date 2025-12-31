#!/usr/bin/env python3
"""
Master Control Script - Complete CI/CD Agent Evolution System
Orchestrates daily learning, monitoring, and improvement
"""

import sys
import time
import datetime
import json
from pathlib import Path
from typing import Dict, List

# Import all our components
from continuous_learning_agent import ContinuousLearningAgent, run_daily_learning_cycle
from performance_monitor import PerformanceMonitor
from agent_auto_updater import AgentAutoUpdater
from self_improving_agent import SelfImprovingCICDAgent

class MasterEvolutionSystem:
    """Master system that orchestrates complete agent evolution"""
    
    def __init__(self):
        self.learning_agent = ContinuousLearningAgent()
        self.performance_monitor = PerformanceMonitor()
        self.auto_updater = AgentAutoUpdater()
        self.ci_agent = SelfImprovingCICDAgent()
        
        self.reports_dir = Path("evolution_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_complete_evolution_cycle(self, pipeline_directory: str = ".") -> Dict:
        """Run complete daily evolution cycle"""
        
        print("🧬 CI/CD Agent Evolution System - Daily Cycle")
        print("=" * 55)
        
        start_time = time.time()
        evolution_report = {
            'date': datetime.date.today().isoformat(),
            'start_time': datetime.datetime.now().isoformat(),
            'phases': {}
        }
        
        # Phase 1: Learning from daily pipelines
        print("\\n🧠 Phase 1: Continuous Learning Analysis")
        print("-" * 40)
        
        learning_start = time.time()
        learning_report = self.learning_agent.process_daily_pipelines(pipeline_directory)
        learning_time = time.time() - learning_start
        
        evolution_report['phases']['learning'] = {
            'duration_seconds': learning_time,
            'pipelines_processed': learning_report.pipelines_processed,
            'new_patterns': learning_report.new_patterns_discovered,
            'success_rate_improvement': learning_report.success_rate_improvement
        }
        
        print(f"✅ Learning Phase Complete ({learning_time:.2f}s)")
        print(f"   📁 Processed: {learning_report.pipelines_processed} pipelines")
        print(f"   🔍 Discovered: {learning_report.new_patterns_discovered} new patterns")
        print(f"   📈 Improvement: {learning_report.success_rate_improvement:+.1f}%")
        
        # Phase 2: Performance monitoring and analysis
        print("\\n📊 Phase 2: Performance Monitoring")
        print("-" * 35)
        
        monitor_start = time.time()
        performance_report = self._run_performance_analysis()
        monitor_time = time.time() - monitor_start
        
        evolution_report['phases']['monitoring'] = {
            'duration_seconds': monitor_time,
            'current_success_rate': performance_report['summary']['average_success_rate'],
            'total_errors_fixed': performance_report['summary']['total_errors_fixed'],
            'recommendations_count': len(performance_report['recommendations'])
        }
        
        print(f"✅ Monitoring Phase Complete ({monitor_time:.2f}s)")
        print(f"   📈 Success Rate: {performance_report['summary']['average_success_rate']:.1f}%")
        print(f"   🔧 Total Fixes: {performance_report['summary']['total_errors_fixed']}")
        
        # Phase 3: Auto-update if patterns are ready
        print("\\n🚀 Phase 3: Automatic Agent Updates")
        print("-" * 35)
        
        update_start = time.time()
        update_status = self.auto_updater.check_for_updates()
        update_applied = False
        
        if update_status['needs_update']:
            print(f"🔄 Applying updates: {update_status['reason']}")
            update_applied = self.auto_updater.update_agent_patterns()
        else:
            print(f"ℹ️  No updates needed: {update_status['reason']}")
        
        update_time = time.time() - update_start
        
        evolution_report['phases']['updates'] = {
            'duration_seconds': update_time,
            'update_needed': update_status['needs_update'],
            'update_applied': update_applied,
            'reason': update_status['reason']
        }
        
        print(f"✅ Update Phase Complete ({update_time:.2f}s)")
        print(f"   🤖 Update Applied: {'✅' if update_applied else '❌'}")
        
        # Phase 4: Validation and testing
        print("\\n🧪 Phase 4: Validation & Testing")
        print("-" * 30)
        
        validation_start = time.time()
        validation_results = self._run_validation_tests()
        validation_time = time.time() - validation_start
        
        evolution_report['phases']['validation'] = {
            'duration_seconds': validation_time,
            'tests_passed': validation_results['passed'],
            'tests_total': validation_results['total'],
            'post_update_performance': validation_results['performance']
        }
        
        print(f"✅ Validation Phase Complete ({validation_time:.2f}s)")
        print(f"   🧪 Tests Passed: {validation_results['passed']}/{validation_results['total']}")
        print(f"   🎯 Performance: {validation_results['performance']:.1f}%")
        
        # Generate comprehensive report
        total_time = time.time() - start_time
        evolution_report['total_duration_seconds'] = total_time
        evolution_report['end_time'] = datetime.datetime.now().isoformat()
        
        # Save evolution report
        report_path = self._save_evolution_report(evolution_report)
        
        print(f"\\n🎊 Evolution Cycle Complete!")
        print(f"   ⏱️  Total Time: {total_time:.2f}s")
        print(f"   📄 Report: {report_path}")
        
        return evolution_report
    
    def _run_performance_analysis(self) -> Dict:
        """Run comprehensive performance analysis"""
        
        # Test current agent on various pipeline types
        test_pipelines = {
            "enterprise": "broken_enterprise_pipeline.yml",
            "basic": "broken_workflow.yml",
            "complex": "test_complex_pipeline.yml"
        }
        
        for pipeline_type, filename in test_pipelines.items():
            if Path(filename).exists():
                with open(filename, 'r') as f:
                    content = f.read()
                
                # Measure performance
                start_time = time.time()
                fixed_content = self.ci_agent.fix_production_pipeline(content, learn_from_errors=False)
                processing_time = time.time() - start_time
                
                # Analyze results
                remaining_errors = self.ci_agent._analyze_remaining_errors(content, fixed_content)
                
                # Record performance
                self.performance_monitor.record_performance(
                    content, fixed_content, remaining_errors, 
                    processing_time, pipeline_type
                )
        
        # Generate comprehensive report
        return self.performance_monitor.generate_performance_report()
    
    def _run_validation_tests(self) -> Dict:
        """Run validation tests to ensure agent quality"""
        
        tests = []
        passed = 0
        
        # Test 1: Basic functionality
        test_content = "name: Test\\non: push\\njobs:\\n  test:\\n    runs-on: ubuntu-lat"
        fixed_content = self.ci_agent.fix_production_pipeline(test_content, learn_from_errors=False)
        
        test_1_passed = "ubuntu-latest" in fixed_content
        tests.append(("Basic fix functionality", test_1_passed))
        if test_1_passed:
            passed += 1
        
        # Test 2: YAML validation
        try:
            import yaml
            yaml.safe_load(fixed_content)
            test_2_passed = True
        except:
            test_2_passed = False
        
        tests.append(("YAML syntax validation", test_2_passed))
        if test_2_passed:
            passed += 1
        
        # Test 3: Performance benchmark
        if Path("broken_enterprise_pipeline.yml").exists():
            with open("broken_enterprise_pipeline.yml", 'r') as f:
                enterprise_content = f.read()
            
            start_time = time.time()
            enterprise_fixed = self.ci_agent.fix_production_pipeline(enterprise_content, learn_from_errors=False)
            processing_time = time.time() - start_time
            
            remaining_errors = self.ci_agent._analyze_remaining_errors(enterprise_content, enterprise_fixed)
            success_rate = ((26 - len(remaining_errors)) / 26) * 100
            
            test_3_passed = success_rate >= 70  # Minimum acceptable performance
            tests.append(("Enterprise pipeline performance", test_3_passed))
            if test_3_passed:
                passed += 1
        else:
            success_rate = 0
        
        # Test 4: Learning system integration
        try:
            learned_patterns_file = Path("learning_data/learned_patterns.json")
            test_4_passed = learned_patterns_file.exists()
            tests.append(("Learning system integration", test_4_passed))
            if test_4_passed:
                passed += 1
        except:
            tests.append(("Learning system integration", False))
        
        return {
            'passed': passed,
            'total': len(tests),
            'tests': tests,
            'performance': success_rate if 'success_rate' in locals() else 0
        }
    
    def _save_evolution_report(self, report: Dict) -> Path:
        """Save comprehensive evolution report"""
        
        # Generate detailed markdown report
        report_content = f"""# 🧬 CI/CD Agent Evolution Report
**Date:** {report['date']}  
**Duration:** {report['total_duration_seconds']:.2f} seconds

## 📊 Executive Summary

| Phase | Status | Duration | Key Metrics |
|-------|--------|----------|-------------|
| 🧠 Learning | ✅ Complete | {report['phases']['learning']['duration_seconds']:.1f}s | {report['phases']['learning']['new_patterns']} new patterns |
| 📊 Monitoring | ✅ Complete | {report['phases']['monitoring']['duration_seconds']:.1f}s | {report['phases']['monitoring']['current_success_rate']:.1f}% success rate |
| 🚀 Updates | {'✅ Applied' if report['phases']['updates']['update_applied'] else 'ℹ️ Skipped'} | {report['phases']['updates']['duration_seconds']:.1f}s | {report['phases']['updates']['reason']} |
| 🧪 Validation | ✅ Complete | {report['phases']['validation']['duration_seconds']:.1f}s | {report['phases']['validation']['tests_passed']}/{report['phases']['validation']['tests_total']} tests passed |

## 🎯 Performance Metrics

- **Current Success Rate:** {report['phases']['monitoring']['current_success_rate']:.1f}%
- **Performance Improvement:** {report['phases']['learning']['success_rate_improvement']:+.1f}%
- **Total Errors Fixed:** {report['phases']['monitoring']['total_errors_fixed']}
- **Post-Validation Performance:** {report['phases']['validation']['post_update_performance']:.1f}%

## 🧠 Learning Progress

- **Pipelines Processed:** {report['phases']['learning']['pipelines_processed']}
- **New Patterns Discovered:** {report['phases']['learning']['new_patterns']}
- **Update Applied:** {'Yes' if report['phases']['updates']['update_applied'] else 'No'}

## 🔍 Next Steps

Based on today's evolution cycle:

"""
        
        # Add recommendations based on results
        if report['phases']['monitoring']['current_success_rate'] < 80:
            report_content += "1. **🔴 Priority:** Focus on improving core success rate (currently below 80%)\n"
        
        if report['phases']['learning']['new_patterns'] > 5:
            report_content += "2. **🧠 Learning:** High pattern discovery rate - consider increasing update frequency\n"
        
        if not report['phases']['updates']['update_applied'] and report['phases']['updates']['update_needed']:
            report_content += "3. **🚀 Updates:** Manual review needed for pending updates\n"
        
        if report['phases']['validation']['tests_passed'] < report['phases']['validation']['tests_total']:
            report_content += "4. **🧪 Quality:** Some validation tests failed - investigate issues\n"
        
        report_content += f"""

## 📈 Historical Context

This evolution cycle represents continuous improvement in action. The agent is:
- **Learning** from daily pipeline errors
- **Adapting** its fix patterns automatically  
- **Monitoring** its own performance
- **Updating** itself when ready
- **Validating** all changes for quality

---
*Generated by CI/CD Agent Evolution System v2.0*  
*Next evolution cycle: {datetime.date.today() + datetime.timedelta(days=1)}*
"""
        
        # Save report
        report_file = self.reports_dir / f"evolution_report_{report['date']}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Also save raw JSON data
        json_file = self.reports_dir / f"evolution_data_{report['date']}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def get_evolution_history(self, days: int = 7) -> List[Dict]:
        """Get evolution history for the last N days"""
        
        history = []
        
        for i in range(days):
            date = datetime.date.today() - datetime.timedelta(days=i)
            json_file = self.reports_dir / f"evolution_data_{date.isoformat()}.json"
            
            if json_file.exists():
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    history.append(data)
        
        return history
    
    def generate_weekly_summary(self) -> str:
        """Generate weekly evolution summary"""
        
        history = self.get_evolution_history(7)
        
        if not history:
            return "No evolution data available for weekly summary"
        
        # Calculate weekly metrics
        total_patterns = sum(h['phases']['learning']['new_patterns'] for h in history)
        avg_success_rate = sum(h['phases']['monitoring']['current_success_rate'] for h in history) / len(history)
        total_updates = sum(1 for h in history if h['phases']['updates']['update_applied'])
        
        summary = f"""# 📅 Weekly Evolution Summary
**Period:** {(datetime.date.today() - datetime.timedelta(days=6)).isoformat()} to {datetime.date.today().isoformat()}

## 🎯 Weekly Achievements
- **📊 Average Success Rate:** {avg_success_rate:.1f}%
- **🧠 Total New Patterns:** {total_patterns}
- **🚀 Agent Updates Applied:** {total_updates}
- **📁 Evolution Cycles:** {len(history)}

## 📈 Progress Trend
"""
        
        for day_data in reversed(history):
            date = day_data['date']
            success_rate = day_data['phases']['monitoring']['current_success_rate']
            new_patterns = day_data['phases']['learning']['new_patterns']
            summary += f"- **{date}**: {success_rate:.1f}% success, {new_patterns} new patterns\n"
        
        summary += f"""

## 🚀 Looking Ahead
Your CI/CD agent is continuously evolving and improving. Keep running daily evolution cycles to maintain peak performance!

*Generated on {datetime.date.today().isoformat()}*
"""
        
        # Save weekly summary
        summary_file = self.reports_dir / f"weekly_summary_{datetime.date.today().isoformat()}.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return summary


def main():
    """Main entry point for the evolution system"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        system = MasterEvolutionSystem()
        
        if command == "evolve":
            # Run complete evolution cycle
            pipeline_dir = sys.argv[2] if len(sys.argv) > 2 else "."
            report = system.run_complete_evolution_cycle(pipeline_dir)
            
        elif command == "weekly":
            # Generate weekly summary
            summary = system.generate_weekly_summary()
            print(summary)
            
        elif command == "history":
            # Show evolution history
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            history = system.get_evolution_history(days)
            
            print(f"📈 Evolution History ({days} days):")
            for day_data in history:
                print(f"  {day_data['date']}: {day_data['phases']['monitoring']['current_success_rate']:.1f}% success")
                
        else:
            print("Unknown command. Usage: python master_evolution.py [evolve|weekly|history]")
    else:
        # Interactive mode
        print("🧬 CI/CD Agent Evolution System")
        print("=" * 40)
        print("Commands:")
        print("  evolve    - Run complete evolution cycle")
        print("  weekly    - Generate weekly summary")
        print("  history   - Show evolution history")


if __name__ == "__main__":
    main()