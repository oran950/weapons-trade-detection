"""
Report Workflow - Generates analysis reports
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import json

from ..entities.post import RedditPost, TelegramMessage
from ..utils.file_manager import FileManager
from ..config import config


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    report_type: str = "summary"  # 'summary', 'detailed', 'executive'
    include_high_risk_only: bool = False
    include_charts: bool = False
    format: str = "json"  # 'json', 'html', 'markdown'


class ReportWorkflow:
    """
    Generates reports from analysis results
    """
    
    def __init__(self, report_config: Optional[ReportConfig] = None):
        """
        Initialize report workflow
        
        Args:
            report_config: Report configuration
        """
        self.config = report_config or ReportConfig()
        self.file_manager = FileManager(config.DATA_DIR)
    
    def generate_from_file(self, analysis_file: str) -> Dict[str, Any]:
        """
        Generate report from an analysis file
        
        Args:
            analysis_file: Path to analysis JSON file
            
        Returns:
            Report data
        """
        # Load analysis data
        data = self.file_manager.load_json(analysis_file, "analyzed")
        
        if not data:
            raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
        
        return self.generate(data)
    
    def generate(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate report from analysis data
        
        Args:
            analysis_data: Analysis results dictionary
            
        Returns:
            Report data
        """
        if self.config.report_type == "summary":
            return self._generate_summary_report(analysis_data)
        elif self.config.report_type == "detailed":
            return self._generate_detailed_report(analysis_data)
        elif self.config.report_type == "executive":
            return self._generate_executive_report(analysis_data)
        else:
            return self._generate_summary_report(analysis_data)
    
    def _generate_summary_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary report"""
        high_risk = data.get('high_risk_posts', [])
        medium_risk = data.get('medium_risk_posts', [])
        low_risk = data.get('low_risk_posts', [])
        
        total = len(high_risk) + len(medium_risk) + len(low_risk)
        
        # Collect statistics
        platforms = {}
        subreddits = {}
        keywords_freq = {}
        
        all_posts = high_risk + medium_risk + low_risk
        
        for post in all_posts:
            # Platform distribution
            platform = post.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
            
            # Subreddit distribution (for Reddit)
            if 'subreddit' in post:
                sub = post['subreddit']
                subreddits[sub] = subreddits.get(sub, 0) + 1
            
            # Keyword frequency
            if post.get('risk_analysis'):
                for kw in post['risk_analysis'].get('detected_keywords', []):
                    keywords_freq[kw] = keywords_freq.get(kw, 0) + 1
        
        # Sort keywords by frequency
        top_keywords = sorted(
            keywords_freq.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20]
        
        report = {
            "report_type": "summary",
            "generated_at": datetime.now().isoformat(),
            "overview": {
                "total_posts_analyzed": total,
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk),
                "high_risk_percentage": round(len(high_risk) / total * 100, 2) if total > 0 else 0
            },
            "distribution": {
                "by_platform": platforms,
                "by_subreddit": dict(sorted(subreddits.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            "top_keywords": dict(top_keywords),
            "high_risk_samples": [
                {
                    "id": p.get('id'),
                    "platform": p.get('platform'),
                    "subreddit": p.get('subreddit'),
                    "risk_score": p.get('risk_analysis', {}).get('risk_score'),
                    "url": p.get('url')
                }
                for p in high_risk[:10]
            ]
        }
        
        return report
    
    def _generate_detailed_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed report"""
        summary = self._generate_summary_report(data)
        
        high_risk = data.get('high_risk_posts', [])
        
        # Add detailed analysis for each high-risk post
        detailed_findings = []
        
        for post in high_risk:
            analysis = post.get('risk_analysis', {})
            
            finding = {
                "post_id": post.get('id'),
                "platform": post.get('platform'),
                "source": post.get('subreddit') or post.get('chat_title'),
                "url": post.get('url'),
                "collected_at": post.get('collected_at'),
                "risk_score": analysis.get('risk_score'),
                "confidence": analysis.get('confidence'),
                "flags": analysis.get('flags', []),
                "detected_keywords": analysis.get('detected_keywords', []),
                "detected_patterns": analysis.get('detected_patterns', []),
                "content_preview": (post.get('title', '') + ' ' + post.get('content', ''))[:200] + '...'
            }
            
            # Add LLM analysis if available
            if analysis.get('llm_reasons'):
                finding['llm_analysis'] = {
                    "reasons": analysis.get('llm_reasons'),
                    "evidence": analysis.get('llm_evidence_spans'),
                    "misclassification_risk": analysis.get('llm_misclassification_risk')
                }
            
            detailed_findings.append(finding)
        
        summary["report_type"] = "detailed"
        summary["detailed_findings"] = detailed_findings
        
        return summary
    
    def _generate_executive_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary report"""
        summary = self._generate_summary_report(data)
        
        high_risk = data.get('high_risk_posts', [])
        total = summary['overview']['total_posts_analyzed']
        
        # Generate key insights
        insights = []
        
        high_pct = summary['overview']['high_risk_percentage']
        if high_pct > 10:
            insights.append(f"ALERT: High risk content rate ({high_pct}%) exceeds normal threshold")
        elif high_pct > 5:
            insights.append(f"NOTICE: Elevated high risk content rate ({high_pct}%)")
        else:
            insights.append(f"Normal high risk content rate ({high_pct}%)")
        
        # Platform insights
        platforms = summary['distribution']['by_platform']
        if platforms:
            top_platform = max(platforms.items(), key=lambda x: x[1])
            insights.append(f"Most content from {top_platform[0]} ({top_platform[1]} posts)")
        
        # Keyword insights
        top_keywords = list(summary['top_keywords'].keys())[:5]
        if top_keywords:
            insights.append(f"Top detected keywords: {', '.join(top_keywords)}")
        
        # Recommendations
        recommendations = []
        
        if high_pct > 10:
            recommendations.append("Recommend immediate review of high-risk content")
            recommendations.append("Consider increasing monitoring frequency")
        
        if len(high_risk) > 0:
            recommendations.append(f"Review {len(high_risk)} high-risk posts for potential action")
        
        recommendations.append("Continue regular monitoring schedule")
        
        executive_report = {
            "report_type": "executive",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": {
                "total_analyzed": total,
                "high_risk_count": len(high_risk),
                "risk_rate": f"{high_pct}%",
                "status": "ELEVATED" if high_pct > 5 else "NORMAL"
            },
            "key_insights": insights,
            "recommendations": recommendations,
            "overview": summary['overview'],
            "top_sources": summary['distribution']['by_subreddit'],
            "top_indicators": dict(list(summary['top_keywords'].items())[:10])
        }
        
        return executive_report
    
    def save_report(
        self, 
        report: Dict[str, Any], 
        filename: Optional[str] = None
    ) -> str:
        """
        Save report to file
        
        Args:
            report: Report data
            filename: Optional filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{report['report_type']}_{timestamp}"
        
        if self.config.format == "json":
            return self.file_manager.save_json(report, filename, "reports")
        elif self.config.format == "markdown":
            return self._save_markdown(report, filename)
        else:
            return self.file_manager.save_json(report, filename, "reports")
    
    def _save_markdown(self, report: Dict[str, Any], filename: str) -> str:
        """Save report as markdown"""
        md_content = self._report_to_markdown(report)
        
        filepath = Path(config.DATA_DIR) / "reports" / f"{filename}.md"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(filepath)
    
    def _report_to_markdown(self, report: Dict[str, Any]) -> str:
        """Convert report to markdown format"""
        lines = []
        
        lines.append(f"# Weapons Detection Analysis Report")
        lines.append(f"\n**Report Type:** {report.get('report_type', 'summary')}")
        lines.append(f"**Generated:** {report.get('generated_at', 'N/A')}")
        
        if 'executive_summary' in report:
            lines.append("\n## Executive Summary")
            summary = report['executive_summary']
            lines.append(f"- **Total Analyzed:** {summary.get('total_analyzed', 0)}")
            lines.append(f"- **High Risk Count:** {summary.get('high_risk_count', 0)}")
            lines.append(f"- **Risk Rate:** {summary.get('risk_rate', 'N/A')}")
            lines.append(f"- **Status:** {summary.get('status', 'N/A')}")
        
        if 'overview' in report:
            lines.append("\n## Overview")
            overview = report['overview']
            lines.append(f"- Total Posts: {overview.get('total_posts_analyzed', 0)}")
            lines.append(f"- High Risk: {overview.get('high_risk_count', 0)}")
            lines.append(f"- Medium Risk: {overview.get('medium_risk_count', 0)}")
            lines.append(f"- Low Risk: {overview.get('low_risk_count', 0)}")
        
        if 'key_insights' in report:
            lines.append("\n## Key Insights")
            for insight in report['key_insights']:
                lines.append(f"- {insight}")
        
        if 'recommendations' in report:
            lines.append("\n## Recommendations")
            for rec in report['recommendations']:
                lines.append(f"- {rec}")
        
        if 'top_keywords' in report:
            lines.append("\n## Top Keywords")
            for kw, count in list(report['top_keywords'].items())[:10]:
                lines.append(f"- {kw}: {count}")
        
        return "\n".join(lines)

