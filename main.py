#!/usr/bin/env python3
"""
AI Research & Content Assistant Agent
Built for Launch IO Hackathon 2025

A powerful autonomous agent that performs research, content analysis,
and report generation using IO Intelligence APIs.
"""

import asyncio
import click
import os
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

from agent.core import ResearchAgent
from config.settings import Settings

console = Console()

@click.command()
@click.option('--topic', '-t', required=True, help='Research topic or query')
@click.option('--format', '-f', default='markdown', 
              type=click.Choice(['markdown', 'json', 'txt']),
              help='Output format')
@click.option('--depth', '-d', default='standard',
              type=click.Choice(['quick', 'standard', 'detailed']),
              help='Research depth')
@click.option('--mode', '-m', default='standard',
              type=click.Choice(['standard', 'multi-agent']),
              help='Research mode: standard or multi-agent')
@click.option('--output', '-o', help='Output file path')
@click.option('--sources', '-s', type=int, help='Maximum number of sources')
@click.option('--stream', is_flag=True, help='Enable streaming output')
def research(topic, format, depth, mode, output, sources, stream):
    """Launch IO Research Agent - Autonomous research and content generation."""
    
    # Display different headers based on mode
    if mode == 'multi-agent':
        console.print(Panel.fit(
            "[bold blue]🤖 Multi-Agent Research System[/bold blue]\n"
            "[dim]Powered by IO Intelligence Specialized Agents[/dim]",
            border_style="blue"
        ))
    else:
        console.print(Panel.fit(
            "[bold blue]🚀 Launch IO Research Agent[/bold blue]\n"
            "[dim]Powered by IO Intelligence[/dim]",
            border_style="blue"
        ))
    
    # Load settings
    settings = Settings()
    if not settings.io_api_key:
        console.print("[red]❌ Error: IO_API_KEY not found in environment variables[/red]")
        console.print("[yellow]💡 Copy .env.example to .env and add your API key[/yellow]")
        return
    
    # Override settings with CLI options
    if sources:
        settings.max_sources = sources
    
    # Run research with agent initialization
    asyncio.run(run_research_with_agent(settings, topic, format, depth, mode, output, stream))

async def run_research_with_agent(settings, topic, format, depth, mode, output, stream):
    """Initialize agent with fallback and run research."""
    
    # Try to initialize with real API first
    try:
        agent = ResearchAgent(settings)
        # Test API connectivity
        if hasattr(agent.io_client, 'health_check'):
            is_healthy = await agent.io_client.health_check()
            if not is_healthy:
                raise Exception("API health check failed")
    except Exception as e:
        console.print(f"[yellow]⚠️  Real API not available: {str(e)}[/yellow]")
        console.print("[blue]🔧 Switching to Mock API for demonstration[/blue]\n")
        
        # Switch to mock API
        settings.use_mock_api = True
        agent = ResearchAgent(settings)
    
    # Run the research based on mode
    if mode == 'multi-agent':
        await run_multi_agent_research(agent, topic, format, depth, output, stream)
    else:
        await run_research(agent, topic, format, depth, output, stream)

async def run_research(agent, topic, format, depth, output, stream):
    """Execute the research process."""
    
    console.print(f"[green]🔍 Starting research on:[/green] [bold]{topic}[/bold]")
    console.print(f"[dim]Format: {format} | Depth: {depth}[/dim]\n")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            # Phase 1: Research
            task1 = progress.add_task("🔍 Researching sources...", total=None)
            sources = await agent.research_topic(topic, depth)
            progress.update(task1, description="✅ Research completed")
            
            # Phase 2: Analysis
            task2 = progress.add_task("🧠 Analyzing content...", total=None)
            analysis = await agent.analyze_content(sources)
            progress.update(task2, description="✅ Analysis completed")
            
            # Phase 3: Report Generation
            task3 = progress.add_task("📝 Generating report...", total=None)
            report = await agent.generate_report(analysis, format)
            progress.update(task3, description="✅ Report generated")
        
        # Display results
        console.print("\n" + "="*60)
        console.print("[bold green]📊 Research Report Generated[/bold green]")
        console.print("="*60 + "\n")
        
        if format == 'markdown':
            console.print(Markdown(report))
        else:
            console.print(report)
        
        # Save to file if specified
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
            console.print(f"\n[green]💾 Report saved to:[/green] {output}")
        
        console.print(f"\n[dim]📈 Processed {len(sources)} sources[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during research:[/red] {str(e)}")
        console.print("[yellow]💡 Check your API key and internet connection[/yellow]")

async def run_multi_agent_research(agent, topic, format, depth, output, stream):
    """Execute multi-agent research process."""
    
    console.print(f"[green]🤖 Starting multi-agent research on:[/green] [bold]{topic}[/bold]")
    console.print(f"[dim]Format: {format} | Depth: {depth} | Mode: Multi-Agent[/dim]\n")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            # Phase 1: Multi-Agent Research
            task1 = progress.add_task("🤖 Initializing specialized agents...", total=None)
            research_result = await agent.research_with_multi_agents(topic, depth)
            progress.update(task1, description="✅ Multi-agent research completed")
            
            # Phase 2: Report Formatting
            task2 = progress.add_task("📝 Formatting final report...", total=None)
            
            # Extract the final report from multi-agent result
            final_report = research_result.get('final_report', '')
            quality_review = research_result.get('quality_review', '')
            metadata = research_result.get('metadata', {})
            
            # Format report based on requested format
            if format == 'json':
                import json
                formatted_report = json.dumps({
                    'topic': topic,
                    'research_mode': 'multi-agent',
                    'final_report': final_report,
                    'quality_review': quality_review,
                    'metadata': metadata,
                    'agents_used': metadata.get('agents_used', [])
                }, indent=2)
            elif format == 'txt':
                formatted_report = f"""MULTI-AGENT RESEARCH REPORT
Topic: {topic}
Research Mode: Multi-Agent System
Generated: {metadata.get('generated_at', 'N/A')}

{final_report}

QUALITY REVIEW:
{quality_review}

AGENTS USED: {', '.join(str(agent) for agent in metadata.get('agents_used', []))}
"""
            else:  # markdown
                formatted_report = f"""# Multi-Agent Research Report: {topic}

*Generated using specialized AI agents powered by IO Intelligence*

## Executive Summary & Findings

{final_report}

## Quality Assurance Review

{quality_review}

## Research Methodology

This report was generated using a multi-agent research system with the following specialized agents:

{chr(10).join(f'- **{str(agent).replace("AgentRole.", "").replace("_", " ").title()}**' for agent in metadata.get('agents_used', []))}

### Multi-Agent Process:
1. **Research Coordination** - Strategic planning and task distribution
2. **Parallel Research Execution** - Multiple agents working simultaneously
3. **Data Analysis** - Statistical and quantitative analysis
4. **Content Synthesis** - Information integration and summarization
5. **Fact Verification** - Accuracy and credibility checking
6. **Trend Analysis** - Pattern identification and future implications
7. **Professional Report Writing** - Structured presentation
8. **Quality Review** - Final validation and improvement suggestions

*Powered by IO Intelligence Multi-Agent System*
"""
            
            progress.update(task2, description="✅ Report formatting completed")
        
        # Display results
        console.print("\n" + "="*70)
        console.print("[bold green]🤖 Multi-Agent Research Report Generated[/bold green]")
        console.print("="*70 + "\n")
        
        if format == 'markdown':
            console.print(Markdown(formatted_report))
        else:
            console.print(formatted_report)
        
        # Save to file if specified
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(formatted_report, encoding='utf-8')
            console.print(f"\n[green]💾 Multi-agent report saved to:[/green] {output}")
        
        # Display agent statistics
        agent_status = await agent.get_agent_status()
        if agent_status:
            console.print(f"\n[dim]🤖 Utilized {len(agent_status)} specialized agents[/dim]")
            for role, status in agent_status.items():
                console.print(f"[dim]  • {status['name']}: {status['status']}[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during multi-agent research:[/red] {str(e)}")
        console.print("[yellow]💡 Check your API key and multi-agent system configuration[/yellow]")

@click.command()
def agents():
    """Show available agents and their capabilities."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Multi-Agent Research System[/bold blue]\n"
        "[dim]Specialized AI Agents Overview[/dim]",
        border_style="blue"
    ))
    
    # Load settings and initialize agent system
    try:
        settings = Settings()
        agent = ResearchAgent(settings)
        
        console.print("\n[bold green]Available Specialized Agents:[/bold green]\n")
        
        agent_descriptions = {
            'Research Coordinator': '📋 Orchestrates research strategy and coordinates between agents',
            'Web Research Specialist': '🔍 Finds and extracts information from web sources',
            'Data Analysis Expert': '📊 Analyzes statistical data and quantitative information',
            'Content Synthesis Specialist': '🧠 Synthesizes and summarizes complex information',
            'Fact Verification Specialist': '✅ Verifies facts, claims, and information accuracy',
            'Trend Analysis Expert': '📈 Identifies trends, patterns, and future implications',
            'Professional Report Writer': '📝 Creates professional, well-structured reports',
            'Quality Assurance Specialist': '🔍 Reviews and ensures quality of research outputs'
        }
        
        for name, description in agent_descriptions.items():
            console.print(f"[bold cyan]{name}[/bold cyan]")
            console.print(f"  {description}\n")
        
        console.print("[yellow]💡 Use --mode multi-agent to leverage all these specialized agents![/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Error loading agent system:[/red] {str(e)}")

@click.command()
@click.option('--topic', '-t', required=True, help='Research topic for comparison')
@click.option('--format', '-f', default='markdown', 
              type=click.Choice(['markdown', 'json', 'txt']),
              help='Output format')
def compare(topic, format):
    """Compare standard vs multi-agent research results."""
    
    console.print(Panel.fit(
        "[bold blue]⚖️  Research Mode Comparison[/bold blue]\n"
        "[dim]Standard vs Multi-Agent Research[/dim]",
        border_style="blue"
    ))
    
    console.print(f"[green]🔬 Comparing research approaches for:[/green] [bold]{topic}[/bold]\n")
    
    # Run both research modes
    asyncio.run(run_comparison(topic, format))

async def run_comparison(topic, format):
    """Run both standard and multi-agent research for comparison."""
    
    settings = Settings()
    
    try:
        # Initialize agent
        agent = ResearchAgent(settings)
        
        console.print("[blue]📊 Running Standard Research...[/blue]")
        
        # Standard research
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task1 = progress.add_task("🔍 Standard research in progress...", total=None)
            
            sources = await agent.research_topic(topic, 'standard')
            analysis = await agent.analyze_content(sources)
            standard_report = await agent.generate_report(analysis, format)
            
            progress.update(task1, description="✅ Standard research completed")
        
        console.print("[blue]🤖 Running Multi-Agent Research...[/blue]")
        
        # Multi-agent research
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task2 = progress.add_task("🤖 Multi-agent research in progress...", total=None)
            
            multi_agent_result = await agent.research_with_multi_agents(topic, 'standard')
            
            progress.update(task2, description="✅ Multi-agent research completed")
        
        # Display comparison
        console.print("\n" + "="*80)
        console.print("[bold green]📊 Research Comparison Results[/bold green]")
        console.print("="*80 + "\n")
        
        console.print("[bold blue]📋 STANDARD RESEARCH RESULTS:[/bold blue]")
        console.print("-" * 50)
        if format == 'markdown':
            console.print(Markdown(standard_report[:1000] + "..." if len(standard_report) > 1000 else standard_report))
        else:
            console.print(standard_report[:1000] + "..." if len(standard_report) > 1000 else standard_report)
        
        console.print(f"\n[bold blue]🤖 MULTI-AGENT RESEARCH RESULTS:[/bold blue]")
        console.print("-" * 50)
        multi_agent_report = multi_agent_result.get('final_report', 'No report generated')
        if format == 'markdown':
            console.print(Markdown(multi_agent_report[:1000] + "..." if len(multi_agent_report) > 1000 else multi_agent_report))
        else:
            console.print(multi_agent_report[:1000] + "..." if len(multi_agent_report) > 1000 else multi_agent_report)
        
        # Save comparison report
        comparison_report = f"""# Research Mode Comparison: {topic}

## Standard Research Results
{standard_report}

## Multi-Agent Research Results
{multi_agent_result.get('final_report', 'No report generated')}

## Quality Review (Multi-Agent Only)
{multi_agent_result.get('quality_review', 'No quality review available')}

## Comparison Summary
- **Standard Mode**: Single-agent approach with basic research and analysis
- **Multi-Agent Mode**: Specialized agents working collaboratively with quality assurance
- **Agents Used**: {', '.join(str(agent) for agent in multi_agent_result.get('metadata', {}).get('agents_used', []))}
"""
        
        # Save comparison
        output_path = Path(f"comparison_{topic.replace(' ', '_')}.{format}")
        output_path.write_text(comparison_report, encoding='utf-8')
        console.print(f"\n[green]💾 Comparison report saved to:[/green] {output_path}")
        
    except Exception as e:
        console.print(f"[red]❌ Error during comparison:[/red] {str(e)}")

@click.command()
@click.argument('topics_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='reports', help='Output directory')
@click.option('--format', '-f', default='markdown', 
              type=click.Choice(['markdown', 'json', 'txt']))
def batch(topics_file, output_dir, format):
    """Process multiple topics from a file."""
    
    console.print("[blue]📋 Batch Processing Mode[/blue]\n")
    
    # Read topics
    topics = Path(topics_file).read_text().strip().split('\n')
    topics = [t.strip() for t in topics if t.strip()]
    
    console.print(f"[green]Found {len(topics)} topics to process[/green]\n")
    
    # Process each topic
    settings = Settings()
    agent = ResearchAgent(settings)
    
    asyncio.run(process_batch(agent, topics, output_dir, format))

async def process_batch(agent, topics, output_dir, format):
    """Process multiple topics in batch."""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for i, topic in enumerate(topics, 1):
        console.print(f"[blue]Processing {i}/{len(topics)}:[/blue] {topic}")
        
        try:
            sources = await agent.research_topic(topic, 'standard')
            analysis = await agent.analyze_content(sources)
            report = await agent.generate_report(analysis, format)
            
            # Save report
            filename = f"{topic.replace(' ', '_').replace('/', '_')}.{format}"
            file_path = output_path / filename
            file_path.write_text(report, encoding='utf-8')
            
            console.print(f"[green]✅ Saved:[/green] {filename}\n")
            
        except Exception as e:
            console.print(f"[red]❌ Failed:[/red] {str(e)}\n")

# CLI Group
@click.group()
def cli():
    """Launch IO Research Agent - AI-powered research and content generation."""
    pass

cli.add_command(research)
cli.add_command(batch)
cli.add_command(agents)
cli.add_command(compare)

# Make research the default command when no subcommand is provided
@cli.result_callback()
def process_result(result):
    pass

if __name__ == '__main__':
    import sys
    
    # If no command is provided, default to 'research'
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1].startswith('--')):
        sys.argv.insert(1, 'research')
    
    cli()