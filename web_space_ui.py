#!/usr/bin/env python3
"""
Launch IO Hackathon - Space-Themed AI Research System
Enhanced UI with navbar, footer, and space-inspired design
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from real_data_demo import IOIntelligenceResearcher

app = FastAPI(title="🚀 Launch IO Hackathon - Space Research Station", version="3.0.0")

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
user_stats = {"total_research": 0, "total_reports": 0, "time_saved": 0}

# Load/Save functions
def load_search_history():
    global search_history, user_stats
    try:
        if Path("search_history.json").exists():
            with open("search_history.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    search_history = data.get("history", [])
                    user_stats = data.get("stats", {"total_research": 0, "total_reports": 0, "time_saved": 0})
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

class ResearchRequest(BaseModel):
    topic: str
    mode: str = "io_intelligence"
    priority: str = "normal"

class ReportRequest(BaseModel):
    task_ids: List[str]
    report_title: str = "Research Report"
    report_type: str = "comprehensive"
@app.g
et("/", response_class=HTMLResponse)
async def homepage():
    return HTMLResponse(open("space_ui.html", "r").read())

@app.post("/api/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    research_tasks[task_id] = {
        "id": task_id, "topic": request.topic, "mode": request.mode, "status": "starting",
        "progress": 0, "current_phase": "Initializing", "message": "Starting mission...", 
        "created_at": datetime.now().isoformat(), "result": None
    }
    background_tasks.add_task(execute_research, task_id, request)
    return {"task_id": task_id, "status": "started"}

@app.get("/api/research/{task_id}")
async def get_status(task_id: str):
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task = research_tasks[task_id]
    return {"task_id": task_id, "status": task["status"], "progress": task["progress"], 
            "current_phase": task["current_phase"], "message": task.get("message", ""), 
            "topic": task["topic"], "mode": task["mode"]}

@app.get("/api/research/{task_id}/result")
async def get_result(task_id: str):
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task = research_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    return task["result"]

@app.get("/api/history")
async def get_history():
    return {"history": search_history, "stats": user_stats}

@app.delete("/api/history")
async def clear_history():
    global search_history, user_stats
    search_history = []
    user_stats = {"total_research": 0, "total_reports": 0, "time_saved": 0}
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
        "id": report_id, "topic": request.report_title, "mode": "report_generation", "status": "starting",
        "progress": 0, "current_phase": "Collecting data", "message": "Gathering mission data...", 
        "created_at": datetime.now().isoformat(), "result": None
    }
    background_tasks.add_task(execute_report_generation, report_id, request)
    return {"task_id": report_id, "status": "started"}

async def execute_research(task_id: str, request: ResearchRequest):
    try:
        research_tasks[task_id]["status"] = "running"
        research_tasks[task_id]["progress"] = 20
        research_tasks[task_id]["message"] = f"Researching: {request.topic}"
        
        if request.mode == "io_intelligence":
            research_tasks[task_id]["progress"] = 50
            result = await io_researcher.research_topic(request.topic)
            final_result = {"task_id": task_id, "topic": request.topic, "mode": request.mode, 
                          "status": "completed", "report": result, "created_at": research_tasks[task_id]["created_at"], 
                          "completed_at": datetime.now().isoformat()}
        elif request.mode == "multi_topic":
            research_tasks[task_id]["progress"] = 30
            topics = [f"{request.topic} trends", f"{request.topic} applications", f"{request.topic} challenges"]
            research_results = []
            for topic in topics:
                result = await io_researcher.research_topic(topic)
                research_results.append(result)
            report = await io_researcher.generate_report(research_results)
            final_result = {"task_id": task_id, "topic": request.topic, "mode": request.mode, "status": "completed",
                          "report": {"research_results": research_results, "comprehensive_report": report},
                          "created_at": research_tasks[task_id]["created_at"], "completed_at": datetime.now().isoformat()}
        elif request.mode == "sentiment":
            research_tasks[task_id]["progress"] = 50
            result = await io_researcher.analyze_sentiment(request.topic)
            final_result = {"task_id": task_id, "topic": request.topic, "mode": request.mode, 
                          "status": "completed", "report": result, "created_at": research_tasks[task_id]["created_at"], 
                          "completed_at": datetime.now().isoformat()}
        
        research_tasks[task_id]["status"] = "completed"
        research_tasks[task_id]["progress"] = 100
        research_tasks[task_id]["current_phase"] = "Completed"
        research_tasks[task_id]["message"] = "Mission completed!"
        research_tasks[task_id]["result"] = final_result
        
        # Add to history
        global search_history, user_stats
        history_item = {"task_id": task_id, "topic": request.topic, "mode": request.mode, "status": "completed",
                       "created_at": research_tasks[task_id]["created_at"], "completed_at": datetime.now().isoformat(),
                       "summary": str(final_result["report"])[:200] + "..." if len(str(final_result["report"])) > 200 else str(final_result["report"])}
        search_history.insert(0, history_item)
        if len(search_history) > 50:
            search_history = search_history[:50]
        user_stats["total_research"] += 1
        user_stats["time_saved"] += 2
        save_search_history()
        
    except Exception as e:
        research_tasks[task_id]["status"] = "failed"
        research_tasks[task_id]["message"] = f"Mission failed: {str(e)}"

async def execute_report_generation(report_id: str, request: ReportRequest):
    try:
        research_tasks[report_id]["status"] = "running"
        research_tasks[report_id]["progress"] = 50
        
        collected_data = []
        for task_id in request.task_ids:
            if task_id in research_tasks and research_tasks[task_id]["status"] == "completed":
                collected_data.append(research_tasks[task_id]["result"])
        
        # Generate simple report
        report_content = f"🚀 {request.report_title}\n\n📊 Generated from {len(collected_data)} research missions:\n\n"
        for item in collected_data:
            report_content += f"🎯 {item['topic']}: {str(item['report'])[:100]}...\n\n"
        
        final_result = {"task_id": report_id, "topic": request.report_title, "mode": "report_generation", 
                       "status": "completed", "report": report_content, "created_at": research_tasks[report_id]["created_at"], 
                       "completed_at": datetime.now().isoformat()}
        
        research_tasks[report_id]["status"] = "completed"
        research_tasks[report_id]["progress"] = 100
        research_tasks[report_id]["current_phase"] = "Completed"
        research_tasks[report_id]["message"] = "Report generated!"
        research_tasks[report_id]["result"] = final_result
        
        # Add to history
        global search_history, user_stats
        history_item = {"task_id": report_id, "topic": request.report_title, "mode": "report_generation", "status": "completed",
                       "created_at": research_tasks[report_id]["created_at"], "completed_at": datetime.now().isoformat(),
                       "summary": f"Generated {request.report_type} report from {len(collected_data)} missions"}
        search_history.insert(0, history_item)
        user_stats["total_reports"] += 1
        save_search_history()
        
    except Exception as e:
        research_tasks[report_id]["status"] = "failed"
        research_tasks[report_id]["message"] = f"Report generation failed: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Space Research Station...")
    print("🌌 Open your browser to: http://localhost:5000")
    print("✨ Space-themed UI with advanced features!")
    uvicorn.run(app, host="127.0.0.1", port=5000)