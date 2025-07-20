# 🚀 Launch IO - Complete Research Platform Suite

A comprehensive research platform offering three different web applications, each with unique capabilities for AI-powered research and analysis.

## 📱 Available Applications

### 1. 🤖 Multi-Agent Web Application (`multi_agent_web.py`)
**Specialized Multi-Agent Research System**

- **8 Specialized AI Agents** working collaboratively
- **Agent Comparison & Analysis** with detailed breakdowns
- **Professional Report Generation** in multiple formats (HTML, Markdown, JSON)
- **Agent Performance Tracking** and consensus analysis
- **Downloadable Reports** with comprehensive insights

**Key Features:**
- Research Coordinator, Web Research Specialist, Data Analysis Expert
- Content Synthesizer, Fact Verification, Trend Analysis Expert
- Report Writer, Quality Assurance Reviewer
- Multi-agent consensus and divergent view analysis

### 2. 🌐 Web Complete Application (`web_complete.py`)
**Complete IO Intelligence Research Suite**

- **IO Intelligence Research** powered by Llama-3.3-70B-Instruct
- **Multi-Topic Analysis** for comprehensive topic exploration
- **Sentiment Analysis** with public opinion detection
- **Search History Management** with persistent storage
- **Advanced Report Generation** from multiple research sessions

**Key Features:**
- Space-themed UI with animated backgrounds
- Real-time progress tracking
- Mission archive with rerun capabilities
- Quick demo topics for instant research
- Statistics tracking (missions, reports, time saved)

### 3. 🚀 Complete Unified Application (`complete_unified_app.py`)
**All-in-One Research Platform**

- **Combined Multi-Agent + IO Intelligence** in one interface
- **All Research Modes** available from single application
- **Priority & Depth Settings** for customized research
- **Complete Mission Archive** with advanced management
- **Multi-Mission Report Generation** with data synthesis

**Key Features:**
- Unified interface accessing all capabilities
- Research modes: IO Intelligence, Multi-Agent, Multi-Topic, Sentiment
- Priority levels: Normal, High, Emergency
- Research depth: Quick, Standard, Detailed
- Comprehensive statistics and analytics

## 🛠️ Installation & Setup

### Prerequisites
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/launch-io-unified-platform.git
cd launch-io-unified-platform

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file with your API key:
```env
IO_API_KEY=your_io_intelligence_api_key_here
```

### Multi-Agent System Setup (Optional)
For full multi-agent functionality:
```bash
# The iointel directory should be included in the repository
# If not available, multi-agent features will be disabled gracefully
```

## 🚀 Running the Applications

### Option 1: Multi-Agent Web Application
```bash
python multi_agent_web.py
```
- **Access:** http://localhost:8000
- **Best for:** Detailed multi-agent analysis and professional reports
- **Features:** 8 AI agents, comparative analysis, downloadable reports

### Option 2: Web Complete Application  
```bash
python web_complete.py
```
- **Access:** http://localhost:8000
- **Best for:** IO Intelligence research with beautiful space-themed UI
- **Features:** Multi-topic analysis, sentiment analysis, mission history

### Option 3: Complete Unified Application
```bash
python complete_unified_app.py
```
- **Access:** http://localhost:8000
- **Best for:** All features in one platform with advanced controls
- **Features:** All research modes, priority settings, comprehensive reports

## 📊 Feature Comparison

| Feature | Multi-Agent Web | Web Complete | Unified App |
|---------|----------------|--------------|-------------|
| Multi-Agent System | ✅ Primary Focus | ❌ | ✅ Available |
| IO Intelligence | ✅ | ✅ Primary Focus | ✅ Available |
| Multi-Topic Analysis | ✅ | ✅ | ✅ |
| Sentiment Analysis | ❌ | ✅ | ✅ |
| Report Generation | ✅ Advanced | ✅ Basic | ✅ Advanced |
| Search History | ✅ | ✅ | ✅ |
| Priority Settings | ❌ | ❌ | ✅ |
| Research Depth Control | ❌ | ❌ | ✅ |
| Agent Status Tracking | ✅ Detailed | ❌ | ✅ Basic |
| Download Reports | ✅ Multiple Formats | ❌ | ✅ |
| UI Theme | Professional | Space Theme | Modern Professional |

## 🎯 Use Cases

### For Research Professionals
**→ Use Multi-Agent Web Application**
- Need detailed agent-by-agent analysis
- Require professional downloadable reports
- Want to compare different AI perspectives
- Need comprehensive fact verification

### For Quick Research & Exploration
**→ Use Web Complete Application**
- Beautiful, engaging interface
- Quick topic exploration
- Sentiment analysis needs
- Casual research sessions

### For Comprehensive Research Projects
**→ Use Complete Unified Application**
- Need all research modes in one place
- Require priority and depth control
- Managing multiple research projects
- Want advanced report generation

## 🔧 Configuration Options

### Research Modes Available
- **IO Intelligence:** Direct Llama-3.3-70B-Instruct research
- **Multi-Agent:** 8 specialized agents working together
- **Multi-Topic:** Comprehensive topic exploration
- **Sentiment:** Public opinion and sentiment analysis

### Priority Levels (Unified App Only)
- **Normal:** Standard processing
- **High:** Elevated priority
- **Emergency:** Highest priority processing

### Research Depth (Unified App Only)
- **Quick:** Fast overview (2 hours saved)
- **Standard:** Balanced analysis (4 hours saved)  
- **Detailed:** Comprehensive research (8 hours saved)

## 📁 Project Structure

```
launch-io-unified-platform/
├── multi_agent_web.py          # Multi-agent focused web app
├── web_complete.py             # IO Intelligence focused web app
├── complete_unified_app.py     # All-in-one unified platform
├── real_data_demo.py          # IO Intelligence researcher class
├── multi_agent_comparison.py   # Multi-agent system core
├── agent/                     # Agent system components
├── config/                    # Configuration files
├── iointel/                   # Multi-agent framework
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🌐 Deployment

### Local Development
```bash
# Choose your preferred application
python complete_unified_app.py    # Recommended for full features
python web_complete.py           # For IO Intelligence focus
python multi_agent_web.py        # For multi-agent focus
```

### Production Deployment

**Railway:**
```bash
railway login
railway init
railway up
```

**Render:**
- Connect GitHub repository
- Build: `pip install -r requirements.txt`
- Start: `python complete_unified_app.py`

**Heroku:**
```bash
echo "web: python complete_unified_app.py" > Procfile
heroku create your-app-name
git push heroku main
```

## 🔑 Environment Variables

Required for all applications:
```env
IO_API_KEY=your_io_intelligence_api_key
PORT=8000                    # Optional, defaults to 8000
```

## 📈 Statistics & Analytics

All applications track:
- Total research missions completed
- Reports generated
- Time saved through automation
- Success rates and performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with all three applications
5. Submit a pull request

## 📄 License

This project is part of the Launch IO Hackathon submission.

## 🆘 Support

For issues or questions:
1. Check the application logs
2. Verify your IO_API_KEY is set correctly
3. Ensure all dependencies are installed
4. Try different applications to isolate issues

## 🏆 Hackathon Submission

This repository contains three complete web applications demonstrating different approaches to AI-powered research:

1. **Multi-Agent Focus** - Showcasing collaborative AI agents
2. **IO Intelligence Focus** - Highlighting powerful single-model research
3. **Unified Platform** - Combining all capabilities in one interface

Each application is fully functional and can be deployed independently or together.

---

**🚀 Launch IO - Powering the Future of AI Research**