#!/usr/bin/env python3
"""
Complete Unified Launch IO Application
Combines Multi-Agent System + Web Interface + IO Intelligence
All features accessible from one application
"""

import asyncio
import json
import uuid
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import all components
from real_data_demo import IOIntelligenceResearcher

# Add iointel to path for multi-agent functionality
sys.path.append('./iointel')
try:
    from iointel import Agent, Workflow
    MULTI_AGENT_AVAILABLE = True
except ImportError:
    MULTI_AGENT_AVAILABLE = False
    print("⚠️ Multi-agent system not available - continuing with IO Intelligence only")

app = FastAPI(title="🚀 Launch IO - Complete Unified Platform", version="6.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
research_tasks: Dict[str, Dict] = {}
search_history: List[Dict] = []
io_researcher = IOIntelligenceResearcher()
user_stats = {"total_research": 0, "total_reports": 0, "time_saved": 0, "success_rate": 100}

# Multi-agent system setup
class MultiAgentSystem:
    def __init__(self):
        self.agents = {}
        self.setup_agents()
    
    def setup_agents(self):
        if not MULTI_AGENT_AVAILABLE:
            return
            
        agent_configs = [
            {
                "name": "Research_Coordinator",
                "instructions": "You are a research coordinator who orchestrates comprehensive research strategies and coordinates between different research approaches.",
                "specialty": "Research Coordination"
            },
            {
                "name": "Web_Research_Specialist", 
                "instructions": "You are a web research specialist who finds and extracts information from various online sources with high accuracy.",
                "specialty": "Web Research"
            },
            {
                "name": "Data_Analysis_Expert",
                "instructions": "You are a data analysis expert who analyzes statistical data, trends, and quantitative information.",
                "specialty": "Data Analysis"
            },
            {
                "name": "Content_Synthesizer",
                "instructions": "You are a content synthesizer who combines information from multiple sources into coherent, comprehensive summaries.",
                "specialty": "Content Synthesis"
            },
            {
                "name": "Fact_Verification_Specialist",
                "instructions": "You are a fact verification specialist who checks the accuracy and reliability of information and claims.",
                "specialty": "Fact Verification"
            },
            {
                "name": "Trend_Analysis_Expert",
                "instructions": "You are a trend analysis expert who identifies patterns, emerging trends, and future implications.",
                "specialty": "Trend Analysis"
            },
            {
                "name": "Report_Writer",
                "instructions": "You are a professional report writer who creates well-structured, comprehensive reports from research data.",
                "specialty": "Report Writing"
            },
            {
                "name": "Quality_Assurance_Reviewer",
                "instructions": "You are a quality assurance reviewer who ensures research quality, completeness, and accuracy.",
                "specialty": "Quality Assurance"
            }
        ]
        
        api_key = os.environ.get("IO_API_KEY", "")
        if not api_key:
            print("⚠️ No IO_API_KEY found - multi-agent system disabled")
            return
            
        for config in agent_configs:
            try:
                agent = Agent(
                    name=config["name"],
                    instructions=config["instructions"],
                    model="meta-llama/Llama-3.3-70B-Instruct",
                    api_key=api_key,
                    base_url="https://api.intelligence.io.solutions/api/v1"
                )
                self.agents[config["name"]] = {
                    "agent": agent,
                    "specialty": config["specialty"]
                }
                print(f"✅ Created agent: {config['name']}")
            except Exception as e:
                print(f"❌ Failed to create agent {config['name']}: {e}")
    
    async def run_multi_agent_research(self, topic: str) -> Dict[str, Any]:
        if not self.agents:
            return {"error": "Multi-agent system not available"}
            
        results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "agent_results": {},
            "summary": {}
        }
        
        # Run research with each agent
        for agent_name, agent_info in self.agents.items():
            try:
                specialized_prompt = f"Research and analyze: {topic}. Focus on {agent_info['specialty'].lower()} aspects."
                
                workflow = Workflow(objective=specialized_prompt, client_mode=False)
                agent_results = await workflow.summarize_text(max_words=200, agents=[agent_info["agent"]]).run_tasks()
                
                if "results" in agent_results and "summarize_text" in agent_results["results"]:
                    summary_result = agent_results["results"]["summarize_text"]
                    
                    results["agent_results"][agent_name] = {
                        "specialty": agent_info["specialty"],
                        "summary": summary_result.summary if hasattr(summary_result, 'summary') else str(summary_result),
                        "key_points": summary_result.key_points if hasattr(summary_result, 'key_points') else [],
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                results["agent_results"][agent_name] = {
                    "specialty": agent_info["specialty"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Generate summary
        successful_agents = [name for name, result in results["agent_results"].items() if "error" not in result]
        results["summary"] = {
            "total_agents": len(self.agents),
            "successful_agents": len(successful_agents),
            "overall_assessment": f"Multi-agent analysis completed with {len(successful_agents)} agents providing insights on '{topic}'."
        }
        
        return results

multi_agent_system = MultiAgentSystem()

# Load/Save functions
def load_search_history():
    global search_history, user_stats
    try:
        if Path("search_history.json").exists():
            with open("search_history.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    search_history = data.get("history", [])
                    user_stats = data.get("stats", {"total_research": 0, "total_reports": 0, "time_saved": 0, "success_rate": 100})
                else:
                    search_history = data if isinstance(data, list) else []
    except:
        search_history = []

def save_search_history():
    try:
        with open("search_history.json", "w") as f:
            json.dump({"history": search_history, "stats": user_stats}, f, indent=2)
    except:
        pass

load_search_history()

# Pydantic models
class ResearchRequest(BaseModel):
    topic: str
    mode: str = "io_intelligence"  # io_intelligence, multi_agent, multi_topic, sentiment
    priority: str = "normal"
    depth: str = "standard"

class ReportRequest(BaseModel):
    task_ids: List[str]
    report_title: str = "Research Report"
    report_type: str = "comprehensive"

# API Routes
@app.post("/api/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    research_tasks[task_id] = {
        "id": task_id,
        "topic": request.topic,
        "mode": request.mode,
        "priority": request.priority,
        "depth": request.depth,
        "status": "starting",
        "progress": 0,
        "current_phase": "Initializing",
        "message": "Starting research mission...",
        "created_at": datetime.now().isoformat(),
        "result": None
    }
    
    background_tasks.add_task(execute_research, task_id, request)
    return {"task_id": task_id, "status": "started"}

@app.get("/api/research/{task_id}")
async def get_research_status(task_id: str):
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = research_tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "current_phase": task["current_phase"],
        "message": task.get("message", ""),
        "topic": task["topic"],
        "mode": task["mode"],
        "priority": task.get("priority", "normal"),
        "depth": task.get("depth", "standard")
    }

@app.get("/api/research/{task_id}/result")
async def get_research_result(task_id: str):
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = research_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    return task["result"]

@app.get("/api/history")
async def get_search_history():
    return {"history": search_history, "stats": user_stats}

@app.delete("/api/history")
async def clear_search_history():
    global search_history, user_stats
    search_history = []
    user_stats = {"total_research": 0, "total_reports": 0, "time_saved": 0, "success_rate": 100}
    save_search_history()
    return {"message": "History cleared"}

@app.delete("/api/history/{task_id}")
async def delete_history_item(task_id: str):
    global search_history
    search_history = [item for item in search_history if item.get("task_id") != task_id]
    save_search_history()
    return {"message": "Item deleted"}

@app.post("/api/generate-report")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    report_id = str(uuid.uuid4())
    research_tasks[report_id] = {
        "id": report_id,
        "topic": request.report_title,
        "mode": "report_generation",
        "status": "starting",
        "progress": 0,
        "current_phase": "Collecting data",
        "message": "Gathering research data...",
        "created_at": datetime.now().isoformat(),
        "result": None
    }
    
    background_tasks.add_task(execute_report_generation, report_id, request)
    return {"task_id": report_id, "status": "started"}

# Background task functions
async def execute_research(task_id: str, request: ResearchRequest):
    try:
        research_tasks[task_id]["status"] = "running"
        research_tasks[task_id]["progress"] = 20
        research_tasks[task_id]["current_phase"] = "Analyzing request"
        research_tasks[task_id]["message"] = f"Researching: {request.topic}"
        
        if request.mode == "io_intelligence":
            research_tasks[task_id]["current_phase"] = "IO Intelligence Research"
            research_tasks[task_id]["progress"] = 50
            result = await io_researcher.research_topic(request.topic)
            
            final_result = {
                "task_id": task_id,
                "topic": request.topic,
                "mode": request.mode,
                "status": "completed",
                "report": result,
                "created_at": research_tasks[task_id]["created_at"],
                "completed_at": datetime.now().isoformat()
            }
            
        elif request.mode == "multi_agent":
            research_tasks[task_id]["current_phase"] = "Multi-Agent Analysis"
            research_tasks[task_id]["progress"] = 30
            result = await multi_agent_system.run_multi_agent_research(request.topic)
            
            final_result = {
                "task_id": task_id,
                "topic": request.topic,
                "mode": request.mode,
                "status": "completed",
                "report": result,
                "created_at": research_tasks[task_id]["created_at"],
                "completed_at": datetime.now().isoformat()
            }
            
        elif request.mode == "multi_topic":
            research_tasks[task_id]["current_phase"] = "Multi-Topic Analysis"
            research_tasks[task_id]["progress"] = 30
            topics = [f"{request.topic} trends", f"{request.topic} applications", f"{request.topic} challenges"]
            research_results = []
            
            for i, topic in enumerate(topics):
                research_tasks[task_id]["progress"] = 30 + (i * 20)
                research_tasks[task_id]["message"] = f"Analyzing: {topic}"
                result = await io_researcher.research_topic(topic)
                research_results.append(result)
            
            # Generate comprehensive report
            research_tasks[task_id]["current_phase"] = "Generating comprehensive report"
            research_tasks[task_id]["progress"] = 90
            report = await io_researcher.generate_report(research_results)
            
            final_result = {
                "task_id": task_id,
                "topic": request.topic,
                "mode": request.mode,
                "status": "completed",
                "report": {
                    "research_results": research_results,
                    "comprehensive_report": report
                },
                "created_at": research_tasks[task_id]["created_at"],
                "completed_at": datetime.now().isoformat()
            }
            
        elif request.mode == "sentiment":
            research_tasks[task_id]["current_phase"] = "Sentiment Analysis"
            research_tasks[task_id]["progress"] = 50
            result = await io_researcher.analyze_sentiment(request.topic)
            
            final_result = {
                "task_id": task_id,
                "topic": request.topic,
                "mode": request.mode,
                "status": "completed",
                "report": result,
                "created_at": research_tasks[task_id]["created_at"],
                "completed_at": datetime.now().isoformat()
            }
        
        research_tasks[task_id]["status"] = "completed"
        research_tasks[task_id]["progress"] = 100
        research_tasks[task_id]["current_phase"] = "Completed"
        research_tasks[task_id]["message"] = "Research mission completed!"
        research_tasks[task_id]["result"] = final_result
        
        # Add to history
        global search_history, user_stats
        history_item = {
            "task_id": task_id,
            "topic": request.topic,
            "mode": request.mode,
            "priority": request.priority,
            "depth": request.depth,
            "status": "completed",
            "created_at": research_tasks[task_id]["created_at"],
            "completed_at": datetime.now().isoformat(),
            "summary": str(final_result["report"])[:200] + "..." if len(str(final_result["report"])) > 200 else str(final_result["report"])
        }
        
        search_history.insert(0, history_item)
        if len(search_history) > 100:  # Keep last 100 items
            search_history = search_history[:100]
        
        user_stats["total_research"] += 1
        user_stats["time_saved"] += 2 if request.depth == "quick" else 4 if request.depth == "standard" else 8
        save_search_history()
        
    except Exception as e:
        research_tasks[task_id]["status"] = "failed"
        research_tasks[task_id]["message"] = f"Research failed: {str(e)}"
        print(f"Research failed for {task_id}: {e}")

async def execute_report_generation(report_id: str, request: ReportRequest):
    try:
        research_tasks[report_id]["status"] = "running"
        research_tasks[report_id]["progress"] = 25
        research_tasks[report_id]["current_phase"] = "Collecting research data"
        
        collected_data = []
        for task_id in request.task_ids:
            if task_id in research_tasks and research_tasks[task_id]["status"] == "completed":
                collected_data.append(research_tasks[task_id]["result"])
        
        research_tasks[report_id]["progress"] = 50
        research_tasks[report_id]["current_phase"] = "Analyzing collected data"
        
        # Generate comprehensive report
        report_content = f"# {request.report_title}\n\n"
        report_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_content += f"**Report Type:** {request.report_type.title()}\n"
        report_content += f"**Data Sources:** {len(collected_data)} research missions\n\n"
        
        research_tasks[report_id]["progress"] = 75
        research_tasks[report_id]["current_phase"] = "Generating report sections"
        
        for i, item in enumerate(collected_data, 1):
            report_content += f"## Mission {i}: {item['topic']}\n"
            report_content += f"**Mode:** {item['mode']}\n"
            report_content += f"**Completed:** {item.get('completed_at', 'Unknown')}\n\n"
            
            if isinstance(item['report'], dict):
                if 'research_results' in item['report']:
                    report_content += "### Research Results:\n"
                    for j, result in enumerate(item['report']['research_results'], 1):
                        report_content += f"{j}. {str(result)[:300]}...\n\n"
                elif 'agent_results' in item['report']:
                    report_content += "### Agent Analysis:\n"
                    for agent_name, result in item['report']['agent_results'].items():
                        if 'error' not in result:
                            report_content += f"**{agent_name}:** {result.get('summary', '')[:200]}...\n\n"
                else:
                    report_content += f"{str(item['report'])[:500]}...\n\n"
            else:
                report_content += f"{str(item['report'])[:500]}...\n\n"
            
            report_content += "---\n\n"
        
        research_tasks[report_id]["progress"] = 90
        research_tasks[report_id]["current_phase"] = "Finalizing report"
        
        final_result = {
            "task_id": report_id,
            "topic": request.report_title,
            "mode": "report_generation",
            "status": "completed",
            "report": report_content,
            "data_sources": len(collected_data),
            "created_at": research_tasks[report_id]["created_at"],
            "completed_at": datetime.now().isoformat()
        }
        
        research_tasks[report_id]["status"] = "completed"
        research_tasks[report_id]["progress"] = 100
        research_tasks[report_id]["current_phase"] = "Report completed"
        research_tasks[report_id]["message"] = "Report generated successfully!"
        research_tasks[report_id]["result"] = final_result
        
        # Add to history
        global search_history, user_stats
        history_item = {
            "task_id": report_id,
            "topic": request.report_title,
            "mode": "report_generation",
            "status": "completed",
            "created_at": research_tasks[report_id]["created_at"],
            "completed_at": datetime.now().isoformat(),
            "summary": f"Generated {request.report_type} report from {len(collected_data)} research missions"
        }
        
        search_history.insert(0, history_item)
        user_stats["total_reports"] += 1
        save_search_history()
        
    except Exception as e:
        research_tasks[report_id]["status"] = "failed"
        research_tasks[report_id]["message"] = f"Report generation failed: {str(e)}"
        print(f"Report generation failed for {report_id}: {e}")

# Main HTML interface
@app.get("/", response_class=HTMLResponse)
async def unified_interface():
    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Launch IO - Complete Unified Platform</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
            min-height: 100vh; color: #ffffff; overflow-x: hidden;
        }}
        
        /* Navigation */
        .navbar {{ position: fixed; top: 0; width: 100%; background: rgba(0, 0, 0, 0.95); backdrop-filter: blur(15px); 
                  border-bottom: 1px solid rgba(255, 255, 255, 0.1); z-index: 1000; padding: 1rem 0; }}
        .nav-container {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; 
                         align-items: center; padding: 0 2rem; }}
        .logo {{ display: flex; align-items: center; font-size: 1.5rem; font-weight: bold; color: #00d4ff; }}
        .logo i {{ margin-right: 0.5rem; animation: spin 10s linear infinite; }}
        @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
        
        .nav-links {{ display: flex; list-style: none; gap: 1rem; }}
        .nav-links a {{ color: #ffffff; text-decoration: none; padding: 0.7rem 1.2rem; border-radius: 25px; 
                       transition: all 0.3s ease; display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }}
        .nav-links a:hover, .nav-links a.active {{ background: linear-gradient(45deg, #00d4ff, #ff6b6b); 
                                                transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 212, 255, 0.3); }}
        
        /* Main content */
        .main-content {{ margin-top: 100px; padding: 2rem; position: relative; z-index: 10; }}
        .page-header {{ text-align: center; margin-bottom: 3rem; padding: 2rem 0; }}
        .page-title {{ font-size: 3rem; font-weight: bold; background: linear-gradient(45deg, #00d4ff, #ff6b6b, #4ecdc4, #45b7d1);
                      background-size: 400% 400%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                      animation: gradientShift 4s ease-in-out infinite; margin-bottom: 1rem; }}
        @keyframes gradientShift {{ 0%, 100% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} }}
        .page-subtitle {{ font-size: 1.2rem; color: #b0b0b0; margin-bottom: 2rem; }}
        
        /* Panels */
        .panel {{ background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); 
                 border-radius: 20px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); transition: transform 0.3s ease; 
                 margin-bottom: 2rem; }}
        .panel:hover {{ transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0, 212, 255, 0.2); }}
        .panel-header {{ display: flex; align-items: center; margin-bottom: 1.5rem; }}
        .panel-header i {{ font-size: 1.5rem; margin-right: 0.5rem; color: #00d4ff; }}
        .panel-title {{ font-size: 1.3rem; font-weight: 600; }}
        
        /* Grid layouts */
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; max-width: 1400px; margin: 0 auto; }}
        .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1400px; margin: 0 auto; }}
        @media (max-width: 768px) {{ .grid-2, .grid-3 {{ grid-template-columns: 1fr; }} .nav-links {{ display: none; }} }}
        
        /* Form elements */
        .form-group {{ margin-bottom: 1.5rem; }}
        .form-label {{ display: block; margin-bottom: 0.5rem; font-weight: 600; color: #e0e0e0; }}
        .form-input, .form-select {{ width: 100%; padding: 1rem; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); 
                                   border-radius: 10px; color: #ffffff; font-size: 1rem; transition: all 0.3s ease; }}
        .form-input:focus, .form-select:focus {{ outline: none; border-color: #00d4ff; box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
                                              background: rgba(255, 255, 255, 0.15); }}
        .form-input::placeholder {{ color: #b0b0b0; }}
        
        /* Buttons */
        .btn {{ background: linear-gradient(45deg, #00d4ff, #0099cc); color: white; border: none; padding: 1rem 2rem; 
               border-radius: 25px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; 
               margin: 0.5rem 0; text-decoration: none; display: inline-block; text-align: center; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4); }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
        .btn-full {{ width: 100%; }}
        .btn-danger {{ background: linear-gradient(45deg, #ff6b6b, #ee5a52); }}
        .btn-success {{ background: linear-gradient(45deg, #4ecdc4, #44a08d); }}
        
        /* Stats cards */
        .stats-container {{ display: flex; justify-content: center; gap: 2rem; margin-bottom: 3rem; flex-wrap: wrap; }}
        .stat-card {{ background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); 
                     border-radius: 15px; padding: 1.5rem; text-align: center; min-width: 150px; transition: transform 0.3s ease; }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2); }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #00d4ff; }}
        .stat-label {{ color: #b0b0b0; font-size: 0.9rem; }}
        
        /* Feature cards */
        .feature-card {{ background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); 
                        border-radius: 15px; padding: 2rem; text-align: center; transition: transform 0.3s ease; }}
        .feature-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2); }}
        .feature-icon {{ font-size: 3rem; color: #00d4ff; margin-bottom: 1rem; }}
        .feature-title {{ font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem; color: #ffffff; }}
        .feature-description {{ color: #b0b0b0; line-height: 1.6; }}
        
        /* Demo topics */
        .demo-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
        .demo-topic {{ background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; 
                      padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease; }}
        .demo-topic:hover {{ background: rgba(0, 212, 255, 0.2); transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3); }}
        
        /* Progress */
        .progress-container {{ background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); 
                             border-radius: 20px; padding: 2rem; margin: 2rem auto; max-width: 800px; display: none; }}
        .progress-bar {{ width: 100%; height: 25px; background: rgba(255, 255, 255, 0.1); border-radius: 15px; overflow: hidden; margin: 1.5rem 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #00d4ff, #4ecdc4, #ff6b6b); background-size: 200% 100%; 
                        width: 0%; transition: width 0.5s ease; animation: progressShine 2s linear infinite; border-radius: 15px; }}
        @keyframes progressShine {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
        
        /* Results */
        .results-container {{ background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); 
                            border-radius: 20px; padding: 2rem; margin: 2rem auto; max-width: 1200px; display: none; }}
        .result-item {{ background: rgba(255, 255, 255, 0.1); border-left: 4px solid #00d4ff; border-radius: 10px; 
                      padding: 1.5rem; margin: 1.5rem 0; transition: transform 0.3s ease; }}
        .result-item:hover {{ transform: translateX(5px); background: rgba(0, 212, 255, 0.1); }}
        .result-title {{ font-size: 1.3rem; font-weight: 600; color: #00d4ff; margin-bottom: 1rem; }}
        .result-summary {{ color: #e0e0e0; line-height: 1.6; margin-bottom: 1rem; }}
        
        /* Tabs */
        .tabs {{ display: flex; border-bottom: 2px solid rgba(255, 255, 255, 0.2); margin-bottom: 1.5rem; }}
        .tab {{ padding: 1rem 1.5rem; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.3s ease; color: #b0b0b0; }}
        .tab.active {{ border-bottom-color: #00d4ff; color: #00d4ff; font-weight: 600; }}
        .tab:hover {{ color: #ffffff; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        /* History items */
        .history-item {{ background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; 
                       border-left: 4px solid #00d4ff; transition: all 0.3s ease; }}
        .history-item:hover {{ background: rgba(0, 212, 255, 0.1); transform: translateX(5px); }}
        .history-actions {{ margin-top: 1rem; display: flex; gap: 0.5rem; }}
        .history-actions button {{ padding: 0.5rem 1rem; border: none; border-radius: 20px; cursor: pointer; font-size: 0.8rem; 
                                 transition: all 0.3s ease; }}
        
        /* Checkbox groups */
        .checkbox-group {{ display: flex; align-items: center; margin: 1rem 0; padding: 0.5rem; border-radius: 10px; 
                          transition: background 0.3s ease; }}
        .checkbox-group:hover {{ background: rgba(255, 255, 255, 0.05); }}
        .checkbox-group input[type="checkbox"] {{ width: auto; margin-right: 1rem; transform: scale(1.2); }}
        
        /* Page content */
        .page-content {{ display: none; }}
        .page-content.active {{ display: block; }}
        
        /* API Status */
        .api-status {{ background: linear-gradient(45deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1)); 
                      border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 10px; padding: 1rem; 
                      margin-bottom: 1.5rem; display: flex; align-items: center; }}
        .api-status i {{ color: #4caf50; margin-right: 0.5rem; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        
        /* Agent status */
        .agent-item {{ background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0; 
                      border-left: 3px solid #00d4ff; }}
        .status-ready {{ color: #4caf50; font-weight: 600; }}
        .status-working {{ color: #ff9800; font-weight: 600; }}
        .status-completed {{ color: #2196f3; font-weight: 600; }}
        
        /* Notification */
        .notification {{ position: fixed; top: 100px; right: 20px; background: rgba(0, 212, 255, 0.9); color: white; 
                        padding: 1rem 1.5rem; border-radius: 10px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); 
                        transform: translateX(400px); transition: transform 0.3s ease; z-index: 1001; }}
        .notification.show {{ transform: translateX(0); }}
        
        /* Loading spinner */
        .loading-spinner {{ display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(255, 255, 255, 0.3); 
                           border-radius: 50%; border-top-color: #00d4ff; animation: spin 1s ease-in-out infinite; }}
        
        /* Footer */
        .footer {{ background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(10px); border-top: 1px solid rgba(255, 255, 255, 0.1); 
                  padding: 2rem 0 1rem; margin-top: 5rem; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">
                <i class="fas fa-rocket"></i>
                Launch IO Complete Platform
            </div>
            <ul class="nav-links">
                <li><a onclick="showPage('home')" class="active"><i class="fas fa-home"></i> Home</a></li>
                <li><a onclick="showPage('research')"><i class="fas fa-search"></i> Research</a></li>
                <li><a onclick="showPage('history')"><i class="fas fa-history"></i> History</a></li>
                <li><a onclick="showPage('reports')"><i class="fas fa-chart-line"></i> Reports</a></li>
                <li><a onclick="showPage('about')"><i class="fas fa-info-circle"></i> About</a></li>
            </ul>
        </div>
    </nav>
    
    <!-- Main content -->
    <div class="main-content">
        <!-- Home Page -->
        <div id="page-home" class="page-content active">
            <div class="page-header">
                <h1 class="page-title">🚀 COMPLETE UNIFIED PLATFORM</h1>
                <p class="page-subtitle">Multi-Agent System + IO Intelligence + Web Interface • All-in-One Solution</p>
                
                <!-- Stats -->
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-number" id="totalResearch">{user_stats["total_research"]}</div>
                        <div class="stat-label">Research Missions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="totalReports">{user_stats["total_reports"]}</div>
                        <div class="stat-label">Reports Generated</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="timeSaved">{user_stats["time_saved"]}</div>
                        <div class="stat-label">Hours Saved</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">8</div>
                        <div class="stat-label">AI Agents</div>
                    </div>
                </div>
            </div>
            
            <!-- Features Grid -->
            <div class="grid-3">
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-brain"></i></div>
                    <div class="feature-title">IO Intelligence Research</div>
                    <div class="feature-description">
                        Powered by Llama-3.3-70B-Instruct for deep research analysis and comprehensive insights.
                    </div>
                    <button onclick="showPage('research')" class="btn btn-full" style="margin-top: 1rem;">Start Research</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-users"></i></div>
                    <div class="feature-title">Multi-Agent System</div>
                    <div class="feature-description">
                        8 specialized AI agents: Research Coordinator, Web Researcher, Data Analyst, Content Synthesizer, and more.
                    </div>
                    <button onclick="showPage('research')" class="btn btn-full" style="margin-top: 1rem;">Launch Agents</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-history"></i></div>
                    <div class="feature-title">Mission Archive</div>
                    <div class="feature-description">
                        Complete history of all research missions with ability to rerun, analyze, and export results.
                    </div>
                    <button onclick="showPage('history')" class="btn btn-full" style="margin-top: 1rem;">View History</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="feature-title">Advanced Reports</div>
                    <div class="feature-description">
                        Generate comprehensive reports from multiple research missions with advanced analytics.
                    </div>
                    <button onclick="showPage('reports')" class="btn btn-full" style="margin-top: 1rem;">Generate Reports</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-layer-group"></i></div>
                    <div class="feature-title">Multi-Topic Analysis</div>
                    <div class="feature-description">
                        Analyze multiple aspects of a topic simultaneously for comprehensive understanding.
                    </div>
                    <button onclick="showPage('research')" class="btn btn-full" style="margin-top: 1rem;">Try Multi-Topic</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-heart"></i></div>
                    <div class="feature-title">Sentiment Analysis</div>
                    <div class="feature-description">
                        Analyze public sentiment and opinions on any topic with advanced AI sentiment detection.
                    </div>
                    <button onclick="showPage('research')" class="btn btn-full" style="margin-top: 1rem;">Analyze Sentiment</button>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="panel">
                <div class="panel-header">
                    <i class="fas fa-zap"></i>
                    <h2 class="panel-title">Quick Launch Missions</h2>
                </div>
                
                <div class="demo-grid">
                    <div class="demo-topic" onclick="quickResearch('artificial intelligence trends 2025', 'io_intelligence')">
                        🤖 AI Evolution 2025
                    </div>
                    <div class="demo-topic" onclick="quickResearch('quantum computing breakthroughs', 'multi_agent')">
                        ⚛️ Quantum Computing (Multi-Agent)
                    </div>
                    <div class="demo-topic" onclick="quickResearch('space exploration technologies', 'multi_topic')">
                        🚀 Space Tech (Multi-Topic)
                    </div>
                    <div class="demo-topic" onclick="quickResearch('blockchain in metaverse', 'sentiment')">
                        🌐 Metaverse Sentiment
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Research Page -->
        <div id="page-research" class="page-content">
            <div class="page-header">
                <h1 class="page-title">🔬 RESEARCH LABORATORY</h1>
                <p class="page-subtitle">Complete Research Suite with All Available Methods</p>
            </div>
            
            <div class="grid-2">
                <!-- Research Control Panel -->
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-satellite"></i>
                        <h2 class="panel-title">Mission Control Center</h2>
                    </div>
                    
                    <div class="api-status">
                        <i class="fas fa-satellite-dish"></i>
                        <strong>All Systems Online</strong> - IO Intelligence + Multi-Agent Ready
                    </div>
                    
                    <form id="researchForm">
                        <div class="form-group">
                            <label class="form-label">🎯 Research Target</label>
                            <input type="text" id="topic" class="form-input" placeholder="Enter your research mission..." required>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">🛸 Research Mode</label>
                            <select id="mode" class="form-select">
                                <option value="io_intelligence">🤖 IO Intelligence Research</option>
                                <option value="multi_agent">👥 Multi-Agent System (8 Agents)</option>
                                <option value="multi_topic">🌌 Multi-Topic Analysis</option>
                                <option value="sentiment">💫 Sentiment Analysis</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">⚡ Mission Priority</label>
                            <select id="priority" class="form-select">
                                <option value="normal">🟢 Standard Priority</option>
                                <option value="high">🟡 High Priority</option>
                                <option value="urgent">🔴 Emergency Protocol</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">🔍 Research Depth</label>
                            <select id="depth" class="form-select">
                                <option value="quick">⚡ Quick Scan (2 hours saved)</option>
                                <option value="standard">📊 Standard Analysis (4 hours saved)</option>
                                <option value="detailed">🔬 Deep Research (8 hours saved)</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn btn-full" id="startBtn">
                            <i class="fas fa-rocket"></i> Launch Research Mission
                        </button>
                    </form>
                    
                    <div class="demo-grid">
                        <div class="demo-topic" onclick="setTopic('artificial intelligence trends 2025')">
                            🤖 AI Trends 2025
                        </div>
                        <div class="demo-topic" onclick="setTopic('quantum computing applications')">
                            ⚛️ Quantum Apps
                        </div>
                        <div class="demo-topic" onclick="setTopic('blockchain technology future')">
                            ⛓️ Blockchain Future
                        </div>
                        <div class="demo-topic" onclick="setTopic('machine learning healthcare')">
                            🏥 ML Healthcare
                        </div>
                    </div>
                </div>
                
                <!-- Agent Status Panel -->
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-users"></i>
                        <h2 class="panel-title">Multi-Agent Status</h2>
                    </div>
                    
                    <div id="agentStatus">
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>🎯 Research Coordinator</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Orchestrates research strategy and coordinates between agents</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>🌐 Web Research Specialist</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Finds and extracts information from web sources</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>📊 Data Analysis Expert</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Analyzes statistical data and quantitative information</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>📝 Content Synthesizer</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Synthesizes and summarizes complex information</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>✅ Fact Verification Specialist</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Verifies facts, claims, and information accuracy</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>📈 Trend Analysis Expert</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Identifies trends, patterns, and future implications</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>📋 Report Writer</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Creates comprehensive, well-structured reports</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>🔍 Quality Assurance Reviewer</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Ensures research quality, completeness, and accuracy</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- History Page -->
        <div id="page-history" class="page-content">
            <div class="page-header">
                <h1 class="page-title">📚 MISSION ARCHIVE</h1>
                <p class="page-subtitle">Complete History of All Research Missions</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <i class="fas fa-history"></i>
                    <h2 class="panel-title">Research History</h2>
                    <button class="btn btn-danger" onclick="clearHistory()" style="margin-left: auto; width: auto; padding: 0.5rem 1rem;">
                        🗑️ Clear All
                    </button>
                </div>
                
                <div id="historyList">Loading history...</div>
            </div>
        </div>
        
        <!-- Reports Page -->
        <div id="page-reports" class="page-content">
            <div class="page-header">
                <h1 class="page-title">📊 REPORT GENERATOR</h1>
                <p class="page-subtitle">Generate Comprehensive Reports from Multiple Missions</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <i class="fas fa-chart-line"></i>
                    <h2 class="panel-title">Generate Report</h2>
                </div>
                
                <div class="form-group">
                    <label class="form-label">📋 Report Title</label>
                    <input type="text" id="reportTitle" class="form-input" value="Research Report">
                </div>
                
                <div class="form-group">
                    <label class="form-label">📊 Report Type</label>
                    <select id="reportType" class="form-select">
                        <option value="comprehensive">📋 Comprehensive Report</option>
                        <option value="summary">📝 Executive Summary</option>
                        <option value="comparison">⚖️ Comparative Analysis</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">🎯 Select Research Missions</label>
                    <div id="taskSelection">No completed missions available</div>
                </div>
                
                <button class="btn btn-success btn-full" onclick="generateReport()" id="generateBtn" disabled>
                    📊 Generate Report
                </button>
            </div>
        </div>
        
        <!-- About Page -->
        <div id="page-about" class="page-content">
            <div class="page-header">
                <h1 class="page-title">ℹ️ ABOUT PLATFORM</h1>
                <p class="page-subtitle">Complete Unified Research Solution</p>
            </div>
            
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-info-circle"></i>
                        <h2 class="panel-title">Platform Features</h2>
                    </div>
                    
                    <ul style="color: #e0e0e0; line-height: 2;">
                        <li>🤖 <strong>IO Intelligence Research:</strong> Powered by Llama-3.3-70B-Instruct</li>
                        <li>👥 <strong>Multi-Agent System:</strong> 8 specialized AI agents working together</li>
                        <li>🌌 <strong>Multi-Topic Analysis:</strong> Comprehensive topic exploration</li>
                        <li>💫 <strong>Sentiment Analysis:</strong> Public opinion and sentiment detection</li>
                        <li>📚 <strong>Mission Archive:</strong> Complete research history</li>
                        <li>📊 <strong>Advanced Reports:</strong> Multi-mission report generation</li>
                        <li>⚡ <strong>Real-time Processing:</strong> Live progress tracking</li>
                        <li>🔍 <strong>Quality Assurance:</strong> Built-in fact verification</li>
                    </ul>
                </div>
                
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-users"></i>
                        <h2 class="panel-title">Multi-Agent Specialists</h2>
                    </div>
                    
                    <ul style="color: #e0e0e0; line-height: 2;">
                        <li>🎯 <strong>Research Coordinator:</strong> Strategy orchestration</li>
                        <li>🌐 <strong>Web Research Specialist:</strong> Information extraction</li>
                        <li>📊 <strong>Data Analysis Expert:</strong> Statistical analysis</li>
                        <li>📝 <strong>Content Synthesizer:</strong> Information synthesis</li>
                        <li>✅ <strong>Fact Verification:</strong> Accuracy checking</li>
                        <li>📈 <strong>Trend Analysis:</strong> Pattern identification</li>
                        <li>📋 <strong>Report Writer:</strong> Professional documentation</li>
                        <li>🔍 <strong>Quality Assurance:</strong> Final review and validation</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Progress Container -->
    <div class="progress-container" id="progressContainer">
        <div class="panel-header">
            <i class="fas fa-satellite"></i>
            <h2 class="panel-title">🔄 Research Mission in Progress</h2>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        <div id="statusMessage">Initializing research mission...</div>
        <div style="margin-top: 1rem; color: #b0b0b0;">
            <strong>Topic:</strong> <span id="currentTopic">-</span><br>
            <strong>Mode:</strong> <span id="currentMode">-</span><br>
            <strong>Priority:</strong> <span id="currentPriority">-</span>
        </div>
    </div>
    
    <!-- Results Container -->
    <div class="results-container" id="resultsContainer">
        <div class="panel-header">
            <i class="fas fa-check-circle"></i>
            <h2 class="panel-title">📊 Research Results</h2>
        </div>
        <div id="resultsContent"></div>
        <div style="margin-top: 2rem; text-align: center;">
            <button class="btn btn-success" onclick="addToReport()" id="addToReportBtn">
                📊 Add to Report Queue
            </button>
            <button class="btn" onclick="startNewResearch()">
                🚀 Start New Research
            </button>
        </div>
    </div>
    
    <!-- Notification -->
    <div class="notification" id="notification"></div>
    
    <!-- Footer -->
    <div class="footer">
        <p>&copy; 2025 Launch IO - Complete Unified Research Platform | Powered by IO Intelligence & Multi-Agent System</p>
    </div>
    
    <script>
        let currentTaskId = null;
        let searchHistory = [];
        let selectedTasks = new Set();
        let completedTasks = [];
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            loadSearchHistory();
            loadTaskSelection();
            updateStats();
        }});
        
        // Form submission
        document.getElementById('researchForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const topic = document.getElementById('topic').value;
            const mode = document.getElementById('mode').value;
            const priority = document.getElementById('priority').value;
            const depth = document.getElementById('depth').value;
            
            if (!topic.trim()) {{
                showNotification('Please enter a research topic', 'error');
                return;
            }}
            
            await startResearch(topic, mode, priority, depth);
        }});
        
        // Navigation
        function showPage(pageId) {{
            // Update navigation
            document.querySelectorAll('.nav-links a').forEach(link => link.classList.remove('active'));
            document.querySelector(`[onclick="showPage('${{pageId}}')"]`).classList.add('active');
            
            // Show page content
            document.querySelectorAll('.page-content').forEach(page => page.classList.remove('active'));
            document.getElementById(`page-${{pageId}}`).classList.add('active');
            
            // Load page-specific data
            if (pageId === 'history') loadSearchHistory();
            if (pageId === 'reports') loadTaskSelection();
        }}
        
        // Quick research
        function quickResearch(topic, mode = 'io_intelligence') {{
            document.getElementById('topic').value = topic;
            document.getElementById('mode').value = mode;
            showPage('research');
            showNotification(`Quick launch: ${{topic}} (${{mode}})`, 'info');
        }}
        
        // Set topic
        function setTopic(topic) {{
            document.getElementById('topic').value = topic;
        }}
        
        // Start research
        async function startResearch(topic, mode, priority = 'normal', depth = 'standard') {{
            const startBtn = document.getElementById('startBtn');
            const progressContainer = document.getElementById('progressContainer');
            const resultsContainer = document.getElementById('resultsContainer');
            
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Launching Mission...';
            progressContainer.style.display = 'block';
            resultsContainer.style.display = 'none';
            
            // Update progress info
            document.getElementById('currentTopic').textContent = topic;
            document.getElementById('currentMode').textContent = mode;
            document.getElementById('currentPriority').textContent = priority;
            
            try {{
                const response = await fetch('/api/research', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ topic, mode, priority, depth }})
                }});
                
                const data = await response.json();
                currentTaskId = data.task_id;
                
                showNotification(`Research mission launched: ${{topic}}`, 'success');
                pollProgress();
                
            }} catch (error) {{
                showNotification('Failed to start research mission', 'error');
                resetUI();
            }}
        }}
        
        // Poll progress
        async function pollProgress() {{
            if (!currentTaskId) return;
            
            try {{
                const response = await fetch(`/api/research/${{currentTaskId}}`);
                const data = await response.json();
                
                updateProgress(data);
                
                if (data.status === 'completed') {{
                    await showResults();
                    loadSearchHistory();
                    loadTaskSelection();
                    updateStats();
                }} else if (data.status === 'failed') {{
                    showNotification('Research mission failed', 'error');
                    resetUI();
                }} else {{
                    setTimeout(pollProgress, 1000);
                }}
                
            }} catch (error) {{
                setTimeout(pollProgress, 2000);
            }}
        }}
        
        // Update progress
        function updateProgress(data) {{
            document.getElementById('progressFill').style.width = data.progress + '%';
            document.getElementById('statusMessage').textContent = 
                `${{data.current_phase}}: ${{data.message || 'Processing...'}}`;
        }}
        
        // Show results
        async function showResults() {{
            try {{
                const response = await fetch(`/api/research/${{currentTaskId}}/result`);
                const data = await response.json();
                
                displayResults(data);
                showNotification('Research mission completed!', 'success');
                
            }} catch (error) {{
                showNotification('Failed to fetch results', 'error');
            }}
            
            resetUI();
        }}
        
        // Display results
        function displayResults(data) {{
            const resultsContainer = document.getElementById('resultsContainer');
            const resultsContent = document.getElementById('resultsContent');
            
            let html = `
                <div class="result-item">
                    <div class="result-title">🎯 ${{data.topic}}</div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Mode:</strong> ${{data.mode}} | 
                        <strong>Completed:</strong> ${{new Date(data.completed_at).toLocaleString()}}
                    </div>
            `;
            
            if (data.report && typeof data.report === 'object') {{
                if (data.report.agent_results) {{
                    html += '<h4>🤖 Multi-Agent Analysis:</h4>';
                    for (const [agentName, result] of Object.entries(data.report.agent_results)) {{
                        if (!result.error) {{
                            html += `
                                <div style="background: rgba(255,255,255,0.05); padding: 1rem; margin: 0.5rem 0; border-radius: 10px;">
                                    <strong>${{agentName.replace(/_/g, ' ')}}:</strong><br>
                                    <span style="color: #e0e0e0;">${{result.summary || 'No summary available'}}</span>
                                </div>
                            `;
                        }}
                    }}
                }} else if (data.report.research_results) {{
                    html += '<h4>🌌 Multi-Topic Results:</h4>';
                    data.report.research_results.forEach((result, i) => {{
                        html += `
                            <div style="background: rgba(255,255,255,0.05); padding: 1rem; margin: 0.5rem 0; border-radius: 10px;">
                                <strong>Topic ${{i + 1}}:</strong><br>
                                <span style="color: #e0e0e0;">${{String(result).substring(0, 300)}}...</span>
                            </div>
                        `;
                    }});
                }} else {{
                    html += `<div class="result-summary">${{String(data.report).substring(0, 1000)}}...</div>`;
                }}
            }} else {{
                html += `<div class="result-summary">${{String(data.report).substring(0, 1000)}}...</div>`;
            }}
            
            html += '</div>';
            
            resultsContent.innerHTML = html;
            resultsContainer.style.display = 'block';
            
            // Add to completed tasks
            completedTasks.push(data);
            document.getElementById('addToReportBtn').style.display = 'inline-block';
        }}
        
        // Reset UI
        function resetUI() {{
            const startBtn = document.getElementById('startBtn');
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-rocket"></i> Launch Research Mission';
            document.getElementById('progressContainer').style.display = 'none';
        }}
        
        // Load search history
        async function loadSearchHistory() {{
            try {{
                const response = await fetch('/api/history');
                const data = await response.json();
                
                searchHistory = data.history || [];
                displayHistory();
                
            }} catch (error) {{
                console.error('Failed to load history:', error);
            }}
        }}
        
        // Display history
        function displayHistory() {{
            const historyList = document.getElementById('historyList');
            
            if (searchHistory.length === 0) {{
                historyList.innerHTML = '<p style="color: #b0b0b0; text-align: center;">No research missions yet</p>';
                return;
            }}
            
            let html = '';
            searchHistory.forEach(item => {{
                html += `
                    <div class="history-item">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong>${{item.topic}}</strong>
                            <span style="color: #00d4ff;">${{item.mode}}</span>
                        </div>
                        <p style="color: #b0b0b0; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            ${{new Date(item.created_at).toLocaleString()}}
                            ${{item.priority ? ` | Priority: ${{item.priority}}` : ''}}
                            ${{item.depth ? ` | Depth: ${{item.depth}}` : ''}}
                        </p>
                        <p style="color: #e0e0e0; font-size: 0.9rem;">${{item.summary}}</p>
                        <div class="history-actions">
                            <button onclick="rerunResearch('${{item.task_id}}')" class="btn-success">🔄 Rerun</button>
                            <button onclick="deleteHistoryItem('${{item.task_id}}')" class="btn-danger">🗑️ Delete</button>
                        </div>
                    </div>
                `;
            }});
            
            historyList.innerHTML = html;
        }}
        
        // Clear history
        async function clearHistory() {{
            if (!confirm('Are you sure you want to clear all history?')) return;
            
            try {{
                await fetch('/api/history', {{ method: 'DELETE' }});
                searchHistory = [];
                displayHistory();
                updateStats();
                showNotification('History cleared', 'success');
            }} catch (error) {{
                showNotification('Failed to clear history', 'error');
            }}
        }}
        
        // Delete history item
        async function deleteHistoryItem(taskId) {{
            try {{
                await fetch(`/api/history/${{taskId}}`, {{ method: 'DELETE' }});
                loadSearchHistory();
                showNotification('Item deleted', 'success');
            }} catch (error) {{
                showNotification('Failed to delete item', 'error');
            }}
        }}
        
        // Rerun research
        function rerunResearch(taskId) {{
            const item = searchHistory.find(h => h.task_id === taskId);
            if (item) {{
                document.getElementById('topic').value = item.topic;
                document.getElementById('mode').value = item.mode;
                if (item.priority) document.getElementById('priority').value = item.priority;
                if (item.depth) document.getElementById('depth').value = item.depth;
                showPage('research');
                showNotification(`Rerunning: ${{item.topic}}`, 'info');
            }}
        }}
        
        // Load task selection
        function loadTaskSelection() {{
            const taskSelection = document.getElementById('taskSelection');
            const generateBtn = document.getElementById('generateBtn');
            
            if (searchHistory.length === 0) {{
                taskSelection.innerHTML = '<p style="color: #b0b0b0;">No completed missions available</p>';
                generateBtn.disabled = true;
                return;
            }}
            
            let html = '';
            searchHistory.forEach(item => {{
                html += `
                    <div class="checkbox-group">
                        <input type="checkbox" id="task_${{item.task_id}}" value="${{item.task_id}}" 
                               onchange="updateReportSelection()">
                        <label for="task_${{item.task_id}}" style="flex: 1;">
                            <strong>${{item.topic}}</strong> (${{item.mode}}) - ${{new Date(item.created_at).toLocaleDateString()}}
                        </label>
                    </div>
                `;
            }});
            
            taskSelection.innerHTML = html;
            updateReportSelection();
        }}
        
        // Update report selection
        function updateReportSelection() {{
            const checkboxes = document.querySelectorAll('#taskSelection input[type="checkbox"]:checked');
            const generateBtn = document.getElementById('generateBtn');
            
            selectedTasks.clear();
            checkboxes.forEach(cb => selectedTasks.add(cb.value));
            
            generateBtn.disabled = selectedTasks.size === 0;
            generateBtn.textContent = selectedTasks.size > 0 ? 
                `📊 Generate Report (${{selectedTasks.size}} missions)` : 
                '📊 Generate Report';
        }}
        
        // Generate report
        async function generateReport() {{
            if (selectedTasks.size === 0) {{
                showNotification('Please select at least one mission', 'error');
                return;
            }}
            
            const reportTitle = document.getElementById('reportTitle').value;
            const reportType = document.getElementById('reportType').value;
            const generateBtn = document.getElementById('generateBtn');
            
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            try {{
                const response = await fetch('/api/generate-report', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        task_ids: Array.from(selectedTasks),
                        report_title: reportTitle,
                        report_type: reportType
                    }})
                }});
                
                const data = await response.json();
                currentTaskId = data.task_id;
                
                showNotification('Report generation started', 'success');
                document.getElementById('progressContainer').style.display = 'block';
                pollProgress();
                
            }} catch (error) {{
                showNotification('Failed to generate report', 'error');
                generateBtn.disabled = false;
                generateBtn.textContent = '📊 Generate Report';
            }}
        }}
        
        // Add to report
        function addToReport() {{
            if (currentTaskId) {{
                selectedTasks.add(currentTaskId);
                showPage('reports');
                showNotification('Added to report queue', 'success');
            }}
        }}
        
        // Start new research
        function startNewResearch() {{
            document.getElementById('topic').value = '';
            document.getElementById('resultsContainer').style.display = 'none';
            showPage('research');
        }}
        
        // Update stats
        async function updateStats() {{
            try {{
                const response = await fetch('/api/history');
                const data = await response.json();
                
                if (data.stats) {{
                    document.getElementById('totalResearch').textContent = data.stats.total_research || 0;
                    document.getElementById('totalReports').textContent = data.stats.total_reports || 0;
                    document.getElementById('timeSaved').textContent = data.stats.time_saved || 0;
                }}
            }} catch (error) {{
                console.error('Failed to update stats:', error);
            }}
        }}
        
        // Show notification
        function showNotification(message, type = 'info') {{
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification show ${{type}}`;
            
            setTimeout(() => {{
                notification.classList.remove('show');
            }}, 3000);
        }}
        
        // Initialize stats on load
        updateStats();
    </script>
</body>
</html>
""")

if __name__ == "__main__":
    import uvicorn
    
    # Set up environment
    if not os.environ.get("IO_API_KEY"):
        os.environ["IO_API_KEY"] = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImNjOTcyYTVhLTM1MTAtNDFmMC05ODA3LWY2NDc4M2Y0YTFlZCIsImV4cCI6NDkwNjYyMDAyNn0.D3nqreeXTd-MZUjKNkNr6-oE8SYQGDMYQGUfN84G2rGbaWxFVA0GvbXEvYmfrHstdRlF-CQSpMO5Awpjiic-Kw"
    
    print("🚀 Launch IO - Complete Unified Platform")
    print("=" * 60)
    print("🌟 Features Available:")
    print("  • IO Intelligence Research (Llama-3.3-70B-Instruct)")
    if MULTI_AGENT_AVAILABLE:
        print("  • Multi-Agent System (8 Specialized Agents)")
    else:
        print("  • Multi-Agent System (Not Available - Install iointel)")
    print("  • Multi-Topic Analysis")
    print("  • Sentiment Analysis")
    print("  • Complete Mission Archive")
    print("  • Advanced Report Generation")
    print("  • Real-time Progress Tracking")
    print("  • Web Interface with All Features")
    print("=" * 60)
    print("🌐 Starting server at: http://localhost:8000")
    print("📱 Access all features from the web interface")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)