#!/usr/bin/env python3
"""
Mock IO Intelligence Client
Simulates the IO Intelligence API for demonstration purposes.
"""

import asyncio
import random
import time
from typing import Dict, List, Any

class MockIOIntelligenceClient:
    """Mock client that simulates IO Intelligence API responses."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "mock://api.intelligence.io"
        
    async def generate_text(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate text using mock AI responses."""
        
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Mock responses based on prompt content
        if "artificial intelligence" in prompt.lower():
            responses = [
                "Artificial intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, and problem-solving.",
                "AI encompasses machine learning, neural networks, and deep learning technologies that enable computers to process data and make decisions autonomously.",
                "Modern AI systems use algorithms to analyze patterns in data, enabling applications like natural language processing, computer vision, and predictive analytics."
            ]
        elif "summarize" in prompt.lower() or "summary" in prompt.lower():
            responses = [
                "This text discusses the importance of AI-powered summarization tools in processing large amounts of information efficiently across various industries.",
                "The content highlights how advanced AI models improve summarization by maintaining coherence and contextual relevance compared to traditional methods.",
                "The passage emphasizes the growing demand for intelligent summarization tools to enhance productivity and decision-making in the digital age."
            ]
        elif "blockchain" in prompt.lower():
            responses = [
                "Blockchain technology provides a decentralized, secure ledger system that enables transparent and immutable record-keeping across distributed networks.",
                "Key blockchain applications include cryptocurrency, smart contracts, supply chain management, and digital identity verification systems.",
                "Blockchain's consensus mechanisms ensure data integrity without requiring central authorities, revolutionizing trust in digital transactions."
            ]
        elif "machine learning" in prompt.lower():
            responses = [
                "Machine learning enables computers to learn and improve from experience without explicit programming, using algorithms to identify patterns in data.",
                "ML applications span healthcare diagnostics, financial fraud detection, recommendation systems, and autonomous vehicle navigation.",
                "Deep learning, a subset of ML, uses neural networks to process complex data like images, speech, and natural language."
            ]
        elif "healthcare" in prompt.lower():
            responses = [
                "AI in healthcare revolutionizes diagnosis, treatment planning, and drug discovery through advanced data analysis and pattern recognition.",
                "Machine learning models assist in medical imaging, predictive analytics for patient outcomes, and personalized treatment recommendations.",
                "Healthcare AI applications include robotic surgery, virtual health assistants, and real-time monitoring of patient vital signs."
            ]
        else:
            # Generic responses for other topics
            responses = [
                f"Based on the analysis of '{prompt[:50]}...', this topic involves complex interconnected factors that require careful consideration.",
                f"The subject matter presents interesting challenges and opportunities for innovation and development in the field.",
                f"Current research and developments in this area show promising results with potential for significant impact."
            ]
        
        return random.choice(responses)
    
    async def summarize_text(self, text: str, max_words: int = 50) -> str:
        """Summarize text using mock AI."""
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        # Generate mock summary based on text length and content
        if len(text) < 100:
            return "Brief text summarized: Key points extracted and condensed for clarity."
        
        # Analyze text for key topics
        topics = []
        if "artificial intelligence" in text.lower() or "ai" in text.lower():
            topics.append("AI technology")
        if "machine learning" in text.lower() or "ml" in text.lower():
            topics.append("machine learning")
        if "data" in text.lower():
            topics.append("data analysis")
        if "healthcare" in text.lower():
            topics.append("healthcare applications")
        if "blockchain" in text.lower():
            topics.append("blockchain technology")
        if "research" in text.lower():
            topics.append("research findings")
        
        if topics:
            topic_str = ", ".join(topics[:3])
            summaries = [
                f"This text discusses {topic_str} and their impact on modern technology and society.",
                f"Key insights on {topic_str} highlight significant developments and future potential.",
                f"The content explores {topic_str} with focus on practical applications and innovations."
            ]
        else:
            summaries = [
                "The text presents comprehensive analysis of complex topics with detailed explanations and insights.",
                "Key findings demonstrate significant developments in the field with practical implications.",
                "The content provides valuable information on current trends and future directions."
            ]
        
        return random.choice(summaries)
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        
        await asyncio.sleep(random.uniform(0.3, 1.0))
        
        # Simple sentiment analysis based on keywords
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "positive", "success", "innovation"]
        negative_words = ["bad", "terrible", "awful", "negative", "failure", "problem", "issue", "concern"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.6 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.6 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = random.uniform(0.7, 0.85)
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_score": positive_count / max(1, len(text.split()) / 10),
            "negative_score": negative_count / max(1, len(text.split()) / 10)
        }
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Mock keyword extraction
        common_keywords = {
            "artificial intelligence": ["AI", "machine learning", "neural networks", "algorithms", "automation"],
            "blockchain": ["cryptocurrency", "decentralized", "smart contracts", "consensus", "ledger"],
            "healthcare": ["medical", "diagnosis", "treatment", "patients", "clinical"],
            "technology": ["innovation", "digital", "software", "systems", "development"],
            "research": ["analysis", "study", "findings", "methodology", "results"]
        }
        
        text_lower = text.lower()
        extracted_keywords = []
        
        for topic, keywords in common_keywords.items():
            if topic in text_lower:
                extracted_keywords.extend(keywords[:3])
        
        # Add some generic keywords
        words = text.split()
        long_words = [word.strip('.,!?;:') for word in words if len(word) > 6]
        extracted_keywords.extend(random.sample(long_words, min(3, len(long_words))))
        
        return list(set(extracted_keywords))[:max_keywords]

# Test function
async def test_mock_client():
    """Test the mock client."""
    
    print("🧪 Testing Mock IO Intelligence Client")
    print("=" * 60)
    
    client = MockIOIntelligenceClient("mock-api-key")
    
    # Test text generation
    print("\n1️⃣ Testing text generation...")
    response = await client.generate_text("What is artificial intelligence?")
    print(f"Response: {response}")
    
    # Test summarization
    print("\n2️⃣ Testing summarization...")
    long_text = """
    Artificial intelligence represents one of the most significant technological advances of our time. 
    Machine learning algorithms can now process vast amounts of data to identify patterns and make 
    predictions with remarkable accuracy. From healthcare diagnostics to autonomous vehicles, 
    AI applications are transforming industries and improving human lives in countless ways.
    """
    summary = await client.summarize_text(long_text)
    print(f"Summary: {summary}")
    
    # Test sentiment analysis
    print("\n3️⃣ Testing sentiment analysis...")
    sentiment = await client.analyze_sentiment("This is an amazing breakthrough in technology!")
    print(f"Sentiment: {sentiment}")
    
    # Test keyword extraction
    print("\n4️⃣ Testing keyword extraction...")
    keywords = await client.extract_keywords(long_text)
    print(f"Keywords: {keywords}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_mock_client())