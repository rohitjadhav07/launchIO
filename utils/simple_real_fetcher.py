"""
Simple Real Data Fetcher

A straightforward implementation that actually fetches real data from the web.
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import feedparser

class SimpleRealFetcher:
    """
    Simple but effective real data fetcher that actually works.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=15),
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_real_sources(self, query: str, max_sources: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch real sources from the web.
        
        Args:
            query: Search query
            max_sources: Maximum number of sources
            
        Returns:
            List of real sources with actual content
        """
        
        print(f"🌐 Fetching REAL data for: {query}")
        
        sources = []
        
        # Try multiple real data sources
        tasks = [
            self._fetch_wikipedia_content(query),
            self._fetch_arxiv_papers(query, 2),
            self._fetch_simple_web_content(query, 2),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                sources.extend(result)
            elif isinstance(result, dict):
                sources.append(result)
        
        # Filter and clean sources
        real_sources = []
        for source in sources:
            if source and source.get('content') and len(source.get('content', '')) > 100:
                real_sources.append(source)
        
        print(f"✅ Found {len(real_sources)} REAL sources with actual content")
        return real_sources[:max_sources]
    
    async def _fetch_wikipedia_content(self, query: str) -> Optional[Dict[str, Any]]:
        """Fetch real content from Wikipedia."""
        
        try:
            # Wikipedia API search
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'extract' in data and len(data['extract']) > 100:
                        return {
                            'title': f"Wikipedia: {data.get('title', query)}",
                            'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                            'content': data['extract'],
                            'source_type': 'encyclopedia',
                            'published': '',
                            'summary': data['extract'][:200] + '...',
                            'source_name': 'Wikipedia (Real)',
                            'is_real': True
                        }
        except Exception as e:
            print(f"Wikipedia fetch failed: {e}")
        
        return None
    
    async def _fetch_arxiv_papers(self, query: str, max_papers: int = 2) -> List[Dict[str, Any]]:
        """Fetch real academic papers from arXiv."""
        
        papers = []
        
        try:
            # arXiv API
            arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{quote_plus(query)}&start=0&max_results={max_papers}"
            
            async with self.session.get(arxiv_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse XML
                    from xml.etree import ElementTree as ET
                    root = ET.fromstring(content)
                    
                    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                        title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                        summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                        link_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                        published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                        
                        if title_elem is not None and summary_elem is not None:
                            title = title_elem.text.strip()
                            summary = summary_elem.text.strip()
                            url = link_elem.text if link_elem is not None else ''
                            published = published_elem.text if published_elem is not None else ''
                            
                            papers.append({
                                'title': f"arXiv: {title}",
                                'url': url,
                                'content': summary,
                                'source_type': 'academic',
                                'published': published,
                                'summary': summary[:200] + '...',
                                'source_name': 'arXiv (Real Academic)',
                                'is_real': True
                            })
                            
        except Exception as e:
            print(f"arXiv fetch failed: {e}")
        
        return papers
    
    async def _fetch_simple_web_content(self, query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        """Fetch simple web content from reliable sources."""
        
        sources = []
        
        # Reliable sources that usually work
        reliable_sources = [
            f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
            "https://www.bbc.com/news",
            "https://www.reuters.com/",
            "https://www.nature.com/",
            "https://www.scientificamerican.com/"
        ]
        
        for url in reliable_sources[:max_results]:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Get title
                        title_elem = soup.find('title')
                        title = title_elem.get_text(strip=True) if title_elem else f"Content about {query}"
                        
                        # Get content
                        content = self._extract_content(soup)
                        
                        if content and len(content) > 200:
                            sources.append({
                                'title': f"Web: {title[:100]}",
                                'url': url,
                                'content': content,
                                'source_type': 'web',
                                'published': '',
                                'summary': content[:200] + '...',
                                'source_name': 'Web Source (Real)',
                                'is_real': True
                            })
                            
            except Exception as e:
                print(f"Failed to fetch from {url}: {e}")
                continue
        
        return sources
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful content from HTML."""
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try different content selectors
        content_selectors = [
            'article',
            '[role="main"]',
            '.content',
            '.article-content',
            'main',
            'p'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text(strip=True) for elem in elements[:5]])
                if len(content) > 200:
                    break
        
        # Clean content
        if content:
            content = re.sub(r'\s+', ' ', content)
            return content[:2000]  # Limit length
        
        return ""

async def test_real_fetcher():
    """Test the real data fetcher."""
    
    from config.settings import Settings
    settings = Settings()
    
    async with SimpleRealFetcher(settings) as fetcher:
        sources = await fetcher.fetch_real_sources("artificial intelligence", 3)
        
        print(f"\n🎯 REAL DATA TEST RESULTS:")
        print(f"Found {len(sources)} real sources")
        
        for i, source in enumerate(sources, 1):
            print(f"\n{i}. {source['title']}")
            print(f"   URL: {source['url']}")
            print(f"   Type: {source['source_type']}")
            print(f"   Content: {source['content'][:150]}...")
            print(f"   Real: {source.get('is_real', False)}")

if __name__ == "__main__":
    asyncio.run(test_real_fetcher())