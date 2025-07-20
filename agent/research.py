"""
Web Research Module

Handles web scraping, content extraction, and source gathering
for the research agent.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import feedparser
from utils.real_data_fetcher import RealDataFetcher
from utils.simple_real_fetcher import SimpleRealFetcher

class WebResearcher:
    """
    Web research component that searches and extracts content from various sources.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.session = None
        self.real_data_fetcher = RealDataFetcher(settings)
        self.headers = {
            'User-Agent': getattr(settings, 'user_agent', 'IOResearchAgent/1.0'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_and_extract(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for content and extract relevant information.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of extracted content dictionaries
        """
        
        if not self.session:
            async with self:
                return await self._perform_search(query, max_results)
        else:
            return await self._perform_search(query, max_results)
    
    async def _perform_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform the actual search and content extraction using REAL data."""
        
        print(f"🌐 Fetching REAL data for: {query}")
        
        # Check if we should force real data
        force_real = getattr(self.settings, 'force_real_data', False) or getattr(self.settings, 'use_real_data', False)
        
        if force_real:
            print("🔥 FORCING REAL DATA COLLECTION")
            
            # Use the simple real fetcher that actually works
            try:
                async with SimpleRealFetcher(self.settings) as simple_fetcher:
                    real_sources = await simple_fetcher.fetch_real_sources(query, max_results)
                    if real_sources:
                        print(f"✅ SUCCESS! Found {len(real_sources)} REAL sources with actual content")
                        return real_sources
            except Exception as e:
                print(f"⚠️ Simple real fetcher failed: {e}")
        
        # Try the enhanced real data fetcher
        try:
            real_sources = await self.real_data_fetcher.fetch_real_data(query, max_results)
            if real_sources:
                print(f"✅ Found {len(real_sources)} real sources")
                return real_sources
        except Exception as e:
            print(f"⚠️ Enhanced real data fetcher failed: {e}")
        
        # Fallback to basic search with real content extraction
        print("🔄 Falling back to basic search with real content extraction")
        sources = []
        
        # Search multiple sources
        search_tasks = [
            self._search_news_sources(query, max_results // 3),
            self._search_academic_sources(query, max_results // 3),
            self._search_general_web(query, max_results // 3),
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                sources.extend(result)
        
        print(f"📊 Collected {len(sources)} sources from fallback search")
        return sources[:max_results]
    
    async def _search_news_sources(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search news sources and RSS feeds."""
        
        sources = []
        
        # Popular news RSS feeds
        news_feeds = [
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://www.reuters.com/rssFeed/topNews',
            'https://techcrunch.com/feed/',
        ]
        
        for feed_url in news_feeds[:2]:  # Limit to avoid rate limiting
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:max_results//2]:
                            if self._is_relevant(entry.title + ' ' + entry.get('summary', ''), query):
                                article_content = await self._extract_article_content(entry.link)
                                if article_content:
                                    sources.append({
                                        'title': entry.title,
                                        'url': entry.link,
                                        'content': article_content,
                                        'source_type': 'news',
                                        'published': entry.get('published', ''),
                                        'summary': entry.get('summary', '')
                                    })
            except Exception as e:
                continue  # Skip failed feeds
        
        return sources
    
    async def _search_academic_sources(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search academic and research sources."""
        
        sources = []
        
        # Academic search engines and repositories
        academic_sources = [
            f"https://arxiv.org/search/?query={query.replace(' ', '+')}&searchtype=all",
            f"https://www.semanticscholar.org/search?q={query.replace(' ', '%20')}",
        ]
        
        for source_url in academic_sources[:1]:  # Limit requests
            try:
                async with self.session.get(source_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract paper titles and abstracts (simplified)
                        papers = soup.find_all(['article', 'div'], class_=re.compile(r'result|paper|abstract'))
                        
                        for paper in papers[:max_results]:
                            title_elem = paper.find(['h1', 'h2', 'h3', 'a'])
                            abstract_elem = paper.find(['p', 'div'], class_=re.compile(r'abstract|summary'))
                            
                            if title_elem and abstract_elem:
                                sources.append({
                                    'title': title_elem.get_text(strip=True),
                                    'url': source_url,
                                    'content': abstract_elem.get_text(strip=True),
                                    'source_type': 'academic',
                                    'published': '',
                                    'summary': abstract_elem.get_text(strip=True)[:200] + '...'
                                })
            except Exception as e:
                continue
        
        return sources
    
    async def _search_general_web(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search general web sources using real web scraping."""
        
        sources = []
        
        # Real web search using DuckDuckGo (no API key required)
        search_urls = await self._get_search_urls(query, max_results)
        
        # Extract content from each URL
        for url_data in search_urls:
            try:
                content = await self._extract_article_content(url_data['url'])
                if content and len(content) > 100:  # Only include substantial content
                    sources.append({
                        'title': url_data['title'],
                        'url': url_data['url'],
                        'content': content,
                        'source_type': 'web',
                        'published': url_data.get('published', ''),
                        'summary': content[:300] + '...' if len(content) > 300 else content
                    })
            except Exception as e:
                print(f"Failed to extract content from {url_data['url']}: {e}")
                continue
        
        return sources[:max_results]
    
    async def _get_search_urls(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Get search URLs using DuckDuckGo search."""
        
        search_results = []
        
        try:
            # Use DuckDuckGo search (no API key required)
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract search results
                    results = soup.find_all('a', class_='result__a')
                    
                    for result in results[:max_results]:
                        href = result.get('href')
                        title = result.get_text(strip=True)
                        
                        if href and title and not href.startswith('/'):
                            # Clean up DuckDuckGo redirect URLs
                            if 'uddg=' in href:
                                import urllib.parse
                                href = urllib.parse.unquote(href.split('uddg=')[1])
                            
                            search_results.append({
                                'title': title,
                                'url': href,
                                'published': ''
                            })
                    
                    # If DuckDuckGo doesn't work, try alternative sources
                    if not search_results:
                        search_results = await self._get_alternative_sources(query, max_results)
                        
        except Exception as e:
            print(f"Search failed: {e}")
            # Fallback to alternative sources
            search_results = await self._get_alternative_sources(query, max_results)
        
        return search_results
    
    async def _get_alternative_sources(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Get alternative sources when primary search fails."""
        
        # Curated list of reliable sources for different topics
        topic_sources = {
            'artificial intelligence': [
                'https://www.technologyreview.com/',
                'https://ai.googleblog.com/',
                'https://openai.com/blog/',
                'https://www.nature.com/subjects/machine-learning'
            ],
            'blockchain': [
                'https://cointelegraph.com/',
                'https://www.coindesk.com/',
                'https://ethereum.org/en/learn/',
                'https://bitcoin.org/en/'
            ],
            'climate change': [
                'https://www.ipcc.ch/',
                'https://climate.nasa.gov/',
                'https://www.noaa.gov/climate',
                'https://www.un.org/en/climatechange'
            ],
            'quantum computing': [
                'https://www.ibm.com/quantum-computing/',
                'https://quantumai.google/',
                'https://www.microsoft.com/en-us/quantum',
                'https://www.nature.com/subjects/quantum-physics'
            ],
            'renewable energy': [
                'https://www.irena.org/',
                'https://www.energy.gov/eere/renewable-energy',
                'https://www.iea.org/topics/renewables',
                'https://www.nrel.gov/'
            ]
        }
        
        # Find relevant sources based on query keywords
        relevant_sources = []
        query_lower = query.lower()
        
        for topic, sources in topic_sources.items():
            if any(keyword in query_lower for keyword in topic.split()):
                relevant_sources.extend(sources)
        
        # If no specific sources found, use general tech/news sources
        if not relevant_sources:
            relevant_sources = [
                'https://www.reuters.com/technology/',
                'https://techcrunch.com/',
                'https://www.wired.com/',
                'https://www.scientificamerican.com/',
                'https://www.bbc.com/news/technology',
                'https://www.theverge.com/'
            ]
        
        # Convert to search result format
        search_results = []
        for url in relevant_sources[:max_results]:
            # Try to get the page title
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        title = soup.find('title')
                        title_text = title.get_text(strip=True) if title else f"Article about {query}"
                        
                        search_results.append({
                            'title': title_text,
                            'url': url,
                            'published': ''
                        })
            except:
                # Fallback title
                search_results.append({
                    'title': f"Research source for {query}",
                    'url': url,
                    'published': ''
                })
        
        return search_results
    
    async def _extract_article_content(self, url: str) -> Optional[str]:
        """Extract main content from an article URL."""
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Try to find main content
                    content_selectors = [
                        'article',
                        '[role="main"]',
                        '.content',
                        '.article-body',
                        '.post-content',
                        'main'
                    ]
                    
                    content = None
                    for selector in content_selectors:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            content = content_elem.get_text(strip=True)
                            break
                    
                    # Fallback to body if no specific content found
                    if not content:
                        body = soup.find('body')
                        if body:
                            content = body.get_text(strip=True)
                    
                    # Clean and limit content
                    if content:
                        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                        return content[:5000]  # Limit to 5000 characters
                    
        except Exception as e:
            pass
        
        return None
    
    def _is_relevant(self, text: str, query: str) -> bool:
        """Check if text is relevant to the query."""
        
        text_lower = text.lower()
        query_words = query.lower().split()
        
        # Simple relevance check - at least 50% of query words should be present
        matches = sum(1 for word in query_words if word in text_lower)
        return matches >= len(query_words) * 0.5