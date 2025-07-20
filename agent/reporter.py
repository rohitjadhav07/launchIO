"""
Report Generation Module

Generates structured reports in various formats using IO Intelligence.
"""

import json
from datetime import datetime
from typing import Dict, Any

class ReportGenerator:
    """
    Report generation component that creates structured reports
    from analysis results using IO Intelligence.
    """
    
    def __init__(self, io_client):
        self.io_client = io_client
    
    async def generate_report(self, analysis: Dict[str, Any], format: str = 'markdown') -> str:
        """
        Generate a structured report from analysis results.
        
        Args:
            analysis: Analysis results containing summaries, themes, insights
            format: Output format (markdown, json, txt)
            
        Returns:
            Formatted report string
        """
        
        if format == 'json':
            return await self._generate_json_report(analysis)
        elif format == 'txt':
            return await self._generate_text_report(analysis)
        else:  # markdown (default)
            return await self._generate_markdown_report(analysis)
    
    async def _generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a markdown-formatted report."""
        
        # Extract data
        summaries = analysis.get('summaries', [])
        themes = analysis.get('themes', [])
        insights = analysis.get('key_insights', [])
        sentiment = analysis.get('sentiment', 'neutral')
        confidence = analysis.get('confidence', 0.8)
        
        # Use IO Intelligence to generate executive summary
        executive_summary = await self._generate_executive_summary(analysis)
        
        # Build markdown report
        report = f"""# Research Report
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

{executive_summary}

## Key Findings

### Main Themes
{self._format_list(themes)}

### Key Insights
{self._format_list(insights)}

## Analysis Overview

- **Sentiment**: {sentiment.title()}
- **Confidence Level**: {confidence:.1%}
- **Sources Analyzed**: {len(summaries)}

## Detailed Analysis

### Source Summaries

"""
        
        # Add individual source summaries
        for i, summary_data in enumerate(summaries, 1):
            source = summary_data.get('source', {})
            summary = summary_data.get('summary', '')
            
            report += f"""#### Source {i}: {source.get('title', 'Untitled')}

**URL**: {source.get('url', 'N/A')}  
**Type**: {source.get('source_type', 'web').title()}  
**Published**: {source.get('published', 'N/A')}

{summary}

---

"""
        
        # Add recommendations
        recommendations = await self._generate_recommendations(analysis)
        report += f"""## Recommendations

{recommendations}

## Methodology

This report was generated using AI-powered research and analysis:

1. **Source Collection**: Automated web research and content extraction
2. **Content Analysis**: AI-powered summarization and theme extraction  
3. **Insight Generation**: Pattern recognition and key finding identification
4. **Report Synthesis**: Structured presentation of findings and recommendations

*Powered by IO Intelligence*
"""
        
        return report
    
    async def _generate_json_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a JSON-formatted report."""
        
        executive_summary = await self._generate_executive_summary(analysis)
        recommendations = await self._generate_recommendations(analysis)
        
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "json",
                "version": "1.0"
            },
            "executive_summary": executive_summary,
            "analysis": {
                "themes": analysis.get('themes', []),
                "key_insights": analysis.get('key_insights', []),
                "sentiment": analysis.get('sentiment', 'neutral'),
                "confidence": analysis.get('confidence', 0.8)
            },
            "sources": [
                {
                    "title": s.get('source', {}).get('title', ''),
                    "url": s.get('source', {}).get('url', ''),
                    "type": s.get('source', {}).get('source_type', 'web'),
                    "published": s.get('source', {}).get('published', ''),
                    "summary": s.get('summary', '')
                }
                for s in analysis.get('summaries', [])
            ],
            "recommendations": recommendations.split('\n') if recommendations else [],
            "statistics": {
                "total_sources": len(analysis.get('summaries', [])),
                "avg_confidence": analysis.get('confidence', 0.8)
            }
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    async def _generate_text_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a plain text report."""
        
        summaries = analysis.get('summaries', [])
        themes = analysis.get('themes', [])
        insights = analysis.get('key_insights', [])
        
        executive_summary = await self._generate_executive_summary(analysis)
        recommendations = await self._generate_recommendations(analysis)
        
        report = f"""RESEARCH REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
{executive_summary}

KEY FINDINGS

Main Themes:
{self._format_text_list(themes)}

Key Insights:
{self._format_text_list(insights)}

ANALYSIS OVERVIEW
- Sentiment: {analysis.get('sentiment', 'neutral').title()}
- Confidence: {analysis.get('confidence', 0.8):.1%}
- Sources: {len(summaries)}

SOURCE SUMMARIES

"""
        
        for i, summary_data in enumerate(summaries, 1):
            source = summary_data.get('source', {})
            summary = summary_data.get('summary', '')
            
            report += f"""Source {i}: {source.get('title', 'Untitled')}
URL: {source.get('url', 'N/A')}
Type: {source.get('source_type', 'web').title()}
Published: {source.get('published', 'N/A')}

{summary}

{'='*60}

"""
        
        report += f"""RECOMMENDATIONS

{recommendations}

METHODOLOGY
This report was generated using AI-powered research and analysis through
automated source collection, content analysis, and insight generation.

Powered by IO Intelligence
"""
        
        return report
    
    async def _generate_executive_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate an executive summary using IO Intelligence."""
        
        themes = analysis.get('themes', [])
        insights = analysis.get('key_insights', [])
        
        prompt = f"""
        Write a concise executive summary (2-3 paragraphs) based on this research analysis:
        
        Main Themes: {', '.join(themes)}
        Key Insights: {', '.join(insights)}
        
        The summary should:
        - Highlight the most important findings
        - Provide context and significance
        - Be accessible to both technical and non-technical readers
        
        Executive Summary:
        """
        
        try:
            summary = await self.io_client.generate_text(
                prompt,
                max_tokens=400,
                temperature=0.3
            )
            return summary.strip()
        except Exception as e:
            # Fallback summary
            return self._create_fallback_executive_summary(themes, insights)
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> str:
        """Generate recommendations using IO Intelligence."""
        
        themes = analysis.get('themes', [])
        insights = analysis.get('key_insights', [])
        
        prompt = f"""
        Based on this research analysis, provide 3-5 actionable recommendations:
        
        Themes: {', '.join(themes)}
        Insights: {', '.join(insights)}
        
        Recommendations should be:
        - Specific and actionable
        - Based on the research findings
        - Relevant for decision-makers
        
        Recommendations:
        """
        
        try:
            recommendations = await self.io_client.generate_text(
                prompt,
                max_tokens=300,
                temperature=0.4
            )
            return recommendations.strip()
        except Exception as e:
            # Fallback recommendations
            return self._create_fallback_recommendations(themes, insights)
    
    def _format_list(self, items: list) -> str:
        """Format a list for markdown."""
        if not items:
            return "- No items found"
        return '\n'.join(f"- {item}" for item in items)
    
    def _format_text_list(self, items: list) -> str:
        """Format a list for plain text."""
        if not items:
            return "- No items found"
        return '\n'.join(f"- {item}" for item in items)
    
    def _create_fallback_executive_summary(self, themes: list, insights: list) -> str:
        """Create a basic executive summary when AI fails."""
        
        summary = "This research analysis examined multiple sources to identify key themes and insights. "
        
        if themes:
            summary += f"The main themes identified include {', '.join(themes[:3])}. "
        
        if insights:
            summary += f"Key insights reveal important patterns and trends in the analyzed content. "
        
        summary += "The findings provide valuable context for understanding current developments in this area."
        
        return summary
    
    def _create_fallback_recommendations(self, themes: list, insights: list) -> str:
        """Create basic recommendations when AI fails."""
        
        recommendations = []
        
        if themes:
            recommendations.append(f"Continue monitoring developments in {themes[0] if themes else 'this area'}")
        
        recommendations.extend([
            "Conduct deeper analysis of identified trends",
            "Consider implications for strategic planning",
            "Stay updated with ongoing research and developments"
        ])
        
        return '\n'.join(f"- {rec}" for rec in recommendations)