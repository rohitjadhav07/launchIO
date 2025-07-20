#!/usr/bin/env python3
"""
Complete Launch IO Hackathon Web Interface
With Search History and Report Generator
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

app = FastAPI(title="Launch IO Hackathon - Complete AI Research System", version="2.1.0")

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

# Load/Save search history
def load_search_history():
    global search_history
    try:
        if Path("search_history.json").exists():
            with open("search_history.json", "r") as f:
                search_history = json.load(f)
    except:
        search_history = []

def save_search_history():
    try:
        with open("search_history.json", "w") as f:
            json.dump(search_history, f, indent=2)
    except:
        pass

load_search_history()

class ResearchRequest(BaseModel):
    topic: str
    mode: str = "io_intelligence"

class ReportRequest(BaseModel):
    task_ids: List[str]
    report_title: str = "Research Report"
    report_type: str = "comprehensive"

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Launch IO - Space Research Station</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
            min-height: 100vh;
            color: #ffffff;
            overflow-x: hidden;
        }
        
        /* Animated stars background */
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        
        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle 3s infinite;
        }
        
        @keyframes twinkle {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }
        
        /* Navigation */
        .navbar {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 1000;
            padding: 1rem 0;
        }
        
        .nav-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }
        
        .logo {
            display: flex;
            align-items: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: #00d4ff;
        }
        
        .logo i {
            margin-right: 0.5rem;
            animation: spin 10s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-links a {
            color: #ffffff;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            transition: all 0.3s ease;
        }
        
        .nav-links a:hover, .nav-links a.active {
            background: linear-gradient(45deg, #00d4ff, #ff6b6b);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 212, 255, 0.3);
        }
        
        /* Main content */
        .main-content {
            margin-top: 100px;
            padding: 2rem;
            position: relative;
            z-index: 10;
        }
        
        .hero-section {
            text-align: center;
            margin-bottom: 3rem;
            padding: 3rem 0;
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: bold;
            background: linear-gradient(45deg, #00d4ff, #ff6b6b, #4ecdc4, #45b7d1);
            background-size: 400% 400%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientShift 4s ease-in-out infinite;
            margin-bottom: 1rem;
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: #b0b0b0;
            margin-bottom: 2rem;
        }
        
        .stats-container {
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-bottom: 3rem;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            min-width: 150px;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #00d4ff;
        }
        
        .stat-label {
            color: #b0b0b0;
            font-size: 0.9rem;
        }
        
        /* Main grid */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .main-grid { grid-template-columns: 1fr; }
            .hero-title { font-size: 2.5rem; }
            .stats-container { gap: 1rem; }
            .nav-links { display: none; }
        }
        
        /* Panels */
        .panel {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .panel::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .panel:hover::before {
            left: 100%;
        }
        
        .panel:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 212, 255, 0.2);
        }
        
        .panel-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .panel-header i {
            font-size: 1.5rem;
            margin-right: 0.5rem;
            color: #00d4ff;
        }
        
        .panel-title {
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        /* Form elements */
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #e0e0e0;
        }
        
        .form-input, .form-select {
            width: 100%;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: #ffffff;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #00d4ff;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .form-input::placeholder {
            color: #b0b0b0;
        }
        
        /* Buttons */
        .btn {
            background: linear-gradient(45deg, #00d4ff, #0099cc);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin: 0.5rem 0;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-danger { background: linear-gradient(45deg, #ff6b6b, #ee5a52); }
        .btn-success { background: linear-gradient(45deg, #4ecdc4, #44a08d); }
        .btn-secondary { background: linear-gradient(45deg, #6c757d, #5a6268); }
        
        /* Demo topics */
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .demo-topic {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .demo-topic:hover {
            background: rgba(0, 212, 255, 0.2);
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 1.5rem;
        }
        
        .tab {
            padding: 1rem 1.5rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
            color: #b0b0b0;
        }
        
        .tab.active {
            border-bottom-color: #00d4ff;
            color: #00d4ff;
            font-weight: 600;
        }
        
        .tab:hover {
            color: #ffffff;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Progress */
        .progress-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 800px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 25px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            overflow: hidden;
            margin: 1.5rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #4ecdc4, #ff6b6b);
            background-size: 200% 100%;
            width: 0%;
            transition: width 0.5s ease;
            animation: progressShine 2s linear infinite;
            border-radius: 15px;
        }
        
        @keyframes progressShine {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* Results */
        .results-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 1200px;
            display: none;
        }
        
        .result-item {
            background: rgba(255, 255, 255, 0.1);
            border-left: 4px solid #00d4ff;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            transition: transform 0.3s ease;
        }
        
        .result-item:hover {
            transform: translateX(5px);
            background: rgba(0, 212, 255, 0.1);
        }
        
        .result-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #00d4ff;
            margin-bottom: 1rem;
        }
        
        .result-summary {
            color: #e0e0e0;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        
        .key-points {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .key-point {
            background: linear-gradient(45deg, #00d4ff, #4ecdc4);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        /* History items */
        .history-item {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid #00d4ff;
            transition: all 0.3s ease;
        }
        
        .history-item:hover {
            background: rgba(0, 212, 255, 0.1);
            transform: translateX(5px);
        }
        
        .history-actions {
            margin-top: 1rem;
            display: flex;
            gap: 0.5rem;
        }
        
        .history-actions button {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.3s ease;
        }
        
        /* Checkbox groups */
        .checkbox-group {
            display: flex;
            align-items: center;
            margin: 1rem 0;
            padding: 0.5rem;
            border-radius: 10px;
            transition: background 0.3s ease;
        }
        
        .checkbox-group:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin-right: 1rem;
            transform: scale(1.2);
        }
        
        /* Footer */
        .footer {
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 3rem 0 1rem;
            margin-top: 5rem;
        }
        
        .footer-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }
        
        .footer-section h3 {
            color: #00d4ff;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .footer-section p, .footer-section li {
            color: #b0b0b0;
            line-height: 1.6;
            margin-bottom: 0.5rem;
        }
        
        .footer-section ul {
            list-style: none;
        }
        
        .footer-section a {
            color: #b0b0b0;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .footer-section a:hover {
            color: #00d4ff;
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #666;
        }
        
        /* API Status */
        .api-status {
            background: linear-gradient(45deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1));
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
        }
        
        .api-status i {
            color: #4caf50;
            margin-right: 0.5rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Notification */
        .notification {
            position: fixed;
            top: 100px;
            right: 20px;
            background: rgba(0, 212, 255, 0.9);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1001;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        /* Loading animation */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #00d4ff;
            animation: spin 1s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <!-- Animated stars background -->
    <div class="stars" id="stars"></div>
    
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">
                <i class="fas fa-rocket"></i>
                Launch IO Research Station
            </div>
            <ul class="nav-links">
                <li><a href="#home" class="active"><i class="fas fa-home"></i> Mission Control</a></li>
                <li><a href="#research"><i class="fas fa-search"></i> Research Lab</a></li>
                <li><a href="#history"><i class="fas fa-history"></i> Data Archive</a></li>
                <li><a href="#reports"><i class="fas fa-chart-line"></i> Reports</a></li>
                <li><a href="#about"><i class="fas fa-info-circle"></i> About</a></li>
            </ul>
        </div>
    </nav>
    
    <!-- Main content -->
    <div class="main-content">
        <!-- Hero section -->
        <div class="hero-section">
            <h1 class="hero-title">🚀 SPACE RESEARCH STATION</h1>
            <p class="hero-subtitle">Powered by IO Intelligence • Exploring the Universe of Knowledge</p>
            
            <!-- Stats -->
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-number" id="totalResearch">0</div>
                    <div class="stat-label">Research Missions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="totalReports">0</div>
                    <div class="stat-label">Reports Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="timeSaved">0</div>
                    <div class="stat-label">Hours Saved</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">∞</div>
                    <div class="stat-label">Possibilities</div>
                </div>
            </div>
        </div>
        
        <!-- Main grid -->
        <div class="main-grid">
        
        <div class="grid">
            <div class="panel">
                <div class="api-status">✅ <strong>IO Intelligence Connected</strong> - Llama-3.3-70B-Instruct</div>
                <h2>🔍 Start Research</h2>
                <form id="researchForm">
                    <div class="form-group">
                        <label>Research Topic</label>
                        <input type="text" id="topic" placeholder="Enter research topic..." required>
                    </div>
                    <div class="form-group">
                        <label>Research Mode</label>
                        <select id="mode">
                            <option value="io_intelligence">🤖 IO Intelligence Research</option>
                            <option value="multi_topic">📊 Multi-Topic Analysis</option>
                            <option value="sentiment">😊 Sentiment Analysis</option>
                        </select>
                    </div>
                    <button type="submit" class="btn" id="startBtn">🚀 Start Research</button>
                </form>
                
                <div class="demo-topics">
                    <div class="demo-topic" onclick="setTopic('AI trends 2025')">🤖 AI Trends</div>
                    <div class="demo-topic" onclick="setTopic('blockchain supply chain')">⛓️ Blockchain</div>
                    <div class="demo-topic" onclick="setTopic('quantum computing')">⚛️ Quantum</div>
                    <div class="demo-topic" onclick="setTopic('ML healthcare')">🏥 ML Health</div>
                </div>
            </div>
            
            <div class="panel">
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('history')">📚 History</div>
                    <div class="tab" onclick="switchTab('reports')">📊 Reports</div>
                </div>
                
                <div id="historyTab" class="tab-content active">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <h3>Recent Searches</h3>
                        <button class="btn btn-danger" onclick="clearHistory()" style="width: auto; padding: 5px 10px;">🗑️ Clear</button>
                    </div>
                    <div id="historyList">Loading...</div>
                </div>
                
                <div id="reportsTab" class="tab-content">
                    <h3>📊 Generate Report</h3>
                    <div class="form-group">
                        <label>Report Title</label>
                        <input type="text" id="reportTitle" value="Research Report">
                    </div>
                    <div class="form-group">
                        <label>Report Type</label>
                        <select id="reportType">
                            <option value="comprehensive">📋 Comprehensive</option>
                            <option value="summary">📝 Summary</option>
                            <option value="comparison">⚖️ Comparison</option>
                        </select>
                    </div>
                    <div id="taskSelection">No completed tasks</div>
                    <button class="btn btn-success" onclick="generateReport()" id="generateBtn" disabled>📊 Generate</button>
                </div>
            </div>
        </div>
        
        <div class="progress" id="progressContainer">
            <h3>🔄 Research in Progress</h3>
            <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
            <div id="statusMessage">Initializing...</div>
        </div>
        
        <div class="results" id="resultsContainer">
            <h2>📊 Research Results</h2>
            <div id="resultsContent"></div>
        </div>
    </div>
    
    <script>
        let currentTaskId = null;
        let searchHistory = [];
        let selectedTasks = new Set();
        
        document.addEventListener('DOMContentLoaded', function() {
            loadSearchHistory();
            loadTaskSelection();
        });
        
        document.getElementById('researchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const topic = document.getElementById('topic').value;
            const mode = document.getElementById('mode').value;
            if (!topic.trim()) { alert('Please enter a research topic'); return; }
            await startResearch(topic, mode);
        });
        
        function setTopic(topic) { document.getElementById('topic').value = topic; }
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
            if (tabName === 'reports') loadTaskSelection();
        }
        
        async function startResearch(topic, mode) {
            const startBtn = document.getElementById('startBtn');
            const progressContainer = document.getElementById('progressContainer');
            const resultsContainer = document.getElementById('resultsContainer');
            
            startBtn.disabled = true;
            startBtn.textContent = '🔄 Starting...';
            progressContainer.style.display = 'block';
            resultsContainer.style.display = 'none';
            
            try {
                const response = await fetch('/api/research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic, mode })
                });
                const data = await response.json();
                currentTaskId = data.task_id;
                pollProgress();
            } catch (error) {
                alert('Failed to start research');
                resetUI();
            }
        }
        
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
                } else if (data.status === 'failed') {
                    alert('Research failed');
                    resetUI();
                } else {
                    setTimeout(pollProgress, 1000);
                }
            } catch (error) {
                setTimeout(pollProgress, 2000);
            }
        }
        
        function updateProgress(data) {
            document.getElementById('progressFill').style.width = data.progress + '%';
            document.getElementById('statusMessage').textContent = data.current_phase + ': ' + (data.message || 'Processing...');
        }
        
        async function showResults() {
            try {
                const response = await fetch(`/api/research/${currentTaskId}/result`);
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                alert('Failed to fetch results');
            }
            resetUI();
        }
        
        function displayResults(data) {
            const resultsContainer = document.getElementById('resultsContainer');
            const resultsContent = document.getElementById('resultsContent');
            let html = '';
            
            if (data.report && typeof data.report === 'object') {
                if (data.report.research_results) {
                    data.report.research_results.forEach(result => {
                        if (!result.error) {
                            html += `<div class="result-item"><h4>${result.topic}</h4><p>${result.summary}</p></div>`;
                        }
                    });
                }
                if (data.report.comprehensive_report && !data.report.comprehensive_report.error) {
                    html += `<div class="result-item"><h4>📊 Comprehensive Report</h4><p>${data.report.comprehensive_report.report_summary}</p></div>`;
                }
                if (data.report.summary) {
                    html += `<div class="result-item"><h4>${data.topic}</h4><p>${data.report.summary}</p></div>`;
                }
            } else {
                html = `<div class="result-item"><h4>Research Results</h4><p>${data.report}</p></div>`;
            }
            
            if (!html) html = '<div>No results to display</div>';
            resultsContent.innerHTML = html;
            resultsContainer.style.display = 'block';
        }
        
        function resetUI() {
            const startBtn = document.getElementById('startBtn');
            startBtn.disabled = false;
            startBtn.textContent = '🚀 Start Research';
            document.getElementById('progressContainer').style.display = 'none';
            currentTaskId = null;
        }
        
        async function loadSearchHistory() {
            try {
                const response = await fetch('/api/history');
                const data = await response.json();
                searchHistory = data.history;
                displaySearchHistory();
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }
        
        function displaySearchHistory() {
            const historyList = document.getElementById('historyList');
            if (searchHistory.length === 0) {
                historyList.innerHTML = '<div>No search history yet</div>';
                return;
            }
            let html = '';
            searchHistory.forEach(item => {
                const date = new Date(item.created_at).toLocaleDateString();
                html += `<div class="history-item"><h4>${item.topic}</h4><p><strong>Mode:</strong> ${item.mode} | <strong>Status:</strong> ${item.status}</p><p>${item.summary}</p><small>${date}</small><div class="history-actions"><button onclick="rerunResearch('${item.topic}', '${item.mode}')" style="background: #6c757d; color: white;">🔄 Rerun</button><button onclick="deleteHistoryItem('${item.task_id}')" style="background: #dc3545; color: white;">🗑️ Delete</button></div></div>`;
            });
            historyList.innerHTML = html;
        }
        
        async function clearHistory() {
            if (confirm('Clear all search history?')) {
                try {
                    await fetch('/api/history', { method: 'DELETE' });
                    searchHistory = [];
                    displaySearchHistory();
                    loadTaskSelection();
                } catch (error) {
                    console.error('Error clearing history:', error);
                }
            }
        }
        
        async function deleteHistoryItem(taskId) {
            try {
                await fetch(`/api/history/${taskId}`, { method: 'DELETE' });
                loadSearchHistory();
                loadTaskSelection();
            } catch (error) {
                console.error('Error deleting item:', error);
            }
        }
        
        function rerunResearch(topic, mode) {
            document.getElementById('topic').value = topic;
            document.getElementById('mode').value = mode;
            startResearch(topic, mode);
        }
        
        async function loadTaskSelection() {
            const taskSelection = document.getElementById('taskSelection');
            const generateBtn = document.getElementById('generateBtn');
            const completedTasks = searchHistory.filter(item => item.status === 'completed');
            
            if (completedTasks.length === 0) {
                taskSelection.innerHTML = '<div>No completed tasks available</div>';
                generateBtn.disabled = true;
                return;
            }
            
            let html = '<p>Select tasks for report:</p>';
            completedTasks.forEach(task => {
                const date = new Date(task.created_at).toLocaleDateString();
                html += `<div class="checkbox-group"><input type="checkbox" id="task_${task.task_id}" value="${task.task_id}" onchange="updateSelectedTasks()"><label for="task_${task.task_id}"><strong>${task.topic}</strong> (${task.mode}) - ${date}</label></div>`;
            });
            taskSelection.innerHTML = html;
            updateSelectedTasks();
        }
        
        function updateSelectedTasks() {
            selectedTasks.clear();
            document.querySelectorAll('#taskSelection input[type="checkbox"]:checked').forEach(checkbox => {
                selectedTasks.add(checkbox.value);
            });
            document.getElementById('generateBtn').disabled = selectedTasks.size === 0;
        }
        
        async function generateReport() {
            if (selectedTasks.size === 0) {
                alert('Please select at least one task');
                return;
            }
            const reportTitle = document.getElementById('reportTitle').value || 'Research Report';
            const reportType = document.getElementById('reportType').value;
            
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
            } catch (error) {
                alert('Failed to generate report');
            }
        }
    </script>
</body>
</html>
    """)

@app.post("/api/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    research_tasks[task_id] = {
        "id": task_id, "topic": request.topic, "mode": request.mode, "status": "starting",
        "progress": 0, "current_phase": "Initializing", "message": "Starting...", 
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
    return {"history": search_history}

@app.delete("/api/history")
async def clear_history():
    global search_history
    search_history = []
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
        "progress": 0, "current_phase": "Collecting data", "message": "Gathering data...", 
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
        research_tasks[task_id]["message"] = "Research completed!"
        research_tasks[task_id]["result"] = final_result
        
        # Add to history
        global search_history
        history_item = {"task_id": task_id, "topic": request.topic, "mode": request.mode, "status": "completed",
                       "created_at": research_tasks[task_id]["created_at"], "completed_at": datetime.now().isoformat(),
                       "summary": str(final_result["report"])[:200] + "..." if len(str(final_result["report"])) > 200 else str(final_result["report"])}
        search_history.insert(0, history_item)
        if len(search_history) > 50:
            search_history = search_history[:50]
        save_search_history()
        
    except Exception as e:
        research_tasks[task_id]["status"] = "failed"
        research_tasks[task_id]["message"] = f"Failed: {str(e)}"

async def execute_report_generation(report_id: str, request: ReportRequest):
    try:
        research_tasks[report_id]["status"] = "running"
        research_tasks[report_id]["progress"] = 50
        
        collected_data = []
        for task_id in request.task_ids:
            if task_id in research_tasks and research_tasks[task_id]["status"] == "completed":
                collected_data.append(research_tasks[task_id]["result"])
        
        # Generate simple report
        report_content = f"{request.report_title}\n\nGenerated from {len(collected_data)} research tasks:\n\n"
        for item in collected_data:
            report_content += f"• {item['topic']}: {str(item['report'])[:100]}...\n"
        
        final_result = {"task_id": report_id, "topic": request.report_title, "mode": "report_generation", 
                       "status": "completed", "report": report_content, "created_at": research_tasks[report_id]["created_at"], 
                       "completed_at": datetime.now().isoformat()}
        
        research_tasks[report_id]["status"] = "completed"
        research_tasks[report_id]["progress"] = 100
        research_tasks[report_id]["current_phase"] = "Completed"
        research_tasks[report_id]["message"] = "Report generated!"
        research_tasks[report_id]["result"] = final_result
        
        # Add to history
        global search_history
        history_item = {"task_id": report_id, "topic": request.report_title, "mode": "report_generation", "status": "completed",
                       "created_at": research_tasks[report_id]["created_at"], "completed_at": datetime.now().isoformat(),
                       "summary": f"Generated {request.report_type} report from {len(collected_data)} tasks"}
        search_history.insert(0, history_item)
        save_search_history()
        
    except Exception as e:
        research_tasks[report_id]["status"] = "failed"
        research_tasks[report_id]["message"] = f"Failed: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Launch IO Hackathon Web Interface...")
    print("🌐 Open your browser to: http://localhost:5000")
    print("🤖 Real IO Intelligence API Integration!")
    print("✨ Features: Search History + Report Generator")
    uvicorn.run(app, host="127.0.0.1", port=5000)