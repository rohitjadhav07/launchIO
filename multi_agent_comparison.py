#!/usr/bin/env python3
"""
Multi-AI Agent Comparison System
Using multiple AI models from the iointel repository to compare results
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import os

# Import from the cloned iointel repository
import sys
sys.path.append('./iointel')

from iointel import Agent, Workflow
from real_data_demo import IOIntelligenceResearcher

class MultiAgentComparison:
    """Multi-AI agent system for comparing different models"""
    
    def __init__(self):
        self.io_researcher = IOIntelligenceResearcher()
        self.agents = {}
        self.comparison_results = []
        
        # Initialize different AI agents with various models
        self.setup_agents()
    
    def setup_agents(self):
        """Setup multiple AI agents with different models and configurations"""
        
        # Agent configurations with different models and personalities
        agent_configs = [
            {
                "name": "IO_Intelligence_Researcher",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "instructions": "You are a comprehensive research specialist focused on providing detailed, accurate analysis with citations and evidence.",
                "api_key": os.environ.get("IO_API_KEY", ""),
                "base_url": "https://api.intelligence.io.solutions/api/v1",
                "specialty": "Comprehensive Research"
            },
            {
                "name": "Critical_Analyst",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "instructions": "You are a critical analyst who questions assumptions, identifies potential biases, and provides balanced perspectives on research topics.",
                "api_key": os.environ.get("IO_API_KEY", ""),
                "base_url": "https://api.intelligence.io.solutions/api/v1",
                "specialty": "Critical Analysis"
            },
            {
                "name": "Technical_Expert",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "instructions": "You are a technical expert who focuses on implementation details, technical feasibility, and practical applications.",
                "api_key": os.environ.get("IO_API_KEY", ""),
                "base_url": "https://api.intelligence.io.solutions/api/v1",
                "specialty": "Technical Analysis"
            },
            {
                "name": "Business_Strategist",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "instructions": "You are a business strategist who analyzes market implications, business opportunities, and economic impact.",
                "api_key": os.environ.get("IO_API_KEY", ""),
                "base_url": "https://api.intelligence.io.solutions/api/v1",
                "specialty": "Business Strategy"
            },
            {
                "name": "Innovation_Scout",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "instructions": "You are an innovation scout who identifies emerging trends, future possibilities, and disruptive potential.",
                "api_key": os.environ.get("IO_API_KEY", ""),
                "base_url": "https://api.intelligence.io.solutions/api/v1",
                "specialty": "Innovation & Trends"
            },
            {
                "name": "Risk_Assessor",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "instructions": "You are a risk assessment specialist who identifies potential challenges, limitations, and mitigation strategies.",
                "api_key": os.environ.get("IO_API_KEY", ""),
                "base_url": "https://api.intelligence.io.solutions/api/v1",
                "specialty": "Risk Assessment"
            }
        ]
        
        # Create agents
        for config in agent_configs:
            try:
                if config["api_key"]:
                    agent = Agent(
                        name=config["name"],
                        instructions=config["instructions"],
                        model=config["model"],
                        api_key=config["api_key"],
                        base_url=config["base_url"]
                    )
                    self.agents[config["name"]] = {
                        "agent": agent,
                        "specialty": config["specialty"],
                        "model": config["model"]
                    }
                    print(f"✅ Created agent: {config['name']}")
                else:
                    print(f"⚠️ Skipping {config['name']} - No API key")
            except Exception as e:
                print(f"❌ Failed to create agent {config['name']}: {e}")
    
    async def run_multi_agent_analysis(self, topic: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Run analysis with multiple agents and compare results"""
        
        print(f"\n🚀 Starting multi-agent analysis on: {topic}")
        print(f"📊 Analysis type: {analysis_type}")
        print(f"🤖 Active agents: {len(self.agents)}")
        
        results = {
            "topic": topic,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "agent_results": {},
            "comparison": {},
            "summary": {}
        }
        
        # Run analysis with each agent
        for agent_name, agent_info in self.agents.items():
            print(f"\n🔄 Running analysis with {agent_name}...")
            
            try:
                # Create specialized prompt based on agent's specialty
                specialized_prompt = self.create_specialized_prompt(topic, agent_info["specialty"], analysis_type)
                
                # Use workflow for consistent results
                workflow = Workflow(objective=specialized_prompt, client_mode=False)
                agent_results = await workflow.summarize_text(max_words=200, agents=[agent_info["agent"]]).run_tasks()
                
                # Extract and store results
                if "results" in agent_results and "summarize_text" in agent_results["results"]:
                    summary_result = agent_results["results"]["summarize_text"]
                    
                    results["agent_results"][agent_name] = {
                        "specialty": agent_info["specialty"],
                        "model": agent_info["model"],
                        "summary": summary_result.summary if hasattr(summary_result, 'summary') else str(summary_result),
                        "key_points": summary_result.key_points if hasattr(summary_result, 'key_points') else [],
                        "conversation_id": agent_results.get("conversation_id", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    print(f"✅ {agent_name} completed analysis")
                else:
                    print(f"⚠️ {agent_name} returned unexpected format")
                    
            except Exception as e:
                print(f"❌ {agent_name} failed: {e}")
                results["agent_results"][agent_name] = {
                    "specialty": agent_info["specialty"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Generate comparison analysis
        results["comparison"] = await self.generate_comparison_analysis(results["agent_results"])
        
        # Generate executive summary
        results["summary"] = await self.generate_executive_summary(results["agent_results"], topic)
        
        # Store results
        self.comparison_results.append(results)
        
        return results
    
    def create_specialized_prompt(self, topic: str, specialty: str, analysis_type: str) -> str:
        """Create specialized prompts based on agent specialty"""
        
        base_prompt = f"Analyze the topic: {topic}"
        
        specialty_prompts = {
            "Comprehensive Research": f"{base_prompt}. Provide a thorough research overview with evidence, statistics, and credible sources.",
            "Critical Analysis": f"{base_prompt}. Critically examine assumptions, identify potential biases, and present balanced perspectives.",
            "Technical Analysis": f"{base_prompt}. Focus on technical implementation, feasibility, and practical applications.",
            "Business Strategy": f"{base_prompt}. Analyze market opportunities, business implications, and economic impact.",
            "Innovation & Trends": f"{base_prompt}. Identify emerging trends, future possibilities, and disruptive potential.",
            "Risk Assessment": f"{base_prompt}. Assess potential risks, challenges, limitations, and mitigation strategies."
        }
        
        return specialty_prompts.get(specialty, base_prompt)
    
    async def generate_comparison_analysis(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison analysis between different agents"""
        
        comparison = {
            "consensus_points": [],
            "divergent_views": [],
            "unique_insights": {},
            "confidence_analysis": {},
            "recommendation_synthesis": ""
        }
        
        # Extract all summaries for comparison
        summaries = {}
        all_key_points = []
        
        for agent_name, result in agent_results.items():
            if "error" not in result:
                summaries[agent_name] = result.get("summary", "")
                all_key_points.extend(result.get("key_points", []))
        
        # Find common themes (simplified approach)
        key_point_frequency = {}
        for point in all_key_points:
            key_point_frequency[point] = key_point_frequency.get(point, 0) + 1
        
        # Identify consensus points (mentioned by multiple agents)
        comparison["consensus_points"] = [
            point for point, freq in key_point_frequency.items() if freq > 1
        ]
        
        # Identify unique insights per agent
        for agent_name, result in agent_results.items():
            if "error" not in result:
                unique_points = [
                    point for point in result.get("key_points", [])
                    if key_point_frequency.get(point, 0) == 1
                ]
                if unique_points:
                    comparison["unique_insights"][agent_name] = unique_points
        
        return comparison
    
    async def generate_executive_summary(self, agent_results: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Generate executive summary combining all agent insights"""
        
        # Combine all successful analyses
        combined_insights = []
        successful_agents = []
        
        for agent_name, result in agent_results.items():
            if "error" not in result:
                successful_agents.append(agent_name)
                combined_insights.append(f"{result['specialty']}: {result.get('summary', '')}")
        
        summary = {
            "topic": topic,
            "agents_consulted": len(successful_agents),
            "successful_analyses": len([r for r in agent_results.values() if "error" not in r]),
            "key_findings": combined_insights[:5],  # Top 5 findings
            "overall_assessment": f"Multi-agent analysis of '{topic}' completed with {len(successful_agents)} specialized perspectives.",
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
    
    def generate_detailed_report(self, results: Dict[str, Any], format_type: str = "markdown") -> str:
        """Generate detailed downloadable report"""
        
        if format_type == "markdown":
            return self.generate_markdown_report(results)
        elif format_type == "json":
            return json.dumps(results, indent=2)
        elif format_type == "html":
            return self.generate_html_report(results)
        else:
            return self.generate_text_report(results)
    
    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate detailed markdown report"""
        
        report = f"""# Multi-Agent Analysis Report

## Topic: {results['topic']}
**Analysis Type:** {results['analysis_type']}  
**Generated:** {results['timestamp']}  
**Agents Consulted:** {len(results['agent_results'])}

---

## Executive Summary

{results['summary'].get('overall_assessment', 'No summary available')}

**Key Statistics:**
- Agents Consulted: {results['summary'].get('agents_consulted', 0)}
- Successful Analyses: {results['summary'].get('successful_analyses', 0)}

---

## Agent Analysis Results

"""
        
        for agent_name, result in results['agent_results'].items():
            if "error" not in result:
                report += f"""### {agent_name}
**Specialty:** {result['specialty']}  
**Model:** {result['model']}

**Analysis:**
{result.get('summary', 'No summary available')}

**Key Points:**
"""
                for point in result.get('key_points', []):
                    report += f"- {point}\n"
                
                report += "\n---\n\n"
            else:
                report += f"""### {agent_name} ❌
**Error:** {result['error']}

---

"""
        
        # Add comparison section
        comparison = results.get('comparison', {})
        if comparison:
            report += """## Comparative Analysis

### Consensus Points
"""
            for point in comparison.get('consensus_points', []):
                report += f"- {point}\n"
            
            report += "\n### Unique Insights by Agent\n"
            for agent, insights in comparison.get('unique_insights', {}).items():
                report += f"\n**{agent}:**\n"
                for insight in insights:
                    report += f"- {insight}\n"
        
        report += f"""

---

## Report Metadata
- **Generated by:** Multi-Agent Comparison System
- **Powered by:** IO Intelligence (Llama-3.3-70B-Instruct)
- **Report ID:** {str(uuid.uuid4())[:8]}
- **Generation Time:** {datetime.now().isoformat()}

*This report was generated using multiple AI agents with specialized perspectives to provide comprehensive analysis.*
"""
        
        return report
    
    def generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate detailed HTML report"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Analysis Report - {results['topic']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }}
        .agent-result {{ background: #f8f9fa; border-left: 4px solid #007bff; padding: 1rem; margin: 1rem 0; border-radius: 5px; }}
        .error {{ border-left-color: #dc3545; background: #f8d7da; }}
        .key-points {{ background: white; padding: 1rem; border-radius: 5px; margin-top: 1rem; }}
        .comparison {{ background: #e9ecef; padding: 1.5rem; border-radius: 10px; margin: 2rem 0; }}
        .metadata {{ background: #343a40; color: white; padding: 1rem; border-radius: 5px; margin-top: 2rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Multi-Agent Analysis Report</h1>
        <h2>{results['topic']}</h2>
        <p><strong>Generated:</strong> {results['timestamp']}</p>
        <p><strong>Agents Consulted:</strong> {len(results['agent_results'])}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Executive Summary</h2>
        <p>{results['summary'].get('overall_assessment', 'No summary available')}</p>
    </div>
    
    <h2>🔍 Agent Analysis Results</h2>
"""
        
        for agent_name, result in results['agent_results'].items():
            if "error" not in result:
                html += f"""
    <div class="agent-result">
        <h3>🤖 {agent_name}</h3>
        <p><strong>Specialty:</strong> {result['specialty']}</p>
        <p><strong>Model:</strong> {result['model']}</p>
        <p><strong>Analysis:</strong></p>
        <p>{result.get('summary', 'No summary available')}</p>
        <div class="key-points">
            <strong>Key Points:</strong>
            <ul>
"""
                for point in result.get('key_points', []):
                    html += f"<li>{point}</li>"
                
                html += """
            </ul>
        </div>
    </div>
"""
            else:
                html += f"""
    <div class="agent-result error">
        <h3>❌ {agent_name}</h3>
        <p><strong>Error:</strong> {result['error']}</p>
    </div>
"""
        
        # Add comparison section
        comparison = results.get('comparison', {})
        if comparison:
            html += """
    <div class="comparison">
        <h2>⚖️ Comparative Analysis</h2>
        <h3>Consensus Points</h3>
        <ul>
"""
            for point in comparison.get('consensus_points', []):
                html += f"<li>{point}</li>"
            
            html += """
        </ul>
        <h3>Unique Insights by Agent</h3>
"""
            for agent, insights in comparison.get('unique_insights', {}).items():
                html += f"<h4>{agent}:</h4><ul>"
                for insight in insights:
                    html += f"<li>{insight}</li>"
                html += "</ul>"
        
        html += f"""
    </div>
    
    <div class="metadata">
        <h3>📋 Report Metadata</h3>
        <p><strong>Generated by:</strong> Multi-Agent Comparison System</p>
        <p><strong>Powered by:</strong> IO Intelligence (Llama-3.3-70B-Instruct)</p>
        <p><strong>Report ID:</strong> {str(uuid.uuid4())[:8]}</p>
        <p><strong>Generation Time:</strong> {datetime.now().isoformat()}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def save_report(self, results: Dict[str, Any], format_type: str = "markdown", filename: str = None) -> str:
        """Save report to file and return filename"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_safe = "".join(c for c in results['topic'] if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
            filename = f"multi_agent_report_{topic_safe}_{timestamp}.{format_type}"
        
        report_content = self.generate_detailed_report(results, format_type)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 Report saved: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return None

# Test function
async def test_multi_agent_system():
    """Test the multi-agent comparison system"""
    
    print("🚀 Initializing Multi-Agent Comparison System...")
    
    # Initialize the system
    multi_agent = MultiAgentComparison()
    
    if not multi_agent.agents:
        print("❌ No agents available. Please check your API configuration.")
        return
    
    # Test topics
    test_topics = [
        "artificial intelligence in healthcare",
        "blockchain technology adoption",
        "quantum computing applications"
    ]
    
    for topic in test_topics:
        print(f"\n{'='*60}")
        print(f"🔬 Testing with topic: {topic}")
        print('='*60)
        
        # Run multi-agent analysis
        results = await multi_agent.run_multi_agent_analysis(topic, "comprehensive")
        
        # Generate and save reports in different formats
        markdown_file = multi_agent.save_report(results, "markdown")
        html_file = multi_agent.save_report(results, "html")
        json_file = multi_agent.save_report(results, "json")
        
        print(f"\n📊 Analysis completed for: {topic}")
        print(f"📄 Reports generated:")
        print(f"   - Markdown: {markdown_file}")
        print(f"   - HTML: {html_file}")
        print(f"   - JSON: {json_file}")
        
        # Show summary
        summary = results.get('summary', {})
        print(f"\n📈 Summary:")
        print(f"   - Agents consulted: {summary.get('agents_consulted', 0)}")
        print(f"   - Successful analyses: {summary.get('successful_analyses', 0)}")
        
        # Break after first topic for demo
        break

if __name__ == "__main__":
    # Set up environment
    os.environ["IO_API_KEY"] = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImNjOTcyYTVhLTM1MTAtNDFmMC05ODA3LWY2NDc4M2Y0YTFlZCIsImV4cCI6NDkwNjYyMDAyNn0.D3nqreeXTd-MZUjKNkNr6-oE8SYQGDMYQGUfN84G2rGbaWxFVA0GvbXEvYmfrHstdRlF-CQSpMO5Awpjiic-Kw"
    
    print("🌟 Multi-Agent AI Comparison System")
    print("=" * 50)
    print("Features:")
    print("• Multiple specialized AI agents")
    print("• Comparative analysis")
    print("• Detailed report generation")
    print("• Multiple export formats")
    print("=" * 50)
    
    asyncio.run(test_multi_agent_system())