#!/usr/bin/env python3
"""
Launch IO Hackathon - Unified Research Platform
Complete application combining multi-agent system and web interface
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import all components
from real_data_demo import IOIntelligenceResearcher
from agent.core import ResearchAgent
from config.settings import Settings

app = FastAPI(title="🚀 Launch IO - Unified Research Platform", version="5.0.0")

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
multi_agent_system = ResearchAgent(Settings())
user_stats = {"total_research": 0, "total_reports": 0, "time_saved": 0, "success_rate": 100}

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
    mode: str = "io_intelligence"  # io_intelligence, multi_agent, sentiment
    priority: str = "normal"
    depth: str = "standard"

class ReportRequest(BaseModel):
    task_ids: List[str]
    report_title: str = "Research Report"
    report_type: str = "comprehensive"# Main
 HTML template with navigation
@app.get("/", response_class=HTMLResponse)
async def home_page():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Launch IO - Unified Research Platform</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
            min-height: 100vh; color: #ffffff; overflow-x: hidden;
        }
        
        /* Navigation */
        .navbar {
            position: fixed; top: 0; width: 100%; background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(15px); border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 1000; padding: 1rem 0;
        }
        .nav-container {
            max-width: 1400px; margin: 0 auto; display: flex;
            justify-content: space-between; align-items: center; padding: 0 2rem;
        }
        .logo {
            display: flex; align-items: center; font-size: 1.5rem;
            font-weight: bold; color: #00d4ff; text-decoration: none;
        }
        .logo i { margin-right: 0.5rem; animation: spin 10s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        .nav-links { display: flex; list-style: none; gap: 1rem; }
        .nav-links a {
            color: #ffffff; text-decoration: none; padding: 0.7rem 1.2rem;
            border-radius: 25px; transition: all 0.3s ease; display: flex;
            align-items: center; gap: 0.5rem;
        }
        .nav-links a:hover, .nav-links a.active {
            background: linear-gradient(45deg, #00d4ff, #ff6b6b);
            transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 212, 255, 0.3);
        }
        
        /* Main content */
        .main-content { margin-top: 100px; padding: 2rem; position: relative; z-index: 10; }
        .page-header { text-align: center; margin-bottom: 3rem; padding: 2rem 0; }
        .page-title {
            font-size: 3rem; font-weight: bold;
            background: linear-gradient(45deg, #00d4ff, #ff6b6b, #4ecdc4, #45b7d1);
            background-size: 400% 400%; -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; animation: gradientShift 4s ease-in-out infinite;
            margin-bottom: 1rem;
        }
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        .page-subtitle { font-size: 1.2rem; color: #b0b0b0; margin-bottom: 2rem; }
        
        /* Panels */
        .panel {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px;
            padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease; margin-bottom: 2rem;
        }
        .panel:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0, 212, 255, 0.2); }
        .panel-header { display: flex; align-items: center; margin-bottom: 1.5rem; }
        .panel-header i { font-size: 1.5rem; margin-right: 0.5rem; color: #00d4ff; }
        .panel-title { font-size: 1.3rem; font-weight: 600; }
        
        /* Grid layouts */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; max-width: 1400px; margin: 0 auto; }
        .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1400px; margin: 0 auto; }
        @media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } .nav-links { display: none; } }
        
        /* Form elements */
        .form-group { margin-bottom: 1.5rem; }
        .form-label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #e0e0e0; }
        .form-input, .form-select {
            width: 100%; padding: 1rem; background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 10px;
            color: #ffffff; font-size: 1rem; transition: all 0.3s ease;
        }
        .form-input:focus, .form-select:focus {
            outline: none; border-color: #00d4ff; box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            background: rgba(255, 255, 255, 0.15);
        }
        .form-input::placeholder { color: #b0b0b0; }
        
        /* Buttons */
        .btn {
            background: linear-gradient(45deg, #00d4ff, #0099cc); color: white; border: none;
            padding: 1rem 2rem; border-radius: 25px; font-size: 1rem; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease; margin: 0.5rem 0;
            text-decoration: none; display: inline-block; text-align: center;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .btn-full { width: 100%; }
        .btn-danger { background: linear-gradient(45deg, #ff6b6b, #ee5a52); }
        .btn-success { background: linear-gradient(45deg, #4ecdc4, #44a08d); }
        
        /* Stats cards */
        .stats-container { display: flex; justify-content: center; gap: 2rem; margin-bottom: 3rem; flex-wrap: wrap; }
        .stat-card {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px;
            padding: 1.5rem; text-align: center; min-width: 150px; transition: transform 0.3s ease;
        }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2); }
        .stat-number { font-size: 2rem; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #b0b0b0; font-size: 0.9rem; }
        
        /* Feature cards */
        .feature-card {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px;
            padding: 2rem; text-align: center; transition: transform 0.3s ease;
        }
        .feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2); }
        .feature-icon { font-size: 3rem; color: #00d4ff; margin-bottom: 1rem; }
        .feature-title { font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem; color: #ffffff; }
        .feature-description { color: #b0b0b0; line-height: 1.6; }
        
        /* Demo topics */
        .demo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
        .demo-topic {
            background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;
        }
        .demo-topic:hover {
            background: rgba(0, 212, 255, 0.2); transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
        }
        
        /* Progress */
        .progress-container {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px;
            padding: 2rem; margin: 2rem auto; max-width: 800px; display: none;
        }
        .progress-bar {
            width: 100%; height: 25px; background: rgba(255, 255, 255, 0.1);
            border-radius: 15px; overflow: hidden; margin: 1.5rem 0;
        }
        .progress-fill {
            height: 100%; background: linear-gradient(90deg, #00d4ff, #4ecdc4, #ff6b6b);
            background-size: 200% 100%; width: 0%; transition: width 0.5s ease;
            animation: progressShine 2s linear infinite; border-radius: 15px;
        }
        @keyframes progressShine { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
        
        /* Results */
        .results-container {
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px;
            padding: 2rem; margin: 2rem auto; max-width: 1200px; display: none;
        }
        .result-item {
            background: rgba(255, 255, 255, 0.1); border-left: 4px solid #00d4ff;
            border-radius: 10px; padding: 1.5rem; margin: 1.5rem 0; transition: transform 0.3s ease;
        }
        .result-item:hover { transform: translateX(5px); background: rgba(0, 212, 255, 0.1); }
        .result-title { font-size: 1.3rem; font-weight: 600; color: #00d4ff; margin-bottom: 1rem; }
        .result-summary { color: #e0e0e0; line-height: 1.6; margin-bottom: 1rem; }
        
        /* Tabs */
        .tabs { display: flex; border-bottom: 2px solid rgba(255, 255, 255, 0.2); margin-bottom: 1.5rem; }
        .tab {
            padding: 1rem 1.5rem; cursor: pointer; border-bottom: 2px solid transparent;
            transition: all 0.3s ease; color: #b0b0b0;
        }
        .tab.active { border-bottom-color: #00d4ff; color: #00d4ff; font-weight: 600; }
        .tab:hover { color: #ffffff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* History items */
        .history-item {
            background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 1.5rem;
            margin: 1rem 0; border-left: 4px solid #00d4ff; transition: all 0.3s ease;
        }
        .history-item:hover { background: rgba(0, 212, 255, 0.1); transform: translateX(5px); }
        .history-actions { margin-top: 1rem; display: flex; gap: 0.5rem; }
        .history-actions button {
            padding: 0.5rem 1rem; border: none; border-radius: 20px;
            cursor: pointer; font-size: 0.8rem; transition: all 0.3s ease;
        }
        
        /* Checkbox groups */
        .checkbox-group {
            display: flex; align-items: center; margin: 1rem 0; padding: 0.5rem;
            border-radius: 10px; transition: background 0.3s ease;
        }
        .checkbox-group:hover { background: rgba(255, 255, 255, 0.05); }
        .checkbox-group input[type="checkbox"] { width: auto; margin-right: 1rem; transform: scale(1.2); }
        
        /* Footer */
        .footer {
            background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 2rem 0 1rem;
            margin-top: 5rem; text-align: center; color: #666;
        }
        
        /* API Status */
        .api-status {
            background: linear-gradient(45deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1));
            border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 10px;
            padding: 1rem; margin-bottom: 1.5rem; display: flex; align-items: center;
        }
        .api-status i { color: #4caf50; margin-right: 0.5rem; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        /* Notification */
        .notification {
            position: fixed; top: 100px; right: 20px; background: rgba(0, 212, 255, 0.9);
            color: white; padding: 1rem 1.5rem; border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); transform: translateX(400px);
            transition: transform 0.3s ease; z-index: 1001;
        }
        .notification.show { transform: translateX(0); }
        
        /* Loading spinner */
        .loading-spinner {
            display: inline-block; width: 20px; height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3); border-radius: 50%;
            border-top-color: #00d4ff; animation: spin 1s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">
                <i class="fas fa-rocket"></i>
                Launch IO Research Platform
            </a>
            <ul class="nav-links">
                <li><a href="/" id="nav-home"><i class="fas fa-home"></i> Home</a></li>
                <li><a href="#research" id="nav-research"><i class="fas fa-search"></i> Research</a></li>
                <li><a href="#history" id="nav-history"><i class="fas fa-history"></i> History</a></li>
                <li><a href="#reports" id="nav-reports"><i class="fas fa-chart-line"></i> Reports</a></li>
                <li><a href="#analytics" id="nav-analytics"><i class="fas fa-analytics"></i> Analytics</a></li>
                <li><a href="#about" id="nav-about"><i class="fas fa-info-circle"></i> About</a></li>
            </ul>
        </div>
    </nav>
    
    <!-- Main content -->
    <div class="main-content">
        <!-- Home Page -->
        <div id="page-home" class="page-content active">
            <div class="page-header">
                <h1 class="page-title">🚀 UNIFIED RESEARCH PLATFORM</h1>
                <p class="page-subtitle">Multi-Agent System + IO Intelligence • Complete Research Solution</p>
                
                <!-- Stats -->
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-number" id="totalResearch">""" + str(user_stats["total_research"]) + """</div>
                        <div class="stat-label">Research Missions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="totalReports">""" + str(user_stats["total_reports"]) + """</div>
                        <div class="stat-label">Reports Generated</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="timeSaved">""" + str(user_stats["time_saved"]) + """</div>
                        <div class="stat-label">Hours Saved</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">∞</div>
                        <div class="stat-label">Possibilities</div>
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
                        8 specialized AI agents working together: Research Coordinator, Web Researcher, Data Analyst, and more.
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
                        Generate comprehensive reports from multiple research missions with advanced analytics and insights.
                    </div>
                    <button onclick="showPage('reports')" class="btn btn-full" style="margin-top: 1rem;">Generate Reports</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-analytics"></i></div>
                    <div class="feature-title">Performance Analytics</div>
                    <div class="feature-description">
                        Deep insights into research patterns, success rates, agent performance, and productivity metrics.
                    </div>
                    <button onclick="showPage('analytics')" class="btn btn-full" style="margin-top: 1rem;">View Analytics</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-satellite"></i></div>
                    <div class="feature-title">Real-Time Processing</div>
                    <div class="feature-description">
                        Live progress tracking with real-time updates, instant notifications, and seamless user experience.
                    </div>
                    <button onclick="showPage('research')" class="btn btn-full" style="margin-top: 1rem;">Try Now</button>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="panel">
                <div class="panel-header">
                    <i class="fas fa-zap"></i>
                    <h2 class="panel-title">Quick Launch Missions</h2>
                </div>
                
                <div class="demo-grid">
                    <div class="demo-topic" onclick="quickResearch('artificial intelligence trends 2025')">
                        🤖 AI Evolution 2025
                    </div>
                    <div class="demo-topic" onclick="quickResearch('quantum computing breakthroughs')">
                        ⚛️ Quantum Computing
                    </div>
                    <div class="demo-topic" onclick="quickResearch('space exploration technologies')">
                        🚀 Space Technologies
                    </div>
                    <div class="demo-topic" onclick="quickResearch('blockchain in metaverse')">
                        🌐 Metaverse Blockchain
                    </div>
                </div>
            </div>
        </div> 
       
        <!-- Research Page -->
        <div id="page-research" class="page-content">
            <div class="page-header">
                <h1 class="page-title">🔬 RESEARCH LABORATORY</h1>
                <p class="page-subtitle">Multi-Agent System + IO Intelligence Research</p>
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
                        <strong>IO Intelligence Online</strong> - Llama-3.3-70B-Instruct Ready
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
                                <option value="multi_topic">🌌 Multi-Dimensional Analysis</option>
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
                                <option value="quick">⚡ Quick Scan</option>
                                <option value="standard">📊 Standard Analysis</option>
                                <option value="detailed">🔬 Deep Research</option>
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
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Creates professional, well-structured reports</p>
                        </div>
                        
                        <div class="agent-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>🔍 Quality Reviewer</strong>
                                <span class="status-ready">Ready</span>
                            </div>
                            <p style="color: #b0b0b0; font-size: 0.9rem;">Reviews and ensures quality of research outputs</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- History Page -->
        <div id="page-history" class="page-content">
            <div class="page-header">
                <h1 class="page-title">📚 MISSION ARCHIVE</h1>
                <p class="page-subtitle">Complete History of Research Missions</p>
            </div>
            
            <div class="panel">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                    <div class="panel-header" style="margin-bottom: 0;">
                        <i class="fas fa-database"></i>
                        <h2 class="panel-title">Research History</h2>
                    </div>
                    <button class="btn btn-danger" onclick="clearHistory()">
                        <i class="fas fa-trash"></i> Clear Archive
                    </button>
                </div>
                
                <div id="historyList">
                    <div style="text-align: center; padding: 3rem; color: #666;">
                        <i class="fas fa-satellite" style="font-size: 4rem; margin-bottom: 1rem;"></i>
                        <p>No missions in archive yet</p>
                        <p style="font-size: 0.9rem;">Complete your first research mission to see it here!</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Reports Page -->
        <div id="page-reports" class="page-content">
            <div class="page-header">
                <h1 class="page-title">📊 REPORT GENERATOR</h1>
                <p class="page-subtitle">Generate Comprehensive Reports from Research Missions</p>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <i class="fas fa-file-alt"></i>
                    <h2 class="panel-title">Custom Report Generator</h2>
                </div>
                
                <div class="grid-2">
                    <div>
                        <div class="form-group">
                            <label class="form-label">📋 Report Title</label>
                            <input type="text" id="reportTitle" class="form-input" value="Comprehensive Research Report">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📊 Report Type</label>
                            <select id="reportType" class="form-select">
                                <option value="comprehensive">🌌 Comprehensive Analysis</option>
                                <option value="summary">⚡ Executive Summary</option>
                                <option value="comparison">⚖️ Comparative Study</option>
                                <option value="trend">📈 Trend Analysis</option>
                            </select>
                        </div>
                        
                        <button class="btn btn-success btn-full" onclick="generateReport()" id="generateBtn" disabled>
                            <i class="fas fa-magic"></i> Generate Report
                        </button>
                    </div>
                    
                    <div>
                        <h4 style="color: #00d4ff; margin-bottom: 1rem;">Select Research Missions:</h4>
                        <div id="taskSelection">
                            <div style="text-align: center; padding: 2rem; color: #666;">
                                <i class="fas fa-clipboard-list" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                                <p>No completed missions available</p>
                                <p style="font-size: 0.9rem;">Complete some research missions first!</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Analytics Page -->
        <div id="page-analytics" class="page-content">
            <div class="page-header">
                <h1 class="page-title">📈 ANALYTICS DASHBOARD</h1>
                <p class="page-subtitle">Performance Metrics and Insights</p>
            </div>
            
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-number" id="successRate">""" + str(user_stats["success_rate"]) + """%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="avgTime">2.5</div>
                    <div class="stat-label">Avg Time (min)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="totalAgents">8</div>
                    <div class="stat-label">Active Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="efficiency">95%</div>
                    <div class="stat-label">Efficiency</div>
                </div>
            </div>
            
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-chart-pie"></i>
                        <h2 class="panel-title">Research Mode Distribution</h2>
                    </div>
                    <div style="padding: 2rem; text-align: center;">
                        <div style="margin: 1rem 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>🤖 IO Intelligence</span>
                                <span>45%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px;">
                                <div style="background: #00d4ff; height: 100%; width: 45%; border-radius: 5px;"></div>
                            </div>
                        </div>
                        <div style="margin: 1rem 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>👥 Multi-Agent</span>
                                <span>35%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px;">
                                <div style="background: #4ecdc4; height: 100%; width: 35%; border-radius: 5px;"></div>
                            </div>
                        </div>
                        <div style="margin: 1rem 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span>🌌 Multi-Topic</span>
                                <span>20%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px;">
                                <div style="background: #ff6b6b; height: 100%; width: 20%; border-radius: 5px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-trophy"></i>
                        <h2 class="panel-title">Achievements</h2>
                    </div>
                    <div id="achievements">
                        <div style="padding: 1rem; background: rgba(255, 255, 255, 0.1); border-radius: 10px; margin: 0.5rem 0;">
                            🥇 First Mission Completed
                        </div>
                        <div style="padding: 1rem; background: rgba(255, 255, 255, 0.1); border-radius: 10px; margin: 0.5rem 0;">
                            🚀 Research Pioneer
                        </div>
                        <div style="padding: 1rem; background: rgba(255, 255, 255, 0.1); border-radius: 10px; margin: 0.5rem 0;">
                            📊 Data Explorer
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- About Page -->
        <div id="page-about" class="page-content">
            <div class="page-header">
                <h1 class="page-title">ℹ️ ABOUT PLATFORM</h1>
                <p class="page-subtitle">Launch IO Hackathon - Unified Research Platform</p>
            </div>
            
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-info-circle"></i>
                        <h2 class="panel-title">Platform Overview</h2>
                    </div>
                    <p style="color: #e0e0e0; line-height: 1.6; margin-bottom: 1rem;">
                        This unified research platform combines the power of IO Intelligence API with a sophisticated 
                        multi-agent system to provide comprehensive research capabilities.
                    </p>
                    <p style="color: #e0e0e0; line-height: 1.6; margin-bottom: 1rem;">
                        Built for the Launch IO Hackathon 2025, this platform demonstrates the integration of 
                        cutting-edge AI technologies with practical research applications.
                    </p>
                    <div style="margin-top: 2rem;">
                        <h4 style="color: #00d4ff; margin-bottom: 1rem;">🚀 Key Features:</h4>
                        <ul style="color: #b0b0b0; line-height: 1.8;">
                            <li>• Real IO Intelligence API Integration</li>
                            <li>• 8-Agent Multi-Agent Research System</li>
                            <li>• Advanced Report Generation</li>
                            <li>• Complete Mission History</li>
                            <li>• Performance Analytics</li>
                            <li>• Real-time Progress Tracking</li>
                        </ul>
                    </div>
                </div>
                
                <div class="panel">
                    <div class="panel-header">
                        <i class="fas fa-cogs"></i>
                        <h2 class="panel-title">Technical Specifications</h2>
                    </div>
                    <div style="color: #e0e0e0; line-height: 1.6;">
                        <p><strong>AI Model:</strong> Llama-3.3-70B-Instruct</p>
                        <p><strong>Backend:</strong> FastAPI with async processing</p>
                        <p><strong>Frontend:</strong> Modern HTML5 + CSS3 + JavaScript</p>
                        <p><strong>Architecture:</strong> Multi-agent distributed system</p>
                        <p><strong>Data Storage:</strong> JSON-based persistence</p>
                        <p><strong>API Integration:</strong> IO Intelligence Platform</p>
                    </div>
                    
                    <div style="margin-top: 2rem;">
                        <h4 style="color: #00d4ff; margin-bottom: 1rem;">👥 Multi-Agent System:</h4>
                        <ul style="color: #b0b0b0; line-height: 1.8; font-size: 0.9rem;">
                            <li>• Research Coordinator</li>
                            <li>• Web Research Specialist</li>
                            <li>• Data Analysis Expert</li>
                            <li>• Content Synthesizer</li>
                            <li>• Fact Verification Specialist</li>
                            <li>• Trend Analysis Expert</li>
                            <li>• Professional Report Writer</li>
                            <li>• Quality Assurance Reviewer</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <i class="fas fa-trophy"></i>
                    <h2 class="panel-title">Hackathon Information</h2>
                </div>
                <div class="grid-3">
                    <div style="text-align: center;">
                        <h4 style="color: #00d4ff; margin-bottom: 0.5rem;">Event</h4>
                        <p style="color: #e0e0e0;">Launch IO Hackathon 2025</p>
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: #00d4ff; margin-bottom: 0.5rem;">Theme</h4>
                        <p style="color: #e0e0e0;">AI-Powered Innovation</p>
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: #00d4ff; margin-bottom: 0.5rem;">Version</h4>
                        <p style="color: #e0e0e0;">5.0.0 Unified Edition</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Progress container -->
    <div class="progress-container" id="progressContainer">
        <div style="text-align: center;">
            <h3><i class="fas fa-satellite-dish"></i> Mission in Progress</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div id="statusMessage" style="color: #00d4ff; font-weight: 600;">Initializing mission parameters...</div>
        </div>
    </div>
    
    <!-- Results container -->
    <div class="results-container" id="resultsContainer">
        <h2><i class="fas fa-telescope"></i> Mission Results</h2>
        <div id="resultsContent"></div>
    </div>
    
    <!-- Footer -->
    <footer class="footer">
        <p>&copy; 2025 Launch IO Unified Research Platform. Exploring the infinite possibilities of AI. 🚀</p>
    </footer>
    
    <!-- Notification -->
    <div class="notification" id="notification"></div> 
   
    <script>
        // Global variables
        let currentTaskId = null;
        let searchHistory = [];
        let selectedTasks = new Set();
        let userStats = {total_research: """ + str(user_stats["total_research"]) + """, total_reports: """ + str(user_stats["total_reports"]) + """, time_saved: """ + str(user_stats["time_saved"]) + """};
        
        // Page navigation
        function showPage(pageId) {
            // Hide all pages
            document.querySelectorAll('.page-content').forEach(page => {
                page.style.display = 'none';
                page.classList.remove('active');
            });
            
            // Show selected page
            const targetPage = document.getElementById('page-' + pageId);
            if (targetPage) {
                targetPage.style.display = 'block';
                targetPage.classList.add('active');
            }
            
            // Update navigation
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.classList.remove('active');
            });
            const navLink = document.getElementById('nav-' + pageId);
            if (navLink) {
                navLink.classList.add('active');
            }
            
            // Load page-specific data
            if (pageId === 'history') {
                loadSearchHistory();
            } else if (pageId === 'reports') {
                loadTaskSelection();
            }
        }
        
        // Navigation event listeners
        document.addEventListener('DOMContentLoaded', function() {
            // Set up navigation
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const pageId = this.getAttribute('href').replace('#', '').replace('/', '');
                    if (pageId === '' || pageId === 'home') {
                        showPage('home');
                    } else {
                        showPage(pageId);
                    }
                });
            });
            
            // Initialize
            loadSearchHistory();
            updateStats();
            
            // Set up form submission
            const researchForm = document.getElementById('researchForm');
            if (researchForm) {
                researchForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const topic = document.getElementById('topic').value;
                    const mode = document.getElementById('mode').value;
                    const priority = document.getElementById('priority').value;
                    const depth = document.getElementById('depth').value;
                    
                    if (!topic.trim()) {
                        showNotification('🚨 Please enter a research target!', 'error');
                        return;
                    }
                    
                    await startResearch(topic, mode, priority, depth);
                });
            }
        });
        
        // Show notification
        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification show ${type}`;
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        // Update stats
        function updateStats() {
            const totalResearchEl = document.getElementById('totalResearch');
            const totalReportsEl = document.getElementById('totalReports');
            const timeSavedEl = document.getElementById('timeSaved');
            
            if (totalResearchEl) totalResearchEl.textContent = userStats.total_research;
            if (totalReportsEl) totalReportsEl.textContent = userStats.total_reports;
            if (timeSavedEl) timeSavedEl.textContent = userStats.time_saved;
        }
        
        // Quick research function
        function quickResearch(topic) {
            showPage('research');
            setTimeout(() => {
                document.getElementById('topic').value = topic;
                showNotification('🎯 Research target locked!');
            }, 100);
        }
        
        // Set topic function
        function setTopic(topic) {
            document.getElementById('topic').value = topic;
            showNotification('🎯 Research target locked!');
        }
        
        // Start research
        async function startResearch(topic, mode, priority, depth) {
            const startBtn = document.getElementById('startBtn');
            const progressContainer = document.getElementById('progressContainer');
            const resultsContainer = document.getElementById('resultsContainer');
            
            startBtn.disabled = true;
            startBtn.innerHTML = '<div class="loading-spinner"></div> Launching Mission...';
            progressContainer.style.display = 'block';
            resultsContainer.style.display = 'none';
            
            showNotification('🚀 Mission launched successfully!');
            
            try {
                const response = await fetch('/api/research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic, mode, priority, depth })
                });
                const data = await response.json();
                currentTaskId = data.task_id;
                pollProgress();
            } catch (error) {
                showNotification('🚨 Mission launch failed!', 'error');
                resetUI();
            }
        }
        
        // Poll progress
        async function pollProgress() {
            if (!currentTaskId) return;
            
            try {
                const response = await fetch(`/api/research/${currentTaskId}`);
                const data = await response.json();
                updateProgress(data);
                
                if (data.status === 'completed') {
                    await showResults();
                    loadSearchHistory();
                    loadTaskSelection();
                    userStats.total_research++;
                    userStats.time_saved += Math.floor(Math.random() * 5) + 1;
                    updateStats();
                    showNotification('🎉 Mission completed successfully!');
                } else if (data.status === 'failed') {
                    showNotification('🚨 Mission failed!', 'error');
                    resetUI();
                } else {
                    setTimeout(pollProgress, 1000);
                }
            } catch (error) {
                setTimeout(pollProgress, 2000);
            }
        }
        
        // Update progress
        function updateProgress(data) {
            document.getElementById('progressFill').style.width = data.progress + '%';
            document.getElementById('statusMessage').textContent = data.current_phase + ': ' + (data.message || 'Processing...');
        }
        
        // Show results
        async function showResults() {
            try {
                const response = await fetch(`/api/research/${currentTaskId}/result`);
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                showNotification('🚨 Failed to retrieve mission results!', 'error');
            }
            resetUI();
        }
        
        // Display results
        function displayResults(data) {
            const resultsContainer = document.getElementById('resultsContainer');
            const resultsContent = document.getElementById('resultsContent');
            let html = '';
            
            if (data.report && typeof data.report === 'object') {
                if (data.report.research_results) {
                    data.report.research_results.forEach(result => {
                        if (!result.error) {
                            html += `
                                <div class="result-item">
                                    <div class="result-title">🌟 ${result.topic}</div>
                                    <div class="result-summary">${result.summary}</div>
                                </div>
                            `;
                        }
                    });
                }
                
                if (data.report.comprehensive_report && !data.report.comprehensive_report.error) {
                    html += `
                        <div class="result-item">
                            <div class="result-title">📊 Comprehensive Analysis</div>
                            <div class="result-summary">${data.report.comprehensive_report.report_summary}</div>
                        </div>
                    `;
                }
                
                if (data.report.summary) {
                    html += `
                        <div class="result-item">
                            <div class="result-title">🎯 ${data.topic}</div>
                            <div class="result-summary">${data.report.summary}</div>
                        </div>
                    `;
                }
            } else {
                html = `
                    <div class="result-item">
                        <div class="result-title">🔍 Research Results</div>
                        <div class="result-summary">${data.report}</div>
                    </div>
                `;
            }
            
            if (!html) {
                html = '<div style="text-align: center; padding: 2rem; color: #666;"><i class="fas fa-satellite" style="font-size: 3rem; margin-bottom: 1rem;"></i><p>No results to display</p></div>';
            }
            
            resultsContent.innerHTML = html;
            resultsContainer.style.display = 'block';
        }
        
        // Reset UI
        function resetUI() {
            const startBtn = document.getElementById('startBtn');
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-rocket"></i> Launch Research Mission';
            document.getElementById('progressContainer').style.display = 'none';
            currentTaskId = null;
        }
        
        // Load search history
        async function loadSearchHistory() {
            try {
                const response = await fetch('/api/history');
                const data = await response.json();
                searchHistory = data.history || [];
                userStats = data.stats || userStats;
                displaySearchHistory();
                updateStats();
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }
        
        // Display search history
        function displaySearchHistory() {
            const historyList = document.getElementById('historyList');
            if (!historyList) return;
            
            if (searchHistory.length === 0) {
                historyList.innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: #666;">
                        <i class="fas fa-satellite" style="font-size: 4rem; margin-bottom: 1rem;"></i>
                        <p>No missions in archive yet</p>
                        <p style="font-size: 0.9rem;">Complete your first research mission to see it here!</p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            searchHistory.forEach(item => {
                const date = new Date(item.created_at).toLocaleDateString();
                const time = new Date(item.created_at).toLocaleTimeString();
                const modeIcon = item.mode === 'io_intelligence' ? '🤖' : item.mode === 'multi_agent' ? '👥' : item.mode === 'multi_topic' ? '🌌' : '💫';
                const statusIcon = item.status === 'completed' ? '✅' : '⏳';
                
                html += `
                    <div class="history-item">
                        <h4>${modeIcon} ${item.topic}</h4>
                        <p><strong>Mode:</strong> ${item.mode} | <strong>Status:</strong> ${statusIcon} ${item.status}</p>
                        <p style="color: #b0b0b0;">${item.summary}</p>
                        <small style="color: #666;">🕒 ${date} at ${time}</small>
                        <div class="history-actions">
                            <button onclick="rerunResearch('${item.topic}', '${item.mode}')" style="background: linear-gradient(45deg, #6c757d, #5a6268); color: white;">
                                🔄 Rerun Mission
                            </button>
                            <button onclick="deleteHistoryItem('${item.task_id}')" style="background: linear-gradient(45deg, #ff6b6b, #ee5a52); color: white;">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                `;
            });
            
            historyList.innerHTML = html;
        }
        
        // Clear history
        async function clearHistory() {
            if (confirm('🚨 Are you sure you want to clear the entire mission archive?')) {
                try {
                    await fetch('/api/history', { method: 'DELETE' });
                    searchHistory = [];
                    userStats = {total_research: 0, total_reports: 0, time_saved: 0};
                    displaySearchHistory();
                    loadTaskSelection();
                    updateStats();
                    showNotification('🗑️ Mission archive cleared!');
                } catch (error) {
                    showNotification('🚨 Failed to clear archive!', 'error');
                }
            }
        }
        
        // Delete history item
        async function deleteHistoryItem(taskId) {
            try {
                await fetch(`/api/history/${taskId}`, { method: 'DELETE' });
                loadSearchHistory();
                loadTaskSelection();
                showNotification('🗑️ Mission deleted from archive!');
            } catch (error) {
                showNotification('🚨 Failed to delete mission!', 'error');
            }
        }
        
        // Rerun research
        function rerunResearch(topic, mode) {
            showPage('research');
            setTimeout(() => {
                document.getElementById('topic').value = topic;
                document.getElementById('mode').value = mode;
                showNotification('🎯 Mission parameters loaded!');
            }, 100);
        }
        
        // Load task selection for reports
        async function loadTaskSelection() {
            const taskSelection = document.getElementById('taskSelection');
            const generateBtn = document.getElementById('generateBtn');
            if (!taskSelection || !generateBtn) return;
            
            const completedTasks = searchHistory.filter(item => item.status === 'completed');
            
            if (completedTasks.length === 0) {
                taskSelection.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: #666;">
                        <i class="fas fa-clipboard-list" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                        <p>No completed missions available</p>
                        <p style="font-size: 0.9rem;">Complete some research missions first!</p>
                    </div>
                `;
                generateBtn.disabled = true;
                return;
            }
            
            let html = '';
            completedTasks.forEach(task => {
                const date = new Date(task.created_at).toLocaleDateString();
                const modeIcon = task.mode === 'io_intelligence' ? '🤖' : task.mode === 'multi_agent' ? '👥' : task.mode === 'multi_topic' ? '🌌' : '💫';
                
                html += `
                    <div class="checkbox-group">
                        <input type="checkbox" id="task_${task.task_id}" value="${task.task_id}" onchange="updateSelectedTasks()">
                        <label for="task_${task.task_id}">
                            <strong>${modeIcon} ${task.topic}</strong><br>
                            <small style="color: #b0b0b0;">${task.mode} • ${date}</small>
                        </label>
                    </div>
                `;
            });
            
            taskSelection.innerHTML = html;
            updateSelectedTasks();
        }
        
        // Update selected tasks
        function updateSelectedTasks() {
            selectedTasks.clear();
            document.querySelectorAll('#taskSelection input[type="checkbox"]:checked').forEach(checkbox => {
                selectedTasks.add(checkbox.value);
            });
            
            const generateBtn = document.getElementById('generateBtn');
            if (generateBtn) {
                generateBtn.disabled = selectedTasks.size === 0;
                
                if (selectedTasks.size > 0) {
                    generateBtn.innerHTML = `<i class="fas fa-magic"></i> Generate Report (${selectedTasks.size} missions)`;
                } else {
                    generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Report';
                }
            }
        }
        
        // Generate report
        async function generateReport() {
            if (selectedTasks.size === 0) {
                showNotification('🚨 Please select at least one mission!', 'error');
                return;
            }
            
            const reportTitle = document.getElementById('reportTitle').value || 'Comprehensive Research Report';
            const reportType = document.getElementById('reportType').value;
            
            showNotification('📊 Generating comprehensive report...');
            
            try {
                const response = await fetch('/api/generate-report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task_ids: Array.from(selectedTasks),
                        report_title: reportTitle,
                        report_type: reportType
                    })
                });
                
                const data = await response.json();
                currentTaskId = data.task_id;
                
                document.getElementById('progressContainer').style.display = 'block';
                document.getElementById('resultsContainer').style.display = 'none';
                
                pollProgress();
                
                userStats.total_reports++;
                updateStats();
                
            } catch (error) {
                showNotification('🚨 Failed to generate report!', 'error');
            }
        }
        
        // Add CSS for agent status and other elements
        const additionalCSS = `
            .page-content { display: none; }
            .page-content.active { display: block; }
            .agent-item { 
                background: rgba(255, 255, 255, 0.05); 
                padding: 1rem; 
                border-radius: 10px; 
                margin: 1rem 0; 
                border-left: 3px solid #00d4ff; 
            }
            .status-ready { 
                background: #4caf50; 
                color: white; 
                padding: 0.2rem 0.5rem; 
                border-radius: 10px; 
                font-size: 0.8rem; 
            }
        `;
        
        // Add the CSS to the document
        const style = document.createElement('style');
        style.textContent = additionalCSS;
        document.head.appendChild(style);
    </script>
</body>
</html>
    """)

# API Routes
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
        "id": report_id, "topic": request.report_title, "mode": "report_generation", "status": "starting",
        "progress": 0, "current_phase": "Collecting data", "message": "Gathering mission data...", 
        "created_at": datetime.now().isoformat(), "result": None
    }
    background_tasks.add_task(execute_report_generation, report_id, request)
    return {"task_id": report_id, "status": "started"}# B
ackground task functions
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
                          
        elif request.mode == "multi_agent":
            research_tasks[task_id]["progress"] = 30
            research_tasks[task_id]["message"] = "Activating multi-agent system..."
            
            # Use multi-agent system
            if request.depth == "detailed":
                result = await multi_agent_system.research_with_multi_agents(request.topic, "detailed")
            else:
                result = await multi_agent_system.research_with_multi_agents(request.topic, "standard")
            
            final_result = {"task_id": task_id, "topic": request.topic, "mode": request.mode, "status": "completed",
                          "report": result, "created_at": research_tasks[task_id]["created_at"], 
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
        
        # Generate comprehensive report
        report_content = f"🚀 {request.report_title}\n\n📊 Generated from {len(collected_data)} research missions:\n\n"
        for item in collected_data:
            report_content += f"🎯 {item['topic']} ({item['mode']}):\n{str(item['report'])[:200]}...\n\n"
        
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
    print("🚀 Starting Unified Research Platform...")
    print("🌐 Open your browser to: http://localhost:8000")
    print("✨ Complete unified application with all features!")
    print("🤖 Multi-Agent System + IO Intelligence Integration")
    print("📊 Search History + Report Generator + Analytics")
    uvicorn.run(app, host="127.0.0.1", port=8000)