#!/usr/bin/env python3
"""
Launch IO Hackathon - Final Unified Research Platform
Complete application with all features in one place
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

# Import components
from real_data_demo import IOIntelligenceResearcher

app = FastAPI(title="🚀 Launch IO - Unified Research Platform", version="5.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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

# Models
class ResearchRequest(BaseModel):
    topic: str
    mode: str = "io_intelligence"
    priority: str = "normal"

class ReportRequest(BaseModel):
    task_ids: List[str]
    report_title: str = "Research Report"
    report_type: str = "comprehensive"# Main ro
ute with complete HTML
@app.get("/", response_class=HTMLResponse)
async def unified_app():
    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Launch IO - Unified Research Platform</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
            min-height: 100vh; color: #ffffff; overflow-x: hidden;
        }}
        
        /* Navigation */
        .navbar {{
            position: fixed; top: 0; width: 100%; background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(15px); border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 1000; padding: 1rem 0;
        }}
        .nav-container {{
            max-width: 1400px; margin: 0 auto; display: flex;
            justify-content: space-between; align-items: center; padding: 0 2rem;
        }}
        .logo {{
            display: flex; align-items: center; font-size: 1.5rem;
            font-weight: bold; color: #00d4ff; text-decoration: none;
        }}
        .logo i {{ margin-right: 0.5rem; animation: spin 10s linear infinite; }}
        @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
        
        .nav-links {{ display: flex; list-style: none; gap: 1rem; }}
        .nav-links a {{
            color: #ffffff; text-decoration: none; padding: 0.7rem 1.2rem;
            border-radius: 25px; transition: all 0.3s ease; display: flex;
            align-items: center; gap: 0.5rem; cursor: pointer;
        }}
        .nav-links a:hover, .nav-links a.active {{
            background: linear-gradient(45deg, #00d4ff, #ff6b6b);
            transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 212, 255, 0.3);
        }}
        
        /* Main content */
        .main-content {{ margin-top: 100px; padding: 2rem; position: relative; z-index: 10; }}
        .page-header {{ text-align: center; margin-bottom: 3rem; padding: 2rem 0; }}
        .page-title {{
            font-size: 3rem; font-weight: bold;
            background: linear-gradient(45deg, #00d4ff, #ff6b6b, #4ecdc4, #45b7d1);
            background-size: 400% 400%; -webkit-background-clip: text;
            -webkit-text-fill-color: transparent; animation: gradientShift 4s ease-in-out infinite;
            margin-bottom: 1rem;
        }}
        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        .page-subtitle {{ font-size: 1.2rem; color: #b0b0b0; margin-bottom: 2rem; }}
        
        /* Panels */
        .panel {{
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px;
            padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease; margin-bottom: 2rem;
        }}
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
        .form-input, .form-select {{
            width: 100%; padding: 1rem; background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 10px;
            color: #ffffff; font-size: 1rem; transition: all 0.3s ease;
        }}
        .form-input:focus, .form-select:focus {{
            outline: none; border-color: #00d4ff; box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            background: rgba(255, 255, 255, 0.15);
        }}
        .form-input::placeholder {{ color: #b0b0b0; }}
        
        /* Buttons */
        .btn {{
            background: linear-gradient(45deg, #00d4ff, #0099cc); color: white; border: none;
            padding: 1rem 2rem; border-radius: 25px; font-size: 1rem; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease; margin: 0.5rem 0;
            text-decoration: none; display: inline-block; text-align: center;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4); }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
        .btn-full {{ width: 100%; }}
        .btn-danger {{ background: linear-gradient(45deg, #ff6b6b, #ee5a52); }}
        .btn-success {{ background: linear-gradient(45deg, #4ecdc4, #44a08d); }}
        
        /* Stats cards */
        .stats-container {{ display: flex; justify-content: center; gap: 2rem; margin-bottom: 3rem; flex-wrap: wrap; }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px;
            padding: 1.5rem; text-align: center; min-width: 150px; transition: transform 0.3s ease;
        }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2); }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #00d4ff; }}
        .stat-label {{ color: #b0b0b0; font-size: 0.9rem; }}
        
        /* Feature cards */
        .feature-card {{
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px;
            padding: 2rem; text-align: center; transition: transform 0.3s ease;
        }}
        .feature-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2); }}
        .feature-icon {{ font-size: 3rem; color: #00d4ff; margin-bottom: 1rem; }}
        .feature-title {{ font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem; color: #ffffff; }}
        .feature-description {{ color: #b0b0b0; line-height: 1.6; }}
        
        /* Demo topics */
        .demo-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
        .demo-topic {{
            background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;
        }}
        .demo-topic:hover {{
            background: rgba(0, 212, 255, 0.2); transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
        }}
        
        /* Progress */
        .progress-container {{
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px;
            padding: 2rem; margin: 2rem auto; max-width: 800px; display: none;
        }}
        .progress-bar {{
            width: 100%; height: 25px; background: rgba(255, 255, 255, 0.1);
            border-radius: 15px; overflow: hidden; margin: 1.5rem 0;
        }}
        .progress-fill {{
            height: 100%; background: linear-gradient(90deg, #00d4ff, #4ecdc4, #ff6b6b);
            background-size: 200% 100%; width: 0%; transition: width 0.5s ease;
            animation: progressShine 2s linear infinite; border-radius: 15px;
        }}
        @keyframes progressShine {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
        
        /* Results */
        .results-container {{
            background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px;
            padding: 2rem; margin: 2rem auto; max-width: 1200px; display: none;
        }}
        .result-item {{
            background: rgba(255, 255, 255, 0.1); border-left: 4px solid #00d4ff;
            border-radius: 10px; padding: 1.5rem; margin: 1.5rem 0; transition: transform 0.3s ease;
        }}
        .result-item:hover {{ transform: translateX(5px); background: rgba(0, 212, 255, 0.1); }}
        .result-title {{ font-size: 1.3rem; font-weight: 600; color: #00d4ff; margin-bottom: 1rem; }}
        .result-summary {{ color: #e0e0e0; line-height: 1.6; margin-bottom: 1rem; }}
        
        /* Tabs */
        .tabs {{ display: flex; border-bottom: 2px solid rgba(255, 255, 255, 0.2); margin-bottom: 1.5rem; }}
        .tab {{
            padding: 1rem 1.5rem; cursor: pointer; border-bottom: 2px solid transparent;
            transition: all 0.3s ease; color: #b0b0b0;
        }}
        .tab.active {{ border-bottom-color: #00d4ff; color: #00d4ff; font-weight: 600; }}
        .tab:hover {{ color: #ffffff; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        /* History items */
        .history-item {{
            background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 1.5rem;
            margin: 1rem 0; border-left: 4px solid #00d4ff; transition: all 0.3s ease;
        }}
        .history-item:hover {{ background: rgba(0, 212, 255, 0.1); transform: translateX(5px); }}
        .history-actions {{ margin-top: 1rem; display: flex; gap: 0.5rem; }}
        .history-actions button {{
            padding: 0.5rem 1rem; border: none; border-radius: 20px;
            cursor: pointer; font-size: 0.8rem; transition: all 0.3s ease;
        }}
        
        /* Checkbox groups */
        .checkbox-group {{
            display: flex; align-items: center; margin: 1rem 0; padding: 0.5rem;
            border-radius: 10px; transition: background 0.3s ease;
        }}
        .checkbox-group:hover {{ background: rgba(255, 255, 255, 0.05); }}
        .checkbox-group input[type="checkbox"] {{ width: auto; margin-right: 1rem; transform: scale(1.2); }}
        
        /* Page content */
        .page-content {{ display: none; }}
        .page-content.active {{ display: block; }}
        
        /* API Status */
        .api-status {{
            background: linear-gradient(45deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1));
            border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 10px;
            padding: 1rem; margin-bottom: 1.5rem; display: flex; align-items: center;
        }}
        .api-status i {{ color: #4caf50; margin-right: 0.5rem; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        
        /* Notification */
        .notification {{
            position: fixed; top: 100px; right: 20px; background: rgba(0, 212, 255, 0.9);
            color: white; padding: 1rem 1.5rem; border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); transform: translateX(400px);
            transition: transform 0.3s ease; z-index: 1001;
        }}
        .notification.show {{ transform: translateX(0); }}
        
        /* Loading spinner */
        .loading-spinner {{
            display: inline-block; width: 20px; height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3); border-radius: 50%;
            border-top-color: #00d4ff; animation: spin 1s ease-in-out infinite;
        }}
        
        /* Footer */
        .footer {{
            background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 2rem 0 1rem;
            margin-top: 5rem; text-align: center; color: #666;
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">
                <i class="fas fa-rocket"></i>
                Launch IO Unified Platform
            </div>
            <ul class="nav-links">
                <li><a onclick="showPage('home')" class="active"><i class="fas fa-home"></i> Home</a></li>
                <li><a onclick="showPage('research')"><i class="fas fa-search"></i> Research</a></li>
                <li><a onclick="showPage('history')"><i class="fas fa-history"></i> History</a></li>
                <li><a onclick="showPage('reports')"><i class="fas fa-chart-line"></i> Reports</a></li>
                <li><a onclick="showPage('analytics')"><i class="fas fa-analytics"></i> Analytics</a></li>
                <li><a onclick="showPage('about')"><i class="fas fa-info-circle"></i> About</a></li>
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
                        8 specialized AI agents: Research Coordinator, Web Researcher, Data Analyst, and more.
                    </div>
                    <button onclick="showPage('research')" class="btn btn-full" style="margin-top: 1rem;">Launch Agents</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-history"></i></div>
                    <div class="feature-title">Mission Archive</div>
                    <div class="feature-description">
                        Complete history of research missions with rerun, analyze, and export capabilities.
                    </div>
                    <button onclick="showPage('history')" class="btn btn-full" style="margin-top: 1rem;">View History</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="feature-title">Advanced Reports</div>
                    <div class="feature-description">
                        Generate comprehensive reports from multiple research missions with analytics.
                    </div>
                    <button onclick="showPage('reports')" class="btn btn-full" style="margin-top: 1rem;">Generate Reports</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-analytics"></i></div>
                    <div class="feature-title">Performance Analytics</div>
                    <div class="feature-description">
                        Deep insights into research patterns, success rates, and productivity metrics.
                    </div>
                    <button onclick="showPage('analytics')" class="btn btn-full" style="margin-top: 1rem;">View Analytics</button>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-satellite"></i></div>
                    <div class="feature-title">Real-Time Processing</div>
                    <div class="feature-description">
                        Live progress tracking with real-time updates and instant notifications.
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
               div>ion"></ficat"notition" id=ficaotis="ndiv clas
    <on -->- Notificati  <!-
  oter>
       </fo🚀</p>
 . ties of AI possibiliitethe infinoring  Expltform. Plaarchseied Renif ULaunch IO; 2025 opy       <p>&c
 ">footer"ooter class=->
    <f- Footer -  <!- 
  >
      </div>
 ent"></divresultsCont id="      <divs</h2>
   Resultission"></i> M-telescopes fai class="fa  <h2><     
 r">tsContaineid="resulner" contaiults-class="res   <div ->
 r -ts containeResul   <!-- 
    
 
    </div>>    </div   ...</div>
 rametersission pazing mitialit: 600;">Innt-weigh00d4ff; fo #="color:" styleeatusMessag="stiv id     <d
         </div>     >
     ill"></div"progressFill" id=ogress-fss="pr <div cla      >
         ss-bar""progreclass=<div           h3>
  n Progress</ Mission i/i>-dish"><litetel-sa="fas fa3><i class<h         ">
   center;: "text-aligne=iv styl    <d  ">
  nerssContai"progrener" id=contaiogress- class="pr<div    iner -->
nta coProgress    <!-- >
    
>
    </div  </divv>
          </di          </div>
           /div>
          <             /p>
d Edition<.0 Unifie0;">5.0e0e0e: #e="color   <p styl                >
     /h4on<rsirem;">Veom: 0.5-bottff; margincolor: #00d4"le=    <h4 sty           
         enter;">lign: c="text-aiv style<d             >
       </div              >
      on</pnovatiowered In>AI-P0;"e0elor: #e0co <p style="                  4>
     /hme<Them;">ttom: 0.5rergin-bof; ma#00d4flor: "co  <h4 style=              >
        ;"ntern: cet-aligstyle="tex       <div            
    </div>         >
         </p2025O Hackathon >Launch I0e0e0;"lor: #ee="co  <p styl             >
         ">Event</h40.5rem;bottom: n-4ff; margi #00d="color:le    <h4 sty                >
    : center;"ext-aligntyle="t  <div s           ">
       id-3grs="   <div clas      v>
       /di <          >
     mation</h2hon Infor">Hackattle-tiass="panel2 cl   <h             >
    "></irophyfas fa-tlass="  <i c       
           eader">anel-hclass="p  <div            anel">
    class="p    <div      
             div>
     </      </div>
              </div>
                  
      </ul>                    
    </li>nerationort Ge• Custom Repi>       <l                   /li>
  s<ent Analysili>• Sentim         <            >
       alysis</linal An-Dimensio<li>• Multi                           >
 arch</lisence Re IntelligeIOi>•           <l                 m;">
 e: 0.9reont-sizght: 1.8; fb0; line-heilor: #b0b0tyle="coul s    <                 
   >odes:</h4Research M">🎯 m: 1rem;n-bottogi0d4ff; mar="color: #0<h4 style                   >
     ": 2rem;argin-top style="m  <div                        
       
       iv>         </d         </p>
   Platformelligencent Iong> IOration:</stregntstrong>API Ip><  <                 p>
     stence</-based persi JSONg>onrage:</strong>Data Sto     <p><str                on</p>
   e applicatiag single-pifiedong> Uncture:</strrchitestrong>A   <p><                 
    aScript</p>CSS3 + Jav+ odern HTML5 g> M</strontend:>Fronp><strong     <        
           sing</p> procesasyncPI with g> FastAend:</stronrong>Back    <p><st                 p>
   ct</tru-Ins-3.3-70Bamastrong> Ll:</Model<strong>AI   <p>                    ">
  .6;ne-height: 1e0; li#e0e0e="color: <div styl                 div>
             </          /h2>
fications<ecical Sp">Technitlenel-tipaclass="2        <h               </i>
  ">as fa-cogs"f <i class=                       ">
nel-headers="pa clas     <div          l">
     class="pane  <div                   
   
            </div>         iv>
    </d             l>
       </u                     >
   racking</liss Ttime Progre<li>• Real-                       
     /li>ard<bos Dashnce Analytici>• Performa      <l                      ry</li>
sion Histote Mis<li>• Comple                           </li>
 Generationt epor Advanced R <li>•                           
i>ysis</lesearch Anall RDimensionai>• Multi- <l                     i>
      n</legratioce API Intelligen IntIO>• Real <li                            1.8;">
height: 0b0b0; line- #b="color:l style          <u            
  </h4>ey Features: Kem;">🚀ottom: 1r; margin-b0d4ffr: #0yle="colo<h4 st                      em;">
  -top: 2rle="margin    <div sty             </p>
                       ns.
licatioesearch apptical rith pracnologies wtechAI ge utting-ed c                   f 
     otion integrathestrates orm demon platfn 2025, thishoackatIO Hh ncthe Lau for      Built                    1rem;">
gin-bottom:6; maright: 1.ine-he0e0e0; lr: #ele="colo   <p sty               /p>
             <      hts.
   sigand inanalysis sive mprehencoo provide abilities tcaph esearc        r                ated 
phisticith sogence API wIO Intelli of e power thm combinestforh pla researcunified  This                    ">
   em;: 1rrgin-bottom6; maht: 1.-heig0e0e0; line #eyle="color:      <p st    
            </div>            
      h2> Overview</">Platform-titleel class="pan  <h2                 
     "></i>ircle fa-info-css="fas <i cla                
       l-header">s="pane  <div clas                ">
  "panel <div class=              ">
 -2class="grid     <div    
             </div>
               </p>
formarch Plat Rese - Unifiedckathonnch IO Hae">Lau-subtitllass="page    <p c          >
  ATFORM</h1PLℹ️ ABOUT itle">ge-tpa1 class="  <h       ">
       erpage-headss="v cla       <di    >
 nt"ge-conteass="paclt" age-abouv id="p      <dige -->
   Paut<!-- Abo              
 
 v>      </di
  >div</         iv>
           </d          </div>
           
         </div>                  er
    n Mast🎯 Missio                        ;">
    .5rem 0; margin: 0: 10pxdius; border-ra, 0.1) 255, 255a(255,ound: rgbkgrrem; bac"padding: 1 style= <div                iv>
       </d                      er
  lorata Exp    📊 D             
           rem 0;">rgin: 0.5px; madius: 10ra border-.1); 055, 255, rgba(255, 2 background:ng: 1rem;ddie="pa<div styl                       
 iv>     </d                 r
  eeearch Pion       🚀 Res                     rem 0;">
gin: 0.5px; mar 10r-radius:0.1); borde5, 255, a(255, 25ound: rgbkgr: 1rem; bacngpaddidiv style="     <               
         </div>             eted
      Complission 🥇 First M                       0;">
     0.5rem ; margin: adius: 10px-r; border 255, 0.1)5, 255,(25round: rgbakg1rem; bac"padding:  style=iv<d                     
   <div>          
          >       </div            h2>
 evements</hie">Acl-titlass="pane     <h2 cl                  y"></i>
 s fa-trophs="faas <i cl                     r">
  -headepanelv class=" <di                 nel">
  ="padiv class      <              
       /div>
               <iv>
           </d          >
     div          </            </div>
                        
      </div> 5px;">dius:border-radth: 20%; ht: 100%; wiheigf6b6b; und: #fackgro style="b        <div                       
 ">adius: 5px;r-rbordeght: 10px; ; hei55,0.1),255,2d: rgba(255ounle="backgrdiv sty    <                   v>
             </di                   /span>
 0%<  <span>2                         pan>
     t</s💫 Sentimen  <span>                              ">
5rem;ttom: 0.boeen; margin-pace-betwnt: stify-conteusay: flex; jle="displ sty       <div                 0;">
    rgin: 1rem v style="ma       <di             >
    </div                    iv>
          </d                   div>
   5px;"></der-radius:  35%; bor width:ht: 100%;c4; heig4ecdd: #ckgrounstyle="ba       <div                        
  5px;">adius: x; border-rheight: 10p.1); ,055,2255d: rgba(255,rountyle="backg <div s                         div>
  </                     >
       5%</span    <span>3                     an>
       -Topic</span>🌌 Multi     <sp                        ">
    0.5rem;gin-bottom:etween; marce-btent: spay-conustiflay: flex; jsp style="di      <div                 
      0;">argin: 1rem"mdiv style=           <          v>
         </di                      </div>
                   >
     5px;"></divs: border-radiu; : 45%dth: 100%; wiff; height0d4nd: #0"backgrouiv style=    <d                          ;">
  : 5pxadiusrder-rbo 10px; height:,0.1); 55,255,255ba(2round: rgkgtyle="bac <div s                    iv>
            </d                       pan>
pan>45%</s        <s                     span>
   elligence</ Intan>🤖 IO       <sp              
           ;">tom: 0.5rem-botn; marginbetweepace-: sntent-co justify: flex;"display <div style=                       ">
     1rem 0;argin:style="m  <div                  ">
     ;ing: 2rempaddiv style="     <d              </div>
                     2>
</hionstributrch Mode Di>Reseale"titnel-class="pa      <h2              ></i>
     pie"-chart-as fai class="f       <          
       er">anel-headiv class="p     <d            ">
   anel class="p     <div           2">
grid-s="div clas   <        
          >
      </div         </div>
              y</div>
  ficiencbel">Eftat-la"sass=<div cl             
       5%</div>r">9bestat-num class="     <div              ">
 tat-card class="s  <div              iv>
        </d       div>
 des</>AI Mol"bet-la"staiv class=          <d   
       ">8</div>number"stat-=lass  <div c                ">
  ardss="stat-c<div cla               /div>
           <>
      divTime (min)</abel">Avg s="stat-lclas   <div            div>
      ">2.5</rtat-numbeass="s<div cl                    
">"stat-cardclass=  <div              </div>
           
      div>e</Success Ratt-label">"staclass=  <div            >
       ">100%</divmber-nus="stat <div clas            ">
       tat-card"siv class=          <d    ">
  ontainer"stats-cs= <div clas       
               </div>
          </p>
   tsnsigh and Ince Metrics">Performatitlesubage-s="pp clas    <       
     h1>RD</ DASHBOA📈 ANALYTICSe-title">pags="   <h1 clas          >
   e-header""pagdiv class=     <">
       age-content" class="p-analytics"pageiv id=
        <dcs Page -->lytiAna!--  
        <         </div>
v>
          </di       iv>
         </d   /div>
                <             </div>
          
           </div>                   >
        irst!</pions fmissarch ese some r;">Complete9remnt-size: 0.style="fop      <                          >
 le</pions availabted misscomple    <p>No                      i>
       ></rem;": 1argin-bottom: 2rem; mzent-sile="fo-list" styoard fa-clipbasclass="f       <i                        666;">
  color: #m; g: 2re paddinn: center;text-aligstyle="div       <            
          ction">eletaskS="v id         <di             </h4>
  ions: Missesearchlect R: 1rem;">Seottomff; margin-bor: #00d4 style="col   <h4                 
     <div>               
                       
     </div>           n>
       </butto                 
     te Report Generai>a-magic"></s f"fa<i class=                      ed>
      tn" disabl"generateBd=eport()" ierateRk="genull" onclicss btn-fn-succe bttn"b=ton classbut         <               
                >
        iv       </d      
           t>ec     </sel                     
  y</option>ative Stud>⚖️ Comparrison"ue="compavaloption      <                     ion>
      Summary</opttive ⚡ Execury">e="summaon valu <opti                             n>
  ysis</optioensive Anal">🌌 Comprehivemprehensvalue="cotion      <op                   
        ">m-select"fore" class=rtTyprepoct id="  <sele                          /label>
t Type<">📊 Reporlabelass="form- <label cl                          
 group">"form-s=  <div clas                          
              iv>
      </d                      
  port">arch Reensive Resepreh="Comaluerm-input" v="foclasse" tTitl id="reporext"ype="t <input t                         
  el>itle</labort TRep📋 bel">"form-lalass=    <label c                >
        "roup="form-gdiv class      <             div>
          <        ">
       d-2class="gri     <div         
             >
      div   </            ator</h2>
 ort Genertom Rep>Cus-title"s="panelh2 clas   <            ></i>
     file-alt"as fa-="f<i class              >
      er"eadpanel-hclass="iv          <d   >
    s="panel"lasv c    <di
                      </div>
 
         </p>ionsh Missesearcorts from Rehensive Repe Compr">Generatge-subtitles="pa     <p clas          OR</h1>
  GENERAT>📊 REPORT"ge-titleass="pa    <h1 cl          ">
  adere-heclass="pagdiv          <
   content">s="page-" clasortspage-rep<div id="     >
   -- Page - Reports     <!- 
   
            </div>     </div>
 
         v>    </di    >
             </div              
 !</p>e it hereon to serch missit reseayour firslete ;">Compemze: 0.9rt-si="fonle  <p sty                  
    >/pe yet<ns in archiv<p>No missio                     /i>
   ><: 1rem;"rgin-bottom 4rem; masize:t-onstyle="flite" s fa-satelfass="    <i cla                ">
    r: #666;colo3rem; padding: : center; "text-aligntyle=     <div s           >
    st""historyLi   <div id=           
             v>
         </di         tton>
     </bu               
   lear Archivei> Ctrash"></s fa-ass="fa cl   <i                     ()">
torylearHisclick="conn-danger" ass="btn bt cl  <button               </div>
                    ry</h2>
   tosearch His-title">Reelss="pan   <h2 cla                     </i>
-database">s fa"fa<i class=                 ">
       tom: 0;argin-botyle="msteader" anel-h class="p       <div             2rem;">
ttom: argin-boter; mms: cen-itetween; align: space-betentustify-conflex; jlay: style="disp <div                "panel">
=div class  <        
              </div>
  
          sions</p>esearch Mis of Ristory>Complete Hle"ubtitpage-sass="p cl    <    
        /h1>ARCHIVE<">📚 MISSION "page-title <h1 class=        
       e-header">pag=" <div class           content">
ge-s="pa clastory"hisd="page-      <div i -->
  ry PageHisto<!-- 
                  </div>
 /div>
            </div>
      <                  </div>
            
     ></div                    >
    /pations<nt notificstaith in tracking wem;">Live.9rt-size: 0 fon0b0b0;="color: #bp style          <           >
       gress</h4Time Prom;">📊 Real-: 0.5reottom; margin-bd4ffor: #00yle="col      <h4 st                     m 0;">
 rgin: 1res: 10px; ma-radiu5); border5, 0.0, 255, 25ba(255d: rggrounback 1rem; ="padding: <div style                        
                      div>
       </                  lysis</p>
l anationad emoentiment andvanced s 0.9rem;">Aze:0; font-sib0b"color: #b0e=styl   <p                   
       nalysis</h4>entiment A;">💫 S0.5rem-bottom: d4ff; margin#00e="color: 4 styl  <h                        ;">
  em 0argin: 1rx; mius: 10p-rad.05); border255, 255, 055, (2: rgba background: 1rem;ngdi"padv style=di   <               
                                </div>
                 
     ></pdimensionss multiple sis acroslysive anahen">Compreem;.9rize: 00b0; font-s0b"color: #ble=<p sty                   >
         </h4 Analysisti-Topicrem;">🌌 Mulottom: 0.5in-bf; marg0d4fr: #0yle="colo4 st     <h                      
 m 0;">in: 1remargpx; 10s: r-radiu5); borde55, 0.0 255, 25,nd: rgba(25em; backgrou"padding: 1r=style<div                             
                    </div>
                    ct</p>
    0B-Instrua-3.3-7ng Llam usi researchl-time AIm;">Reaze: 0.9re font-sib0;b0b0color: #p style="      <                    ce</h4>
  igenntellIO I🤖 ;">.5remottom: 0margin-b0d4ff; ="color: #0 <h4 style                 
          ">m 0;ren: 1x; margi0pus: 1adi; border-r 0.05)55,255, 255, 2a(gbound: rbackgrding: 1rem; "paddiv style=          <            ">
  y: 1rem;"space-v style=   <di                
             
              </div>            </h2>
  turestform Fea">Plapanel-titles="las       <h2 c              i>
   cogs"></s fa-fa"   <i class=                 r">
    anel-heade class="p   <div                 anel">
v class="p <di          
     anel -->atures P!-- Fe       <              
   >
            </div          /div>
        <               </div>
              
         lthcare ML Hea           🏥            ">
     care')lthrning heaine leaic('machetTop"sclick=topic" onss="demo-v cla      <di            >
            </div          e
         Futurkchain ⛓️ Bloc                          re')">
 ogy futuhnolchain tecc('blockk="setTopiclicc" onmo-topiclass="de  <div                  
     iv>  </d            
           Appstum⚛️ Quan                           >
 ons')"plicatiputing ap comtumanic('qusetTopk="" onclicopic"demo-tss=  <div cla                     div>
 </               
         ds 2025AI Tren         🤖                    )">
5'202ds enligence tral intelic('artificitTopk="se" onclicopico-tclass="dem     <div              d">
      -gridemo"ss=  <div cla                  
                    m>
   </for                 </button>
              
           Missionearch> Launch Res/iocket"><as fa-r"flass=      <i c                  >
    tartBtn"" id="sbtn btn-fulls="clas"submit"  type=     <button                        
                  iv>
 </d                     t>
       </selec                     on>
   </opti Protocolmergencynt">🔴 Egeue="urn valio        <opt                   on>
     y</optirit>🟡 High Prioigh" value="h    <option                     n>
       ty</optiorioriandard Pl">🟢 Ste="normaoption valu           <                  lect">
   s="form-seity" clast id="prior  <selec                          l>
ority</labesion Priabel">⚡ Mism-lfor"class=    <label                     oup">
    s="form-gras  <div cl                     
                      /div>
     <                 ct>
     le      </se                      ption>
ysis</oAnal💫 Sentiment timent">e="senalution v    <op                    
        s</option>ysialal Animension-D🌌 Multiopic">"multi_talue= voption <                        
       rch</option>seaence ReO Intelligce">🤖 Ieno_intellig"in value=tio<op                             lect">
   form-se class=""mode"lect id=    <se                    bel>
    /lach Mode<">🛸 Resear"form-labellass=l c  <labe                          group">
s="form-<div clas                     
                          </div>
                    d>
     reui.." reqch mission.r researEnter youceholder="" plainput"form-" class=opicxt" id="ttenput type="    <i                      >
  belrget</lach Tal">🎯 Researrm-labess="fo  <label cla                       
   orm-group">v class="fdi       <         >
        archForm"="rese id <form                
             
              </div>            
    truct Ready.3-70B-Inslama-3ong> - Line</strence Onl>IO Intelligtrong         <s           /i>
    ish"><tellite-da-sas f"faass=i cl           <     >
        us"at"api-st <div class=                  
                
          </div>          
     2>er</hent Control C">Mission-title"panelclass=        <h2            
     /i>tellite"><sa fa-lass="fasi c <             
          ">eradanel-heiv class="p        <d           ">
 ="panelv class<di        
        >el -- Control Pan!-- Research           <">
     ="grid-2<div class            
  
          v>   </di     
    ch</p>ce ResearigenO Intelltem + It Sysenti-Agtitle">Mul"page-subclass=        <p         h1>
LABORATORY</SEARCH tle">🔬 RE"page-ti= <h1 class