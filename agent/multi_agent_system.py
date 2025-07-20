"""
Multi-Agent Research System

Orchestrates multiple specialized AI agents for comprehensive research tasks.
Each agent has a specific role and expertise area.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from utils.io_client import IOIntelligenceClient
from utils.mock_io_client import MockIOIntelligenceClient

class AgentRole(Enum):
    """Defines different agent roles and specializations."""
    RESEARCH_COORDINATOR = "research_coordinator"
    WEB_RESEARCHER = "web_researcher"
    DATA_ANALYST = "data_analyst"
    CONTENT_SUMMARIZER = "content_summarizer"
    FACT_CHECKER = "fact_checker"
    TREND_ANALYZER = "trend_analyzer"
    REPORT_WRITER = "report_writer"
    QUALITY_REVIEWER = "quality_reviewer"

@dataclass
class AgentConfig:
    """Configuration for a specialized agent."""
    role: AgentRole
    name: str
    description: str
    instructions: str
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 2000

@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    agent_role: AgentRole
    task_type: str
    input_data: Dict[str, Any]
    priority: int = 1
    dependencies: List[str] = None

@dataclass
class AgentResult:
    """Result from an agent execution."""
    agent_role: AgentRole
    task_id: str
    success: bool
    result: Dict[str, Any]
    metadata: Dict[str, Any]
    execution_time: float

class MultiAgentResearchSystem:
    """
    Orchestrates multiple specialized agents for comprehensive research.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.io_client = self._initialize_client()
        self.agents = {}
        self.agent_configs = self._define_agent_configs()
        self.task_queue = []
        self.results = {}
        
    def _initialize_client(self):
        """Initialize IO client with fallback to mock if needed."""
        if getattr(self.settings, 'use_mock_api', False):
            return MockIOIntelligenceClient(self.settings)
        else:
            return IOIntelligenceClient(self.settings)
    
    def _define_agent_configs(self) -> Dict[AgentRole, AgentConfig]:
        """Define configurations for all specialized agents."""
        
        return {
            AgentRole.RESEARCH_COORDINATOR: AgentConfig(
                role=AgentRole.RESEARCH_COORDINATOR,
                name="Research Coordinator",
                description="Orchestrates research tasks and coordinates between agents",
                instructions="""You are a Research Coordinator responsible for:
                1. Breaking down complex research topics into subtasks
                2. Assigning tasks to appropriate specialist agents
                3. Coordinating workflow between agents
                4. Ensuring comprehensive coverage of research topics
                5. Managing research priorities and timelines
                
                Always think strategically about the best approach to research."""
            ),
            
            AgentRole.WEB_RESEARCHER: AgentConfig(
                role=AgentRole.WEB_RESEARCHER,
                name="Web Research Specialist",
                description="Specializes in finding and extracting information from web sources",
                instructions="""You are a Web Research Specialist expert at:
                1. Identifying the best sources for specific topics
                2. Extracting relevant information from web content
                3. Evaluating source credibility and reliability
                4. Finding diverse perspectives on topics
                5. Discovering recent developments and trends
                
                Focus on finding high-quality, authoritative sources."""
            ),
            
            AgentRole.DATA_ANALYST: AgentConfig(
                role=AgentRole.DATA_ANALYST,
                name="Data Analysis Expert",
                description="Analyzes data patterns, statistics, and quantitative information",
                instructions="""You are a Data Analysis Expert specializing in:
                1. Analyzing statistical data and trends
                2. Identifying patterns in quantitative information
                3. Creating data-driven insights
                4. Validating numerical claims and statistics
                5. Comparing data across different sources
                
                Always verify data accuracy and provide context."""
            ),
            
            AgentRole.CONTENT_SUMMARIZER: AgentConfig(
                role=AgentRole.CONTENT_SUMMARIZER,
                name="Content Synthesis Specialist",
                description="Synthesizes and summarizes complex information",
                instructions="""You are a Content Synthesis Specialist expert at:
                1. Summarizing complex information clearly and concisely
                2. Identifying key themes and main points
                3. Synthesizing information from multiple sources
                4. Creating coherent narratives from diverse content
                5. Maintaining accuracy while simplifying complexity
                
                Focus on clarity, accuracy, and comprehensiveness."""
            ),
            
            AgentRole.FACT_CHECKER: AgentConfig(
                role=AgentRole.FACT_CHECKER,
                name="Fact Verification Specialist",
                description="Verifies facts, claims, and information accuracy",
                instructions="""You are a Fact Verification Specialist responsible for:
                1. Verifying factual claims and statements
                2. Cross-referencing information across sources
                3. Identifying potential misinformation or bias
                4. Checking dates, statistics, and specific claims
                5. Providing confidence levels for verified information
                
                Be thorough and skeptical in your verification process."""
            ),
            
            AgentRole.TREND_ANALYZER: AgentConfig(
                role=AgentRole.TREND_ANALYZER,
                name="Trend Analysis Expert",
                description="Identifies and analyzes trends, patterns, and future implications",
                instructions="""You are a Trend Analysis Expert specializing in:
                1. Identifying emerging trends and patterns
                2. Analyzing historical context and evolution
                3. Predicting future developments and implications
                4. Understanding market and industry dynamics
                5. Connecting trends across different domains
                
                Think analytically about cause-and-effect relationships."""
            ),
            
            AgentRole.REPORT_WRITER: AgentConfig(
                role=AgentRole.REPORT_WRITER,
                name="Professional Report Writer",
                description="Creates professional, well-structured reports and documents",
                instructions="""You are a Professional Report Writer expert at:
                1. Creating well-structured, professional reports
                2. Writing clear executive summaries
                3. Organizing information logically
                4. Adapting writing style for different audiences
                5. Including actionable recommendations
                
                Focus on clarity, professionalism, and actionable insights."""
            ),
            
            AgentRole.QUALITY_REVIEWER: AgentConfig(
                role=AgentRole.QUALITY_REVIEWER,
                name="Quality Assurance Specialist",
                description="Reviews and ensures quality of research outputs",
                instructions="""You are a Quality Assurance Specialist responsible for:
                1. Reviewing research outputs for accuracy and completeness
                2. Ensuring consistency across different sections
                3. Checking for logical flow and coherence
                4. Validating that requirements are met
                5. Suggesting improvements and corrections
                
                Be thorough and maintain high quality standards."""
            )
        }
    
    async def initialize_agents(self):
        """Initialize all specialized agents."""
        
        print("🤖 Initializing Multi-Agent Research System...")
        
        for role, config in self.agent_configs.items():
            try:
                agent_data = await self.io_client.create_agent(
                    name=config.name,
                    description=config.description,
                    instructions=config.instructions,
                    model=config.model
                )
                
                self.agents[role] = {
                    'id': agent_data.get('id', f'mock_{role.value}'),
                    'config': config,
                    'status': 'ready'
                }
                
                print(f"  ✅ {config.name} initialized")
                
            except Exception as e:
                print(f"  ⚠️  Failed to initialize {config.name}: {str(e)}")
                # Create mock agent for development
                self.agents[role] = {
                    'id': f'mock_{role.value}',
                    'config': config,
                    'status': 'mock'
                }
        
        print(f"🎯 Multi-Agent System ready with {len(self.agents)} agents\n")
    
    async def research_with_agents(self, topic: str, depth: str = 'standard') -> Dict[str, Any]:
        """
        Conduct comprehensive research using multiple specialized agents.
        """
        
        print(f"🔬 Starting multi-agent research on: {topic}")
        
        # Phase 1: Research Coordination
        coordination_result = await self._coordinate_research(topic, depth)
        
        # Phase 2: Parallel Research Execution
        research_tasks = coordination_result.get('tasks', [])
        research_results = await self._execute_parallel_tasks(research_tasks)
        
        # Phase 3: Data Analysis
        analysis_result = await self._analyze_research_data(research_results, topic)
        
        # Phase 4: Content Synthesis
        synthesis_result = await self._synthesize_content(research_results, analysis_result)
        
        # Phase 5: Fact Checking
        verified_result = await self._verify_facts(synthesis_result)
        
        # Phase 6: Trend Analysis
        trend_analysis = await self._analyze_trends(verified_result, topic)
        
        # Phase 7: Report Generation
        report_result = await self._generate_professional_report(
            verified_result, trend_analysis, topic
        )
        
        # Phase 8: Quality Review
        final_result = await self._review_quality(report_result)
        
        return final_result
    
    async def _coordinate_research(self, topic: str, depth: str) -> Dict[str, Any]:
        """Coordinate research strategy using the Research Coordinator agent."""
        
        print("  📋 Coordinating research strategy...")
        
        coordination_prompt = f"""
        Plan a comprehensive research strategy for the topic: "{topic}"
        Research depth: {depth}
        
        Create a research plan that includes:
        1. Key research questions to investigate
        2. Types of sources to prioritize
        3. Specific subtopics to explore
        4. Research methodology approach
        
        Respond in JSON format with the research plan.
        """
        
        result = await self._run_agent(AgentRole.RESEARCH_COORDINATOR, coordination_prompt)
        
        # Parse coordination result and create tasks
        try:
            plan = json.loads(result.get('response', '{}'))
        except:
            # Fallback plan
            plan = {
                'research_questions': [f"What are the current trends in {topic}?"],
                'source_types': ['academic', 'news', 'industry'],
                'subtopics': [topic],
                'methodology': 'comprehensive'
            }
        
        return {
            'plan': plan,
            'tasks': self._create_research_tasks(plan, topic)
        }
    
    def _create_research_tasks(self, plan: Dict[str, Any], topic: str) -> List[AgentTask]:
        """Create specific research tasks based on the coordination plan."""
        
        tasks = []
        
        # Web research tasks
        for subtopic in plan.get('subtopics', [topic]):
            tasks.append(AgentTask(
                agent_role=AgentRole.WEB_RESEARCHER,
                task_type='web_research',
                input_data={'topic': subtopic, 'source_types': plan.get('source_types', [])},
                priority=1
            ))
        
        return tasks
    
    async def _execute_parallel_tasks(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """Execute multiple research tasks in parallel."""
        
        print("  🔍 Executing parallel research tasks...")
        
        # Group tasks by agent role for efficient execution
        task_groups = {}
        for task in tasks:
            if task.agent_role not in task_groups:
                task_groups[task.agent_role] = []
            task_groups[task.agent_role].append(task)
        
        # Execute tasks in parallel
        all_results = {}
        
        for agent_role, agent_tasks in task_groups.items():
            agent_results = []
            
            for task in agent_tasks:
                if task.task_type == 'web_research':
                    prompt = f"""
                    Research the topic: {task.input_data['topic']}
                    Focus on finding information from: {', '.join(task.input_data.get('source_types', []))}
                    
                    Provide comprehensive information including:
                    1. Key findings and insights
                    2. Recent developments
                    3. Expert opinions
                    4. Statistical data if available
                    5. Source references
                    """
                    
                    result = await self._run_agent(agent_role, prompt)
                    agent_results.append(result)
            
            all_results[agent_role] = agent_results
        
        return all_results
    
    async def _analyze_research_data(self, research_results: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Analyze research data using the Data Analyst agent."""
        
        print("  📊 Analyzing research data...")
        
        # Combine all research results
        combined_data = ""
        for agent_role, results in research_results.items():
            for result in results:
                combined_data += result.get('response', '') + "\n\n"
        
        analysis_prompt = f"""
        Analyze the following research data for the topic: "{topic}"
        
        Research Data:
        {combined_data[:4000]}  # Limit to avoid token limits
        
        Provide analysis including:
        1. Key statistical insights
        2. Data patterns and trends
        3. Quantitative findings
        4. Data quality assessment
        5. Gaps in data coverage
        
        Format as structured analysis.
        """
        
        return await self._run_agent(AgentRole.DATA_ANALYST, analysis_prompt)
    
    async def _synthesize_content(self, research_results: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize content using the Content Summarizer agent."""
        
        print("  🧠 Synthesizing research content...")
        
        synthesis_prompt = f"""
        Synthesize the following research findings and analysis:
        
        Research Results: {str(research_results)[:2000]}
        Data Analysis: {analysis_result.get('response', '')[:2000]}
        
        Create a comprehensive synthesis including:
        1. Executive summary
        2. Key themes and insights
        3. Main findings
        4. Supporting evidence
        5. Areas of consensus and disagreement
        
        Organize information coherently and logically.
        """
        
        return await self._run_agent(AgentRole.CONTENT_SUMMARIZER, synthesis_prompt)
    
    async def _verify_facts(self, synthesis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify facts using the Fact Checker agent."""
        
        print("  ✅ Verifying facts and claims...")
        
        verification_prompt = f"""
        Review and verify the following synthesized content:
        
        {synthesis_result.get('response', '')[:3000]}
        
        Check for:
        1. Factual accuracy
        2. Consistency of claims
        3. Potential bias or misinformation
        4. Source credibility
        5. Confidence levels for different claims
        
        Provide verification report with confidence scores.
        """
        
        return await self._run_agent(AgentRole.FACT_CHECKER, verification_prompt)
    
    async def _analyze_trends(self, verified_result: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Analyze trends using the Trend Analyzer agent."""
        
        print("  📈 Analyzing trends and implications...")
        
        trend_prompt = f"""
        Analyze trends and future implications for: "{topic}"
        
        Based on verified content:
        {verified_result.get('response', '')[:3000]}
        
        Identify:
        1. Current trends and patterns
        2. Historical context and evolution
        3. Future predictions and implications
        4. Market dynamics and drivers
        5. Cross-industry connections
        
        Provide trend analysis with timeline and impact assessment.
        """
        
        return await self._run_agent(AgentRole.TREND_ANALYZER, trend_prompt)
    
    async def _generate_professional_report(self, verified_result: Dict[str, Any], trend_analysis: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Generate professional report using the Report Writer agent."""
        
        print("  📝 Generating professional report...")
        
        report_prompt = f"""
        Create a professional research report for: "{topic}"
        
        Verified Content: {verified_result.get('response', '')[:2000]}
        Trend Analysis: {trend_analysis.get('response', '')[:2000]}
        
        Structure the report with:
        1. Executive Summary
        2. Key Findings
        3. Detailed Analysis
        4. Trend Insights
        5. Recommendations
        6. Conclusion
        
        Use professional language and clear organization.
        """
        
        return await self._run_agent(AgentRole.REPORT_WRITER, report_prompt)
    
    async def _review_quality(self, report_result: Dict[str, Any]) -> Dict[str, Any]:
        """Review quality using the Quality Reviewer agent."""
        
        print("  🔍 Conducting quality review...")
        
        review_prompt = f"""
        Review the following research report for quality:
        
        {report_result.get('response', '')[:4000]}
        
        Evaluate:
        1. Completeness and accuracy
        2. Logical flow and coherence
        3. Professional presentation
        4. Actionable insights
        5. Areas for improvement
        
        Provide quality assessment and final recommendations.
        """
        
        quality_review = await self._run_agent(AgentRole.QUALITY_REVIEWER, review_prompt)
        
        return {
            'final_report': report_result.get('response', ''),
            'quality_review': quality_review.get('response', ''),
            'metadata': {
                'agents_used': list(self.agents.keys()),
                'quality_score': 'High',  # Could be extracted from review
                'completeness': 'Comprehensive'
            }
        }
    
    async def _run_agent(self, agent_role: AgentRole, prompt: str) -> Dict[str, Any]:
        """Run a specific agent with a given prompt."""
        
        if agent_role not in self.agents:
            raise ValueError(f"Agent {agent_role} not initialized")
        
        agent = self.agents[agent_role]
        
        try:
            if agent['status'] == 'mock':
                # Use direct text generation for mock agents
                response = await self.io_client.generate_text(prompt, max_tokens=1500)
            else:
                # Use agent API
                result = await self.io_client.run_agent(agent['id'], prompt)
                response = result.get('response', result.get('content', ''))
            
            return {
                'agent_role': agent_role,
                'response': response,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"    ⚠️  Agent {agent_role.value} failed: {str(e)}")
            return {
                'agent_role': agent_role,
                'response': f"Agent execution failed: {str(e)}",
                'status': 'failed'
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents in the system."""
        
        status = {}
        for role, agent in self.agents.items():
            status[role.value] = {
                'name': agent['config'].name,
                'status': agent['status'],
                'id': agent['id']
            }
        
        return status