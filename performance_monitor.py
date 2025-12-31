#!/usr/bin/env python3
"""
Real-time Performance Monitor for CI/CD Agent
Tracks success rates, identifies patterns, and provides insights
"""

import json
import time
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetric:
    timestamp: str
    pipeline_type: str
    success_rate: float
    errors_fixed: int
    errors_remaining: int
    processing_time: float
    file_size: int
    complexity_score: int

class PerformanceMonitor:
    """Real-time performance monitoring and analytics"""
    
    def __init__(self, data_dir: str = "performance_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.metrics_file = self.data_dir / "performance_metrics.json"
        self.trends_file = self.data_dir / "performance_trends.json"
        
        self.metrics = self._load_metrics()
        
    def _load_metrics(self) -> List[PerformanceMetric]:
        """Load existing performance metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                return [PerformanceMetric(**item) for item in data]
        return []
    
    def _save_metrics(self):
        """Save performance metrics"""
        data = [asdict(metric) for metric in self.metrics]
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_performance(self, pipeline_content: str, fixed_content: str, 
                          remaining_errors: List[str], processing_time: float,
                          pipeline_type: str = "unknown"):
        """Record performance metrics for a pipeline fix"""
        
        # Calculate metrics
        total_errors = 26  # Known error patterns in test pipeline
        errors_fixed = total_errors - len(remaining_errors)
        success_rate = (errors_fixed / total_errors) * 100
        complexity_score = self._calculate_complexity_score(pipeline_content)
        
        metric = PerformanceMetric(
            timestamp=datetime.datetime.now().isoformat(),
            pipeline_type=pipeline_type,
            success_rate=success_rate,
            errors_fixed=errors_fixed,
            errors_remaining=len(remaining_errors),
            processing_time=processing_time,
            file_size=len(pipeline_content),
            complexity_score=complexity_score
        )
        
        self.metrics.append(metric)
        self._save_metrics()
        
        return metric
    
    def _calculate_complexity_score(self, content: str) -> int:
        """Calculate pipeline complexity score"""
        score = 0
        
        # Count different types of complexity indicators
        complexity_indicators = {
            'matrix:': 10,          # Matrix builds
            'strategy:': 8,         # Build strategies  
            'environment:': 5,      # Environment deployments
            'services:': 7,         # Service containers
            'if:': 3,              # Conditional logic
            'needs:': 4,           # Job dependencies
            'uses: docker://': 6,   # Docker actions
            'kubectl': 8,          # Kubernetes
            'terraform': 7,        # Infrastructure as Code
            'security': 5,         # Security scanning
        }
        
        for indicator, weight in complexity_indicators.items():
            count = content.lower().count(indicator.lower())
            score += count * weight
        
        # Add base score for number of jobs
        jobs_count = content.count('jobs:') + content.count('  ') // 4  # Rough job estimation
        score += jobs_count * 2
        
        return min(score, 100)  # Cap at 100
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        
        if not self.metrics:
            return {"error": "No performance data available"}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([asdict(m) for m in self.metrics])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate key statistics
        report = {
            'summary': {
                'total_pipelines_processed': len(self.metrics),
                'average_success_rate': df['success_rate'].mean(),
                'best_success_rate': df['success_rate'].max(),
                'worst_success_rate': df['success_rate'].min(),
                'average_processing_time': df['processing_time'].mean(),
                'total_errors_fixed': df['errors_fixed'].sum()
            },
            'trends': self._analyze_trends(df),
            'pipeline_types': self._analyze_by_type(df),
            'complexity_analysis': self._analyze_complexity(df),
            'recommendations': self._generate_recommendations(df)
        }
        
        return report
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze performance trends over time"""
        
        # Group by date
        df['date'] = df['timestamp'].dt.date
        daily_stats = df.groupby('date').agg({
            'success_rate': 'mean',
            'processing_time': 'mean',
            'errors_fixed': 'sum'
        }).reset_index()
        
        # Calculate trend direction
        if len(daily_stats) >= 2:
            recent_rate = daily_stats['success_rate'].tail(3).mean()
            older_rate = daily_stats['success_rate'].head(3).mean()
            trend_direction = "improving" if recent_rate > older_rate else "declining"
        else:
            trend_direction = "insufficient_data"
        
        return {
            'trend_direction': trend_direction,
            'daily_averages': daily_stats.to_dict('records'),
            'best_day': daily_stats.loc[daily_stats['success_rate'].idxmax()].to_dict(),
            'worst_day': daily_stats.loc[daily_stats['success_rate'].idxmin()].to_dict()
        }
    
    def _analyze_by_type(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by pipeline type"""
        
        type_stats = df.groupby('pipeline_type').agg({
            'success_rate': ['mean', 'count'],
            'processing_time': 'mean',
            'complexity_score': 'mean'
        }).round(2)
        
        return type_stats.to_dict('index')
    
    def _analyze_complexity(self, df: pd.DataFrame) -> Dict:
        """Analyze performance vs complexity"""
        
        # Create complexity bins
        df['complexity_bin'] = pd.cut(df['complexity_score'], 
                                    bins=[0, 20, 40, 60, 80, 100], 
                                    labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
        
        complexity_stats = df.groupby('complexity_bin').agg({
            'success_rate': 'mean',
            'processing_time': 'mean'
        }).round(2)
        
        return {
            'by_complexity': complexity_stats.to_dict('index'),
            'correlation': df['complexity_score'].corr(df['success_rate'])
        }
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate improvement recommendations based on data"""
        
        recommendations = []
        
        # Success rate recommendations
        avg_success = df['success_rate'].mean()
        if avg_success < 70:
            recommendations.append("🔴 Critical: Success rate below 70%. Focus on core pattern improvements.")
        elif avg_success < 85:
            recommendations.append("🟡 Warning: Success rate below 85%. Review frequent error patterns.")
        
        # Processing time recommendations
        avg_time = df['processing_time'].mean()
        if avg_time > 10:
            recommendations.append("⚡ Performance: Average processing time > 10s. Optimize algorithms.")
        
        # Complexity recommendations
        if df['complexity_score'].corr(df['success_rate']) < -0.3:
            recommendations.append("🧩 Complexity: Success rate drops significantly with complex pipelines.")
        
        # Type-specific recommendations
        type_performance = df.groupby('pipeline_type')['success_rate'].mean()
        worst_type = type_performance.idxmin()
        if type_performance[worst_type] < avg_success - 10:
            recommendations.append(f"🎯 Focus: {worst_type} pipelines underperforming by {avg_success - type_performance[worst_type]:.1f}%")
        
        # Trend recommendations
        if len(df) >= 10:
            recent_trend = df.tail(5)['success_rate'].mean() - df.head(5)['success_rate'].mean()
            if recent_trend < -5:
                recommendations.append("📉 Trend: Performance declining. Review recent changes.")
            elif recent_trend > 5:
                recommendations.append("📈 Trend: Performance improving. Continue current approach.")
        
        if not recommendations:
            recommendations.append("✅ Performance: All metrics within acceptable ranges.")
        
        return recommendations
    
    def create_performance_dashboard(self):
        """Create visual performance dashboard"""
        
        if len(self.metrics) < 2:
            print("❌ Insufficient data for dashboard. Need at least 2 data points.")
            return
        
        # Prepare data
        df = pd.DataFrame([asdict(m) for m in self.metrics])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('CI/CD Agent Performance Dashboard', fontsize=16, fontweight='bold')
        
        # Plot 1: Success Rate Over Time
        ax1.plot(df['timestamp'], df['success_rate'], marker='o', linewidth=2, markersize=4)
        ax1.set_title('Success Rate Trend')
        ax1.set_ylabel('Success Rate (%)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Plot 2: Processing Time vs Complexity
        scatter = ax2.scatter(df['complexity_score'], df['processing_time'], 
                            c=df['success_rate'], cmap='RdYlGn', alpha=0.7)
        ax2.set_title('Processing Time vs Complexity')
        ax2.set_xlabel('Complexity Score')
        ax2.set_ylabel('Processing Time (s)')
        plt.colorbar(scatter, ax=ax2, label='Success Rate (%)')
        
        # Plot 3: Success Rate Distribution
        ax3.hist(df['success_rate'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        ax3.axvline(df['success_rate'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["success_rate"].mean():.1f}%')
        ax3.set_title('Success Rate Distribution')
        ax3.set_xlabel('Success Rate (%)')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        
        # Plot 4: Performance by Pipeline Type
        type_stats = df.groupby('pipeline_type')['success_rate'].agg(['mean', 'count'])
        type_stats = type_stats[type_stats['count'] >= 2]  # Only types with 2+ samples
        
        if not type_stats.empty:
            bars = ax4.bar(type_stats.index, type_stats['mean'], alpha=0.7, color='lightgreen')
            ax4.set_title('Performance by Pipeline Type')
            ax4.set_ylabel('Average Success Rate (%)')
            ax4.tick_params(axis='x', rotation=45)
            
            # Add count labels on bars
            for bar, count in zip(bars, type_stats['count']):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'n={count}', ha='center', va='bottom', fontsize=8)
        else:
            ax4.text(0.5, 0.5, 'Insufficient data\nfor type analysis', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Performance by Pipeline Type')
        
        plt.tight_layout()
        
        # Save dashboard
        dashboard_path = self.data_dir / f"performance_dashboard_{datetime.date.today()}.png"
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        
        print(f"📊 Performance dashboard saved: {dashboard_path}")
        
        return dashboard_path
    
    def export_performance_data(self, format: str = 'csv') -> Path:
        """Export performance data in various formats"""
        
        df = pd.DataFrame([asdict(m) for m in self.metrics])
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == 'csv':
            export_path = self.data_dir / f"performance_export_{timestamp}.csv"
            df.to_csv(export_path, index=False)
        elif format.lower() == 'json':
            export_path = self.data_dir / f"performance_export_{timestamp}.json"
            df.to_json(export_path, orient='records', indent=2)
        else:
            raise ValueError("Supported formats: 'csv', 'json'")
        
        return export_path


def create_monitoring_script():
    """Create automated monitoring script"""
    
    script_content = '''#!/usr/bin/env python3
"""
Automated Performance Monitoring for CI/CD Agent
Run this to continuously monitor and improve agent performance
"""

from performance_monitor import PerformanceMonitor
from self_improving_agent import SelfImprovingCICDAgent
import time
import json
from pathlib import Path

def run_performance_monitoring():
    """Run comprehensive performance monitoring"""
    
    print("📊 CI/CD Agent Performance Monitoring")
    print("=" * 45)
    
    monitor = PerformanceMonitor()
    agent = SelfImprovingCICDAgent()
    
    # Test with various pipeline types
    test_pipelines = {
        "enterprise": "broken_enterprise_pipeline.yml",
        "basic": "broken_workflow.yml",
        "complex": "test_complex_pipeline.yml"
    }
    
    for pipeline_type, filename in test_pipelines.items():
        if Path(filename).exists():
            print(f"\\n🧪 Testing {pipeline_type} pipeline: {filename}")
            
            with open(filename, 'r') as f:
                content = f.read()
            
            # Measure processing time
            start_time = time.time()
            fixed_content = agent.fix_production_pipeline(content)
            processing_time = time.time() - start_time
            
            # Analyze remaining errors
            remaining_errors = agent._analyze_remaining_errors(content, fixed_content)
            
            # Record performance
            metric = monitor.record_performance(
                content, fixed_content, remaining_errors, 
                processing_time, pipeline_type
            )
            
            print(f"   ✅ Success rate: {metric.success_rate:.1f}%")
            print(f"   ⚡ Processing time: {processing_time:.2f}s")
            print(f"   🧩 Complexity score: {metric.complexity_score}")
    
    # Generate comprehensive report
    print("\\n📋 Generating performance report...")
    report = monitor.generate_performance_report()
    
    # Create dashboard
    print("\\n📊 Creating performance dashboard...")
    try:
        dashboard_path = monitor.create_performance_dashboard()
    except Exception as e:
        print(f"⚠️  Dashboard creation failed: {e}")
        dashboard_path = None
    
    # Save detailed report
    report_path = Path("performance_data") / f"detailed_report_{time.strftime('%Y%m%d')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print(f"\\n🎯 Performance Summary:")
    print(f"   📈 Average Success Rate: {report['summary']['average_success_rate']:.1f}%")
    print(f"   ⚡ Average Processing Time: {report['summary']['average_processing_time']:.2f}s")
    print(f"   🔧 Total Errors Fixed: {report['summary']['total_errors_fixed']}")
    print(f"   📁 Pipelines Processed: {report['summary']['total_pipelines_processed']}")
    
    print(f"\\n💡 Top Recommendations:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"   {i}. {rec}")
    
    print(f"\\n📄 Reports saved:")
    print(f"   📊 Dashboard: {dashboard_path if dashboard_path else 'N/A'}")
    print(f"   📋 Detailed report: {report_path}")
    
    return report

if __name__ == "__main__":
    run_performance_monitoring()
'''
    
    with open("performance_monitoring.py", "w") as f:
        f.write(script_content)
    
    print("📊 Created performance monitoring script: performance_monitoring.py")

if __name__ == "__main__":
    
    print("📊 Performance Monitor Ready!")
    print("=" * 35)
    
    # Create monitoring script
    create_monitoring_script()
    
    print("\\n🎯 How to Use:")
    print("1. Monitor: python performance_monitoring.py")
    print("2. Dashboard: monitor.create_performance_dashboard()")
    print("3. Export: monitor.export_performance_data('csv')")
    
    print("\\n✨ Features:")
    print("✅ Real-time performance tracking")
    print("✅ Visual dashboards") 
    print("✅ Trend analysis")
    print("✅ Complexity correlation")
    print("✅ Automated recommendations")
    
    print("\\nTrack your agent's performance in real-time! 📈")