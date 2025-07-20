"""
Content Summarization Module

Uses IO Intelligence Models API to summarize and analyze content.
"""

from typing import Dict, Any, List
import json

class ContentSummarizer:
    """
    Content summarization component using IO Intelligence Models API.
    """
    
    def __init__(self, io_client):
        self.io_client = io_client
    
    async def summarize_content(self, content: str, title: str = "") -> str:
        """
        Summarize a piece of content using IO Intelligence.
        
        Args:
            content: The content to summarize
            title: Optional title for context
            
        Returns:
            Summarized content
        """
        
        prompt = f"""
        Summarize the following content in 2-3 concise paragraphs, focusing on key points and insights:
        
        Title: {title}
        
        Content:
        {content[:3000]}  # Limit content to avoid token limits
        
        Summary:
        """
        
        try:
            summary = await self.io_client.generate_text(
                prompt, 
                max_tokens=300,
                temperature=0.3
            )
            return summary.strip()
        except Exception as e:
            # Fallback summary if AI fails
            return self._create_fallback_summary(content, title)
    
    async def analyze_themes(self, combined_content: str) -> Dict[str, Any]:
        """
        Analyze themes and insights from combined content.
        
        Args:
            combined_content: Combined summaries from multiple sources
            
        Returns:
            Analysis with themes, insights, and sentiment
        """
        
        prompt = f"""
        Analyze the following content and extract:
        1. Main themes (3-5 key themes)
        2. Key insights (3-5 important insights)
        3. Overall sentiment (positive/negative/neutral)
        4. Confidence level (0.0-1.0)
        
        Content:
        {combined_content[:4000]}
        
        Respond in JSON format:
        {{
            "themes": ["theme1", "theme2", "theme3"],
            "insights": ["insight1", "insight2", "insight3"],
            "sentiment": "neutral",
            "confidence": 0.8
        }}
        """
        
        try:
            response = await self.io_client.generate_text(
                prompt,
                max_tokens=400,
                temperature=0.2
            )
            
            # Try to parse JSON response
            analysis = json.loads(response.strip())
            return analysis
            
        except Exception as e:
            # Fallback analysis
            return self._create_fallback_analysis(combined_content)
    
    async def extract_key_points(self, content: str) -> List[str]:
        """
        Extract key points from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of key points
        """
        
        prompt = f"""
        Extract 5-7 key points from the following content. 
        Each point should be a concise, important statement.
        
        Content:
        {content[:3000]}
        
        Key Points:
        1.
        """
        
        try:
            response = await self.io_client.generate_text(
                prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse numbered list
            points = []
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    point = line.split('.', 1)[-1].strip()
                    if point:
                        points.append(point)
            
            return points[:7]  # Limit to 7 points
            
        except Exception as e:
            return self._extract_fallback_points(content)
    
    def _create_fallback_summary(self, content: str, title: str) -> str:
        """Create a basic summary when AI fails."""
        
        # Simple extractive summary - take first few sentences
        sentences = content.split('. ')
        summary_sentences = sentences[:3]
        
        summary = '. '.join(summary_sentences)
        if not summary.endswith('.'):
            summary += '.'
        
        return f"Summary of '{title}': {summary}"
    
    def _create_fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Create basic analysis when AI fails."""
        
        # Simple keyword-based theme extraction
        common_words = ['technology', 'research', 'development', 'analysis', 
                       'study', 'data', 'system', 'method', 'result']
        
        themes = []
        content_lower = content.lower()
        for word in common_words:
            if word in content_lower:
                themes.append(word.title())
        
        return {
            'themes': themes[:5] if themes else ['General Analysis'],
            'insights': ['Content analysis completed', 'Multiple sources reviewed'],
            'sentiment': 'neutral',
            'confidence': 0.6
        }
    
    def _extract_fallback_points(self, content: str) -> List[str]:
        """Extract basic key points when AI fails."""
        
        # Simple sentence extraction
        sentences = content.split('. ')
        
        # Filter for informative sentences
        key_sentences = []
        for sentence in sentences[:10]:
            sentence = sentence.strip()
            if (len(sentence) > 20 and 
                any(word in sentence.lower() for word in ['important', 'key', 'significant', 'shows', 'indicates'])):
                key_sentences.append(sentence)
        
        return key_sentences[:5] if key_sentences else sentences[:3]