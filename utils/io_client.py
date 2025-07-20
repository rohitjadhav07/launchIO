"""
IO Intelligence API Client

Handles communication with IO Intelligence Models and Agents APIs.
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class IOIntelligenceClient:
    """
    Client for IO Intelligence APIs (Models and Agents).
    
    Provides methods for text generation, agent interactions,
    and streaming responses.
    """
    
    def __init__(self, settings):
        """
        Initialize the IO Intelligence client.
        
        Args:
            settings: Settings object with API configuration
        """
        self.settings = settings
        self.base_url = settings.io_base_url
        self.api_key = settings.io_api_key
        self.session = None
        
        # Default headers
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': settings.user_agent
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.settings.request_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def generate_text(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text using IO Intelligence Models API.
        
        Args:
            prompt: Input prompt for text generation
            model: Model to use (defaults to settings.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Generated text
        """
        
        # Prepare request data
        data = {
            'model': model or self.settings.default_model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens or self.settings.max_tokens,
            'temperature': temperature or self.settings.temperature,
            'stream': stream
        }
        
        if not self.session:
            async with self:
                return await self._make_generation_request(data, stream)
        else:
            return await self._make_generation_request(data, stream)
    
    async def _make_generation_request(self, data: Dict[str, Any], stream: bool) -> str:
        """Make the actual generation request."""
        
        url = f"{self.base_url}{self.settings.io_models_endpoint}"
        
        try:
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    if stream:
                        return await self._handle_streaming_response(response)
                    else:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed: {response.status} - {error_text}")
                    raise Exception(f"API request failed: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    async def _handle_streaming_response(self, response) -> str:
        """Handle streaming response from the API."""
        
        full_content = ""
        
        async for line in response.content:
            line = line.decode('utf-8').strip()
            
            if line.startswith('data: '):
                data_str = line[6:]  # Remove 'data: ' prefix
                
                if data_str == '[DONE]':
                    break
                
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content += content
                except json.JSONDecodeError:
                    continue
        
        return full_content
    
    async def create_agent(
        self, 
        name: str, 
        description: str, 
        instructions: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an agent using IO Intelligence Agents API.
        
        Args:
            name: Agent name
            description: Agent description
            instructions: Agent instructions
            model: Model to use for the agent
            
        Returns:
            Agent creation response
        """
        
        data = {
            'name': name,
            'description': description,
            'instructions': instructions,
            'model': model or self.settings.default_model
        }
        
        url = f"{self.base_url}{self.settings.io_agents_endpoint}"
        
        if not self.session:
            async with self:
                return await self._make_agent_request('POST', url, data)
        else:
            return await self._make_agent_request('POST', url, data)
    
    async def run_agent(
        self, 
        agent_id: str, 
        message: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run an agent with a message.
        
        Args:
            agent_id: ID of the agent to run
            message: Message to send to the agent
            thread_id: Optional thread ID for conversation continuity
            
        Returns:
            Agent response
        """
        
        data = {
            'message': message
        }
        
        if thread_id:
            data['thread_id'] = thread_id
        
        url = f"{self.base_url}{self.settings.io_agents_endpoint}/{agent_id}/run"
        
        if not self.session:
            async with self:
                return await self._make_agent_request('POST', url, data)
        else:
            return await self._make_agent_request('POST', url, data)
    
    async def _make_agent_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the Agents API."""
        
        try:
            if method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Agent API request failed: {response.status} - {error_text}")
                        raise Exception(f"Agent API request failed: {response.status}")
            else:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Agent API request failed: {response.status} - {error_text}")
                        raise Exception(f"Agent API request failed: {response.status}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error in agent request: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in agent request: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if the IO Intelligence API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        
        try:
            # Simple test request
            test_prompt = "Hello, this is a test."
            await self.generate_text(test_prompt, max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False