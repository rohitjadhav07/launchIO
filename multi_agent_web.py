#!/usr/bin/env python3
"""
Multi-Agent Comparison Web Interface
Web interface for comparing multiple AI agents and downloading reports
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from multi_agent_comparison import MultiAgentComparison

app = FastAPI(title="🤖 Multi-Agent AI Comparison System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
multi_agent_system = MultiAgentComparison()
analysis_tasks: Dict[str, Dict] = {}
completed_analyses: List[Dict] = []

class AnalysisRequest(BaseModel):
    topic: str
    analysis_type: str = "comprehensive"
    agents: List[str] = []  # Specific agents to use, empty = all

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Multi-Agent AI Comparison System</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            color: #333; 
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 30px; 
            padding: 2rem; 
            background: rgba(0,0,0,0.2); 
            border-radius: 15px; 
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        @media (max-width: 768px) { .main-grid { grid-template-columns: 1fr; } }
        .panel { 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; 
            padding: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        input, select, textarea { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e1e5e9; 
            border-radius: 8px; 
            font-size: 16px; 
        }
        input:focus, select:focus, textarea:focus { 
            outline: none; 
            border-color: #667eea; 
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3); 
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            padding: 15px 30px; 
            border-radius: 8px; 
            font-size: 16px; 
            font-weight: 600; 
            cursor: pointer; 
            width: 100%; 
            margin: 10px 0; 
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-success { background: linear-gradient(135deg, #28a745, #20c997); }
        .btn-danger { background: linear-gradient(135deg, #dc3545, #fd7e14); }
        .agent-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin: 15px 0; 
        }
        .agent-card { 
            background: #f8f9fa; 
            border: 2px solid #e9ecef; 
            border-radius: 10px; 
            padding: 15px; 
            text-align: center; 
            cursor: pointer; 
            transition: all 0.3s; 
        }
        .agent-card:hover { border-color: #667eea; transform: translateY(-2px); }
        .agent-card.selected { border-color: #28a745; background: #d4edda; }
        .progress-container { 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; 
            padding: 25px; 
            margin: 20px 0; 
            display: none; 
        }
        .progress-bar { 
            width: 100%; 
            height: 20px; 
            background: #e9ecef; 
            border-radius: 10px; 
            overflow: hidden; 
            margin: 15px 0; 
        }
        .progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            width: 0%; 
            transition: width 0.5s; 
        }
        .results-container { 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; 
            padding: 25px; 
            margin: 20px 0; 
            display: none; 
        }
        .agent-result { 
            background: #f8f9fa; 
            border-left: 4px solid #667eea; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 0 8px 8px 0; 
        }
        .agent-result h4 { color: #667eea; margin-bottom: 10px; }
        .key-points { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
        .key-point { 
            background: #667eea; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 15px; 
            font-size: 0.9rem; 
        }
        .download-section { 
            background: #e9ecef; 
            padding: 20px; 
            border-radius: 10px; 
            margin-top: 20px; 
        }
        .download-buttons { display: flex; gap: 10px; flex-wrap: wrap; }
        .download-buttons .btn { width: auto; padding: 10px 20px; }
        .comparison-section { 
            background: #fff3cd; 
            border: 1px solid #ffeaa7; 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px 0; 
        }
        .status-message { text-align: center; padding: 20px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Multi-Agent AI Comparison System</h1>
            <p>Compare multiple AI agents • Generate detailed reports • Download analysis</p>
            <p><strong>Powered by IO Intelligence</strong> • Multiple specialized AI perspectives</p>
        </div>
        
        <div class="main-grid">
            <!-- Analysis Setup Panel -->
            <div class="panel">
                <h2><i class="fas fa-cogs"></i> Analysis Setup</h2>
                
                <form id="analysisForm">
                    <div class="form-group">
                        <label for="topic">Research Topic</label>
                        <input type="text" id="topic" placeholder="Enter topic for multi-agent analysis..." required>
                    </div>
                    
                    <div class="form-group">
                        <label for="analysisType">Analysis Type</label>
                        <select id="analysisType">
                            <option value="comprehensive">🔍 Comprehensive Analysis</option>
                            <option value="comparative">⚖️ Comparative Study</option>
                            <option value="strategic">📈 Strategic Assessment</option>
                            <option value="technical">⚙️ Technical Deep Dive</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn" id="startBtn">
                        <i class="fas fa-rocket"></i> Start Multi-Agent Analysis
                    </button>
                </form>
                
                <div class="form-group">
                    <label>Quick Topics</label>
                    <div class="agent-grid">
                        <div class="agent-card" onclick="setTopic('artificial intelligence in healthcare')">
                            🏥 AI in Healthcare
                        </div>
                        <div class="agent-card" onclick="setTopic('blockchain technology adoption')">
                            ⛓️ Blockchain Adoption
                        </div>
                        <div class="agent-card" onclick="setTopic('quantum computing applications')">
                            ⚛️ Quantum Computing
                        </div>
                        <div class="agent-card" onclick="setTopic('sustainable energy solutions')">
                            🌱 Sustainable Energy
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Agent Selection Panel -->
            <div class="panel">
                <h2><i class="fas fa-users"></i> AI Agent Selection</h2>
                <p>Select specific agents or leave empty to use all available agents:</p>
                
                <div id="agentSelection" class="agent-grid">
                    <div class="agent-card" data-agent="IO_Intelligence_Researcher">
                        <i class="fas fa-search"></i>
                        <h4>Research Specialist</h4>
                        <p>Comprehensive research with evidence</p>
                    </div>
                    <div class="agent-card" data-agent="Critical_Analyst">
                        <i class="fas fa-balance-scale"></i>
                        <h4>Critical Analyst</h4>
                        <p>Balanced perspectives & bias analysis</p>
                    </div>
                    <div class="agent-card" data-agent="Technical_Expert">
                        <i class="fas fa-cog"></i>
                        <h4>Technical Expert</h4>
                        <p>Implementation & feasibility focus</p>
                    </div>
                    <div class="agent-card" data-agent="Business_Strategist">
                        <i class="fas fa-chart-line"></i>
                        <h4>Business Strategist</h4>
                        <p>Market & economic analysis</p>
                    </div>
                    <div class="agent-card" data-agent="Innovation_Scout">
                        <i class="fas fa-lightbulb"></i>
                        <h4>Innovation Scout</h4>
                        <p>Trends & future possibilities</p>
                    </div>
                    <div class="agent-card" data-agent="Risk_Assessor">
                        <i class="fas fa-shield-alt"></i>
                        <h4>Risk Assessor</h4>
                        <p>Challenges & mitigation strategies</p>
                    </div>
                </div>
                
                <button class="btn btn-success" onclick="selectAllAgents()">
                    <i class="fas fa-check-double"></i> Select All Agents
                </button>
                <button class="btn btn-danger" onclick="clearAgentSelection()">
                    <i class="fas fa-times"></i> Clear Selection
                </button>
            </div>
        </div>
        
        <!-- Progress Container -->
        <div class="progress-container" id="progressContainer">
            <h3><i class="fas fa-cogs"></i> Multi-Agent Analysis in Progress</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div id="statusMessage" class="status-message">Initializing agents...</div>
        </div>
        
        <!-- Results Container -->
        <div class="results-container" id="resultsContainer">
            <h2><i class="fas fa-chart-bar"></i> Multi-Agent Analysis Results</h2>
            <div id="resultsContent"></div>
            
            <!-- Download Section -->
            <div class="download-section">
                <h3><i class="fas fa-download"></i> Download Detailed Reports</h3>
                <p>Generate and download comprehensive analysis reports in multiple formats:</p>
                <div class="download-buttons">
                    <button class="btn btn-success" onclick="downloadReport('markdown')">
                        <i class="fas fa-file-alt"></i> Download Markdown
                    </button>
                    <button class="btn btn-success" onclick="downloadReport('html')">
                        <i class="fas fa-file-code"></i> Download HTML
                    </button>
                    <button class="btn btn-success" onclick="downloadReport('json')">
                        <i class="fas fa-file-code"></i> Download JSON
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentTaskId = null;
        let selectedAgents = new Set();
        let currentResults = null;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setupAgentSelection();
        });
        
        // Form submission
        document.getElementById('analysisForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const topic = document.getElementById('topic').value;
            const analysisType = document.getElementById('analysisType').value;
            
            if (!topic.trim()) {
                alert('Please enter a research topic');
                return;
            }
            
            await startAnalysis(topic, analysisType);
        });
        
        function setTopic(topic) {
            document.getElementById('topic').value = topic;
        }
        
        function setupAgentSelection() {
            document.querySelectorAll('.agent-card[data-agent]').forEach(card => {
                card.addEventListener('click', function() {
                    const agent = this.dataset.agent;
                    if (selectedAgents.has(agent)) {
                        selectedAgents.delete(agent);
                        this.classList.remove('selected');
                    } else {
                        selectedAgents.add(agent);
                        this.classList.add('selected');
                    }
                });
            });
        }
        
        function selectAllAgents() {
            document.querySelectorAll('.agent-card[data-agent]').forEach(card => {
                const agent = card.dataset.agent;
                selectedAgents.add(agent);
                card.classList.add('selected');
            });
        }
        
        function clearAgentSelection() {
            selectedAgents.clear();
            document.querySelectorAll('.agent-card[data-agent]').forEach(card => {
                card.classList.remove('selected');
            });
        }
        
        async function startAnalysis(topic, analysisType) {
            const startBtn = document.getElementById('startBtn');
            const progressContainer = document.getElementById('progressContainer');
            const resultsContainer = document.getElementById('resultsContainer');
            
            startBtn.disabled = true;
            startBtn.textContent = '🔄 Starting Analysis...';
            progressContainer.style.display = 'block';
            resultsContainer.style.display = 'none';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        topic: topic,
                        analysis_type: analysisType,
                        agents: Array.from(selectedAgents)
                    })
                });
                
                const data = await response.json();
                currentTaskId = data.task_id;
                pollProgress();
                
            } catch (error) {
                alert('Failed to start analysis: ' + error.message);
                resetUI();
            }
        }
        
        async function pollProgress() {
            if (!currentTaskId) return;
            
            try {
                const response = await fetch(`/api/analyze/${currentTaskId}`);
                const data = await response.json();
                
                updateProgress(data);
                
                if (data.status === 'completed') {
                    await showResults();
                } else if (data.status === 'failed') {
                    alert('Analysis failed: ' + data.error);
                    resetUI();
                } else {
                    setTimeout(pollProgress, 2000);
                }
                
            } catch (error) {
                setTimeout(pollProgress, 3000);
            }
        }
        
        function updateProgress(data) {
            const progressFill = document.getElementById('progressFill');
            const statusMessage = document.getElementById('statusMessage');
            
            progressFill.style.width = data.progress + '%';
            statusMessage.textContent = data.message || 'Processing...';
        }
        
        async function showResults() {
            try {
                const response = await fetch(`/api/analyze/${currentTaskId}/result`);
                const data = await response.json();
                
                currentResults = data;
                displayResults(data);
                
            } catch (error) {
                alert('Failed to fetch results: ' + error.message);
            }
            
            resetUI();
        }
        
        function displayResults(data) {
            const resultsContainer = document.getElementById('resultsContainer');
            const resultsContent = document.getElementById('resultsContent');
            
            let html = `
                <div class="comparison-section">
                    <h3>📊 Executive Summary</h3>
                    <p><strong>Topic:</strong> ${data.topic}</p>
                    <p><strong>Analysis Type:</strong> ${data.analysis_type}</p>
                    <p><strong>Agents Consulted:</strong> ${Object.keys(data.agent_results).length}</p>
                    <p><strong>Successful Analyses:</strong> ${Object.values(data.agent_results).filter(r => !r.error).length}</p>
                </div>
            `;
            
            // Agent results
            for (const [agentName, result] of Object.entries(data.agent_results)) {
                if (!result.error) {
                    html += `
                        <div class="agent-result">
                            <h4>🤖 ${agentName}</h4>
                            <p><strong>Specialty:</strong> ${result.specialty}</p>
                            <p><strong>Analysis:</strong></p>
                            <p>${result.summary}</p>
                            <div class="key-points">
                                ${result.key_points.map(point => `<span class="key-point">${point}</span>`).join('')}
                            </div>
                        </div>
                    `;
                } else {
                    html += `
                        <div class="agent-result" style="border-left-color: #dc3545; background: #f8d7da;">
                            <h4>❌ ${agentName}</h4>
                            <p><strong>Error:</strong> ${result.error}</p>
                        </div>
                    `;
                }
            }
            
            // Comparison analysis
            if (data.comparison && data.comparison.consensus_points.length > 0) {
                html += `
                    <div class="comparison-section">
                        <h3>🤝 Consensus Points</h3>
                        <ul>
                            ${data.comparison.consensus_points.map(point => `<li>${point}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            
            resultsContent.innerHTML = html;
            resultsContainer.style.display = 'block';
        }
        
        function resetUI() {
            const startBtn = document.getElementById('startBtn');
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-rocket"></i> Start Multi-Agent Analysis';
            document.getElementById('progressContainer').style.display = 'none';
            currentTaskId = null;
        }
        
        async function downloadReport(format) {
            if (!currentResults) {
                alert('No results available for download');
                return;
            }
            
            try {
                const response = await fetch(`/api/download-report/${format}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentResults)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `multi_agent_report_${Date.now()}.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    alert('Failed to download report');
                }
                
            } catch (error) {
                alert('Download failed: ' + error.message);
            }
        }
    </script>
</body>
</html>
    """)

@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start multi-agent analysis"""
    task_id = str(uuid.uuid4())
    
    analysis_tasks[task_id] = {
        "id": task_id,
        "topic": request.topic,
        "analysis_type": request.analysis_type,
        "agents": request.agents,
        "status": "starting",
        "progress": 0,
        "message": "Initializing multi-agent analysis...",
        "created_at": datetime.now().isoformat(),
        "result": None
    }
    
    background_tasks.add_task(execute_multi_agent_analysis, task_id, request)
    
    return {"task_id": task_id, "status": "started"}

@app.get("/api/analyze/{task_id}")
async def get_analysis_status(task_id: str):
    """Get analysis status"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "message": task["message"],
        "topic": task["topic"]
    }

@app.get("/api/analyze/{task_id}/result")
async def get_analysis_result(task_id: str):
    """Get analysis result"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    return task["result"]

@app.post("/api/download-report/{format}")
async def download_report(format: str, results: dict):
    """Generate and download report"""
    try:
        report_content = multi_agent_system.generate_detailed_report(results, format)
        
        # Set appropriate content type and filename
        content_types = {
            "markdown": "text/markdown",
            "html": "text/html",
            "json": "application/json"
        }
        
        filename = f"multi_agent_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        return Response(
            content=report_content,
            media_type=content_types.get(format, "text/plain"),
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

async def execute_multi_agent_analysis(task_id: str, request: AnalysisRequest):
    """Execute multi-agent analysis in background"""
    try:
        analysis_tasks[task_id]["status"] = "running"
        analysis_tasks[task_id]["progress"] = 10
        analysis_tasks[task_id]["message"] = "Starting multi-agent analysis..."
        
        # Run the analysis
        results = await multi_agent_system.run_multi_agent_analysis(
            request.topic, 
            request.analysis_type
        )
        
        analysis_tasks[task_id]["status"] = "completed"
        analysis_tasks[task_id]["progress"] = 100
        analysis_tasks[task_id]["message"] = "Analysis completed successfully!"
        analysis_tasks[task_id]["result"] = results
        
        # Store in completed analyses
        completed_analyses.append(results)
        
    except Exception as e:
        analysis_tasks[task_id]["status"] = "failed"
        analysis_tasks[task_id]["message"] = f"Analysis failed: {str(e)}"
        analysis_tasks[task_id]["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Multi-Agent AI Comparison Web Interface...")
    print("🌐 Open your browser to: http://localhost:7000")
    print("🤖 Multiple AI agents ready for comparison!")
    uvicorn.run(app, host="127.0.0.1", port=7000)