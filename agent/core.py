"""
Core Research Agent

Main orchestration class that coordinates research, analysis, and reporting
using IO Intelligence APIs for autonomous operation.
"""

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass

from .research import WebResearcher
from .summarizer import ContentSummarizer
from .reporter import ReportGenerator
from .multi_agent_system import MultiAgentResearchSystem
from utils.io_client import IOIntelligenceClient
from utils.mock_io_client import MockIOIntelligenceClient

@dataclass
class ResearchResult:
    """Container for research results."""
    topic: str
    sources: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    report: str
    metadata: Dict[str, Any]

class ResearchAgent:
    """
    Main Research Agent that orchestrates the entire research process.
    
    Uses IO Intelligence APIs to:
    1. Research web sources autonomously
    2. Analyze and summarize content
    3. Generate structured reports
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.io_client = None
        self.researcher = WebResearcher(settings)
        self.multi_agent_system = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize IO client with fallback to mock if needed."""
        if getattr(self.settings, 'use_mock_api', False):
            self.io_client = MockIOIntelligenceClient(self.settings)
            print("🔧 Using Mock IO Intelligence API for development")
        else:
            self.io_client = IOIntelligenceClient(self.settings)
        
        self.summarizer = ContentSummarizer(self.io_client)
        self.reporter = ReportGenerator(self.io_client)
        self.multi_agent_system = MultiAgentResearchSystem(self.settings)
        
    async def research_topic(self, topic: str, depth: str = 'standard') -> List[Dict[str, Any]]:
        """
        Research a topic and gather relevant sources.
        
        Args:
            topic: The research topic
            depth: Research depth (quick, standard, detailed)
            
        Returns:
            List of source dictionaries with content and metadata
        """
        
        # Determine number of sources based on depth
        source_limits = {
            'quick': min(5, self.settings.max_sources),
            'standard': min(10, self.settings.max_sources),
            'detailed': self.settings.max_sources
        }
        
        max_sources = source_limits.get(depth, 10)
        
        # Use IO Intelligence to generate search queries
        search_queries = await self._generate_search_queries(topic, depth)
        
        # Research each query
        all_sources = []
        for query in search_queries:
            sources = await self.researcher.search_and_extract(query, max_sources // len(search_queries))
            all_sources.extend(sources)
        
        # Remove duplicates and rank sources
        unique_sources = self._deduplicate_sources(all_sources)
        ranked_sources = await self._rank_sources(unique_sources, topic)
        
        return ranked_sources[:max_sources]
    
    async def analyze_content(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze collected sources using IO Intelligence.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Analysis results with summaries, insights, and themes
        """
        
        # Summarize each source
        summaries = []
        for source in sources:
            summary = await self.summarizer.summarize_content(
                source['content'], 
                source['title']
            )
            summaries.append({
                'source': source,
                'summary': summary
            })
        
        # Generate overall analysis
        combined_content = '\n\n'.join([s['summary'] for s in summaries])
        
        analysis = await self.summarizer.analyze_themes(combined_content)
        
        return {
            'summaries': summaries,
            'themes': analysis.get('themes', []),
            'key_insights': analysis.get('insights', []),
            'sentiment': analysis.get('sentiment', 'neutral'),
            'confidence': analysis.get('confidence', 0.8)
        }
    
    async def generate_report(self, analysis: Dict[str, Any], format: str = 'markdown') -> str:
        """
        Generate a structured report from analysis results.
        
        Args:
            analysis: Analysis results from analyze_content
            format: Output format (markdown, json, txt)
            
        Returns:
            Formatted report string
        """
        
        return await self.reporter.generate_report(analysis, format)
    
    async def research_with_multi_agents(self, topic: str, depth: str = 'standard') -> Dict[str, Any]:
        """
        Conduct advanced research using the multi-agent system.
        
        Args:
            topic: The research topic
            depth: Research depth (quick, standard, detailed)
            
        Returns:
            Comprehensive research results from multiple specialized agents
        """
        
        # Initialize multi-agent system if not already done
        if not hasattr(self.multi_agent_system, 'agents') or not self.multi_agent_system.agents:
            await self.multi_agent_system.initialize_agents()
        
        # Conduct multi-agent research
        return await self.multi_agent_system.research_with_agents(topic, depth)
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents in the multi-agent system."""
        if self.multi_agent_system:
            return self.multi_agent_system.get_agent_status()
        return {}
    
    async def _generate_search_queries(self, topic: str, depth: str) -> List[str]:
        """Generate search queries using IO Intelligence."""
        
        prompt = f"""
        Generate {3 if depth == 'detailed' else 2} diverse search queries for researching: "{topic}"
        
        Make queries specific and varied to capture different aspects:
        - Current trends and developments
        - Expert opinions and analysis
        - Statistical data and research
        
        Return only the queries, one per line.
        """
        
        response = await self.io_client.generate_text(prompt, max_tokens=200)
        queries = [q.strip() for q in response.split('\n') if q.strip()]
        
        # Fallback if AI doesn't generate good queries
        if not queries:
            queries = [topic, f"{topic} trends 2025", f"{topic} analysis"]
        
        return queries[:3]
    
    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on URL and title similarity."""
        
        seen_urls = set()
        unique_sources = []
        
        for source in sources:
            url = source.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        return unique_sources
    
    async def _rank_sources(self, sources: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Rank sources by relevance using IO Intelligence."""
        
        if len(sources) <= 5:
            return sources
        
        # Use IO Intelligence to score relevance
        scored_sources = []
        
        for source in sources:
            relevance_prompt = f"""
            Rate the relevance of this content to the topic "{topic}" on a scale of 1-10:
            
            Title: {source.get('title', 'No title')}
            Content preview: {source.get('content', '')[:500]}...
            
            Return only a number between 1-10.
            """
            
            try:
                score_response = await self.io_client.generate_text(relevance_prompt, max_tokens=10)
                score = float(score_response.strip())
                scored_sources.append((score, source))
            except:
                # Default score if AI fails
                scored_sources.append((5.0, source))
        
        # Sort by score (highest first)
        scored_sources.sort(key=lambda x: x[0], reverse=True)
        
        return [source for score, source in scored_sources]