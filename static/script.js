// Multi-Agent Research System JavaScript

class ResearchApp {
    constructor() {
        this.ws = null;
        this.currentTaskId = null;
        this.agents = [];
        this.researchHistory = [];
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        await this.loadAgents();
        await this.loadResearchHistory();
        this.setupWebSocket();
    }
    
    setupEventListeners() {
        // Research form submission
        document.getElementById('research-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startResearch();
        });
        
        // Download report button
        document.getElementById('download-report').addEventListener('click', () => {
            this.downloadReport();
        });
        
        // Copy report button
        document.getElementById('copy-report').addEventListener('click', () => {
            this.copyReport();
        });
        
        // Mode change handler
        document.getElementById('mode').addEventListener('change', (e) => {
            this.updateModeDescription(e.target.value);
        });
    }
    
    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            const data = await response.json();
            this.agents = data.agents;
            this.renderAgents();
        } catch (error) {
            console.error('Failed to load agents:', error);
            this.showToast('Failed to load agents', 'error');
        }
    }
    
    renderAgents() {
        const agentsGrid = document.getElementById('agents-grid');
        agentsGrid.innerHTML = '';
        
        this.agents.forEach(agent => {
            const agentCard = document.createElement('div');
            agentCard.className = 'agent-card';
            agentCard.innerHTML = `
                <div class="agent-header">
                    <div class="agent-icon">
                        <i class="fas ${this.getAgentIcon(agent.role)}"></i>
                    </div>
                    <div>
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-status">${agent.status}</div>
                    </div>
                </div>
                <div class="agent-description">${agent.description}</div>
            `;
            agentsGrid.appendChild(agentCard);
        });
    }
    
    getAgentIcon(role) {
        const icons = {
            'research_coordinator': 'fa-clipboard-list',
            'web_researcher': 'fa-search',
            'data_analyst': 'fa-chart-bar',
            'content_summarizer': 'fa-brain',
            'fact_checker': 'fa-check-circle',
            'trend_analyzer': 'fa-chart-line',
            'report_writer': 'fa-file-alt',
            'quality_reviewer': 'fa-shield-alt'
        };
        return icons[role] || 'fa-robot';
    }
    
    setupWebSocket() {
        const clientId = this.generateClientId();
        const wsUrl = `ws://${window.location.host}/ws/${clientId}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.setupWebSocket(), 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'progress':
                this.updateProgress(data);
                break;
            case 'completed':
                this.handleResearchCompleted(data);
                break;
            case 'error':
                this.handleResearchError(data);
                break;
            case 'heartbeat':
                // Keep connection alive
                break;
        }
    }
    
    async startResearch() {
        const form = document.getElementById('research-form');
        const formData = new FormData(form);
        
        const request = {
            topic: formData.get('topic'),
            mode: formData.get('mode'),
            depth: formData.get('depth'),
            format: formData.get('format')
        };
        
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request)
            });
            
            if (!response.ok) {
                throw new Error('Failed to start research');
            }
            
            const data = await response.json();
            this.currentTaskId = data.task_id;
            
            this.showLoading(false);
            this.showProgressSection();
            this.hideResultsSection();
            
            // Update total research count
            this.updateResearchCount();
            
            this.showToast('Research started successfully!', 'success');
            
        } catch (error) {
            console.error('Failed to start research:', error);
            this.showLoading(false);
            this.showToast('Failed to start research', 'error');
        }
    }
    
    updateProgress(data) {
        if (data.task_id !== this.currentTaskId) return;
        
        // Update progress bar
        const progressFill = document.getElementById('progress-fill');
        const progressPercentage = document.getElementById('progress-percentage');
        const progressPhase = document.getElementById('progress-phase');
        const progressMessage = document.getElementById('progress-message');
        
        progressFill.style.width = `${data.progress}%`;
        progressPercentage.textContent = `${data.progress}%`;
        progressPhase.textContent = data.current_phase;
        progressMessage.textContent = data.message;
        
        // Update active agents
        if (data.agents_active && data.agents_active.length > 0) {
            const activeAgentsContainer = document.getElementById('active-agents');
            activeAgentsContainer.innerHTML = '';
            
            data.agents_active.forEach(agentName => {
                const agentTag = document.createElement('div');
                agentTag.className = 'active-agent';
                agentTag.textContent = agentName;
                activeAgentsContainer.appendChild(agentTag);
            });
            
            // Highlight active agents in the agents grid
            this.highlightActiveAgents(data.agents_active);
        }
    }
    
    highlightActiveAgents(activeAgentNames) {
        const agentCards = document.querySelectorAll('.agent-card');
        agentCards.forEach(card => {
            const agentName = card.querySelector('.agent-name').textContent;
            if (activeAgentNames.includes(agentName)) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        });
    }
    
    async handleResearchCompleted(data) {
        if (data.task_id !== this.currentTaskId) return;
        
        this.updateProgress(data);
        
        // Load and display results
        try {
            const response = await fetch(`/api/research/${data.task_id}/result`);
            const result = await response.json();
            
            this.displayResults(result);
            this.hideProgressSection();
            this.showResultsSection();
            
            // Clear active agent highlights
            document.querySelectorAll('.agent-card').forEach(card => {
                card.classList.remove('active');
            });
            
            // Update research history
            await this.loadResearchHistory();
            
            this.showToast('Research completed successfully!', 'success');
            
        } catch (error) {
            console.error('Failed to load research results:', error);
            this.showToast('Failed to load research results', 'error');
        }
    }
    
    handleResearchError(data) {
        if (data.task_id !== this.currentTaskId) return;
        
        this.hideProgressSection();
        this.showToast(`Research failed: ${data.message}`, 'error');
        
        // Clear active agent highlights
        document.querySelectorAll('.agent-card').forEach(card => {
            card.classList.remove('active');
        });
    }
    
    displayResults(result) {
        // Update metadata
        const metadataContainer = document.getElementById('results-metadata');
        metadataContainer.innerHTML = `
            <div class="metadata-item">
                <div class="metadata-label">Topic</div>
                <div class="metadata-value">${result.topic}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Mode</div>
                <div class="metadata-value">${result.mode}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Status</div>
                <div class="metadata-value">${result.status}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Completed</div>
                <div class="metadata-value">${new Date(result.completed_at).toLocaleString()}</div>
            </div>
        `;
        
        // Display report
        const reportContainer = document.getElementById('results-report');
        reportContainer.textContent = typeof result.report === 'string' ? result.report : JSON.stringify(result.report, null, 2);
        
        // Store current result for download/copy
        this.currentResult = result;
    }
    
    async loadResearchHistory() {
        try {
            const response = await fetch('/api/research');
            const data = await response.json();
            this.researchHistory = data.tasks;
            this.renderResearchHistory();
        } catch (error) {
            console.error('Failed to load research history:', error);
        }
    }
    
    renderResearchHistory() {
        const historyContainer = document.getElementById('history-container');
        
        if (this.researchHistory.length === 0) {
            historyContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>No research tasks yet. Start your first research above!</p>
                </div>
            `;
            return;
        }
        
        historyContainer.innerHTML = '';
        
        this.researchHistory.forEach(task => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="history-info">
                    <h4>${task.topic}</h4>
                    <div class="history-meta">
                        ${task.mode} • ${new Date(task.created_at).toLocaleString()}
                    </div>
                </div>
                <div class="history-status status-${task.status}">
                    ${task.status}
                </div>
            `;
            historyContainer.appendChild(historyItem);
        });
    }
    
    downloadReport() {
        if (!this.currentResult) return;
        
        const content = typeof this.currentResult.report === 'string' 
            ? this.currentResult.report 
            : JSON.stringify(this.currentResult.report, null, 2);
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `research-report-${this.currentResult.topic.replace(/\s+/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Report downloaded successfully!', 'success');
    }
    
    async copyReport() {
        if (!this.currentResult) return;
        
        const content = typeof this.currentResult.report === 'string' 
            ? this.currentResult.report 
            : JSON.stringify(this.currentResult.report, null, 2);
        
        try {
            await navigator.clipboard.writeText(content);
            this.showToast('Report copied to clipboard!', 'success');
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            this.showToast('Failed to copy to clipboard', 'error');
        }
    }
    
    updateModeDescription(mode) {
        // Could add mode-specific descriptions or UI changes here
        if (mode === 'multi-agent') {
            this.showToast('Multi-agent mode selected - 8 specialized agents will collaborate!', 'info');
        }
    }
    
    updateResearchCount() {
        const countElement = document.getElementById('total-research');
        if (countElement) {
            countElement.textContent = this.researchHistory.length + 1;
        }
    }
    
    showProgressSection() {
        document.getElementById('progress-section').style.display = 'block';
    }
    
    hideProgressSection() {
        document.getElementById('progress-section').style.display = 'none';
    }
    
    showResultsSection() {
        document.getElementById('results-section').style.display = 'block';
    }
    
    hideResultsSection() {
        document.getElementById('results-section').style.display = 'none';
    }
    
    showLoading(show) {
        document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas ${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
    
    getToastIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }
    
    generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }
}

// Global functions
function showAbout() {
    alert(`Multi-Agent Research System
    
Built for Launch IO Hackathon 2025
Powered by IO Intelligence APIs

Features:
• 8 Specialized AI Agents
• Autonomous Research & Analysis
• Professional Report Generation
• Real-time Progress Tracking
• Multiple Output Formats

This revolutionary system demonstrates the power of collaborative AI agents working together to solve complex research tasks.`);
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResearchApp();
});

// Add some sample topics for quick testing
const sampleTopics = [
    "artificial intelligence trends 2025",
    "blockchain technology applications",
    "quantum computing developments",
    "renewable energy innovations",
    "machine learning in healthcare",
    "sustainable agriculture methods",
    "cybersecurity best practices",
    "space exploration technologies"
];

// Add click handler for topic input to show suggestions
document.addEventListener('DOMContentLoaded', () => {
    const topicInput = document.getElementById('topic');
    
    topicInput.addEventListener('focus', () => {
        if (!topicInput.value) {
            const randomTopic = sampleTopics[Math.floor(Math.random() * sampleTopics.length)];
            topicInput.placeholder = `Try: "${randomTopic}"`;
        }
    });
});