#!/usr/bin/env python3
"""
Real Data Demo with IO Intelligence
Complete integration of IO Intelligence API with your research system.
"""

import asyncio
import os
import json
from datetime import datetime
from iointel import Agent, Workflow

# Set up environment variables for IO Intelligence
os.environ["IO_API_KEY"] = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImNjOTcyYTVhLTM1MTAtNDFmMC05ODA3LWY2NDc4M2Y0YTFlZCIsImV4cCI6NDkwNjYyMDAyNn0.D3nqreeXTd-MZUjKNkNr6-oE8SYQGDMYQGUfN84G2rGbaWxFVA0GvbXEvYmfrHstdRlF-CQSpMO5Awpjiic-Kw"
os.environ["IO_API_BASE_URL"] = "https://api.intelligence.io.solutions/api/v1"
os.environ["IO_API_MODEL"] = "meta-llama/Llama-3.3-70B-Instruct"

class IOIntelligenceResearcher:
    """Real IO Intelligence research system."""
    
    def __init__(self):
        self.api_key = os.environ["IO_API_KEY"]
        self.base_url = os.environ["IO_API_BASE_URL"]
        self.model = os.environ["IO_API_MODEL"]
    
    def create_agent(self, name: str, instructions: str) -> Agent:
        """Create an IO Intelligence agent."""
        return Agent(
            name=name,
            instructions=instructions,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def research_topic(self, topic: str) -> dict:
        """Research a topic using IO Intelligence."""
        
        print(f"🔍 Researching: {topic}")
        
        # Create research workflow
        research_prompt = f"Provide comprehensive research on: {topic}. Include current developments, key applications, challenges, and future prospects."
        
        workflow = Workflow(objective=research_prompt, client_mode=False)
        agent = self.create_agent(
            name="Research Specialist",
            instructions="You are an expert researcher who provides detailed, accurate, and up-to-date information on technology topics."
        )
        
        try:
            results = await workflow.summarize_text(max_words=150, agents=[agent]).run_tasks()
            
            return {
                "topic": topic,
                "summary": results["results"]["summarize_text"].summary,
                "key_points": results["results"]["summarize_text"].key_points,
                "conversation_id": results["conversation_id"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Research error for {topic}: {e}")
            return {"topic": topic, "error": str(e)}
    
    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using IO Intelligence."""
        
        sentiment_prompt = f"Analyze the sentiment of this text and provide a brief analysis: {text}"
        
        workflow = Workflow(objective=sentiment_prompt, client_mode=False)
        agent = self.create_agent(
            name="Sentiment Analyzer",
            instructions="You are an expert at analyzing sentiment and emotional tone in text. Provide clear, concise analysis."
        )
        
        try:
            results = await workflow.summarize_text(max_words=50, agents=[agent]).run_tasks()
            
            return {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment_analysis": results["results"]["summarize_text"].summary,
                "key_insights": results["results"]["summarize_text"].key_points,
                "conversation_id": results["conversation_id"]
            }
        except Exception as e:
            return {"text": text, "error": str(e)}
    
    async def generate_report(self, research_results: list) -> dict:
        """Generate a comprehensive report from research results."""
        
        # Combine all research summaries
        combined_text = "\\n\\n".join([
            f"Topic: {result['topic']}\\nSummary: {result.get('summary', 'No summary available')}\\nKey Points: {', '.join(result.get('key_points', []))}"
            for result in research_results if 'error' not in result
        ])
        
        report_prompt = f"Create a comprehensive research report based on the following research findings:\\n\\n{combined_text}"
        
        workflow = Workflow(objective=report_prompt, client_mode=False)
        agent = self.create_agent(
            name="Report Writer",
            instructions="You are an expert report writer who creates well-structured, professional reports from research data."
        )
        
        try:
            results = await workflow.summarize_text(max_words=200, agents=[agent]).run_tasks()
            
            return {
                "report_summary": results["results"]["summarize_text"].summary,
                "key_findings": results["results"]["summarize_text"].key_points,
                "conversation_id": results["conversation_id"],
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

async def demo_real_research():
    """Demonstrate real research using IO Intelligence."""
    
    print("🚀 Real Data Research Demo with IO Intelligence")
    print("=" * 80)
    
    researcher = IOIntelligenceResearcher()
    
    # Research topics for hackathon demo
    topics = [
        "artificial intelligence trends 2025",
        "blockchain applications in supply chain",
        "quantum computing breakthroughs",
        "machine learning in healthcare diagnostics"
    ]
    
    research_results = []
    
    # Conduct research on each topic
    for i, topic in enumerate(topics, 1):
        print(f"\\n{i}️⃣ Researching: {topic}")
        result = await researcher.research_topic(topic)
        research_results.append(result)
        
        if 'error' not in result:
            print(f"✅ Research completed")
            print(f"Summary: {result['summary'][:100]}...")
            print(f"Key Points: {', '.join(result['key_points'][:3])}")
        else:
            print(f"❌ Research failed: {result['error']}")
    
    # Generate comprehensive report
    print("\\n📊 Generating comprehensive report...")
    report = await researcher.generate_report(research_results)
    
    if 'error' not in report:
        print("✅ Report generated successfully!")
        print(f"Report Summary: {report['report_summary'][:150]}...")
    
    # Save all results
    final_results = {
        "research_results": research_results,
        "comprehensive_report": report,
        "metadata": {
            "total_topics": len(topics),
            "successful_research": len([r for r in research_results if 'error' not in r]),
            "generated_at": datetime.now().isoformat(),
            "api_used": "IO Intelligence",
            "model": os.environ["IO_API_MODEL"]
        }
    }
    
    # Convert to JSON-serializable format
    json_results = json.loads(json.dumps(final_results, default=str))
    
    with open("real_io_research_demo.json", "w") as f:
        json.dump(json_results, f, indent=2)
    
    print("\\n💾 Results saved to: real_io_research_demo.json")
    
    return final_results

async def demo_sentiment_analysis():
    """Demonstrate sentiment analysis with real IO Intelligence."""
    
    print("\\n" + "=" * 80)
    print("😊 Sentiment Analysis Demo")
    print("=" * 80)
    
    researcher = IOIntelligenceResearcher()
    
    # Sample texts for sentiment analysis
    texts = [
        "The new AI breakthrough is absolutely revolutionary and will transform healthcare forever!",
        "I'm concerned about the potential risks and ethical implications of this technology.",
        "The research findings are interesting but require further validation and testing."
    ]
    
    sentiment_results = []
    
    for i, text in enumerate(texts, 1):
        print(f"\\n{i}️⃣ Analyzing sentiment...")
        result = await researcher.analyze_sentiment(text)
        sentiment_results.append(result)
        
        if 'error' not in result:
            print(f"✅ Analysis completed")
            print(f"Text: {result['text']}")
            print(f"Analysis: {result['sentiment_analysis']}")
        else:
            print(f"❌ Analysis failed: {result['error']}")
    
    return sentiment_results

async def main():
    """Run the complete real data demo."""
    
    print("🌟 IO Intelligence Real Data Integration Demo")
    print("=" * 80)
    print(f"API Key: {os.environ['IO_API_KEY'][:30]}...")
    print(f"Base URL: {os.environ['IO_API_BASE_URL']}")
    print(f"Model: {os.environ['IO_API_MODEL']}")
    
    # Demo 1: Real research
    research_results = await demo_real_research()
    
    # Demo 2: Sentiment analysis
    sentiment_results = await demo_sentiment_analysis()
    
    # Final summary
    print("\\n" + "=" * 80)
    print("🎉 DEMO COMPLETE - REAL DATA INTEGRATION SUCCESSFUL!")
    print("=" * 80)
    
    successful_research = len([r for r in research_results["research_results"] if 'error' not in r])
    successful_sentiment = len([r for r in sentiment_results if 'error' not in r])
    
    print(f"✅ Research Topics Completed: {successful_research}/4")
    print(f"✅ Sentiment Analyses Completed: {successful_sentiment}/3")
    print(f"✅ Comprehensive Report: {'Generated' if 'error' not in research_results['comprehensive_report'] else 'Failed'}")
    
    print("\\n🚀 Your hackathon project now has:")
    print("   • Real IO Intelligence API integration")
    print("   • Multi-topic research capability")
    print("   • Sentiment analysis functionality")
    print("   • Automated report generation")
    print("   • JSON data export for web interface")
    
    print("\\n🏆 Ready for Launch IO Hackathon submission!")

if __name__ == "__main__":
    asyncio.run(main())