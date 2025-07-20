"""
Real Data Fetcher

Enhanced web scraping and data collection for real research data.
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class RealDataFetcher:
    """
    Advanced data fetcher that collects real information from multiple sources.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_real_data(self, query: str, max_sources: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch real data from multiple sources.
        
        Args:
            query: Search query
            max_sources: Maximum number of sources to fetch
            
        Returns:
            List of real data sources with content
        """
        
        if not self.session:
            async with self:
                return await self._fetch_data_sources(query, max_sources)
        else:
            return await self._fetch_data_sources(query, max_sources)
    
    async def _fetch_data_sources(self, query: str, max_sources: int) -> List[Dict[str, Any]]:
        """Fetch data from multiple source types."""
        
        # Create tasks for different source types
        tasks = [
            self._fetch_news_data(query, max_sources // 4),
            self._fetch_academic_data(query, max_sources // 4),
            self._fetch_wikipedia_data(query, max_sources // 4),
            self._fetch_specialized_sources(query, max_sources // 4),
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all results
        all_sources = []
        for result in results:
            if isinstance(result, list):
                all_sources.extend(result)
        
        # Remove duplicates and rank by relevance
        unique_sources = self._remove_duplicates(all_sources)
        ranked_sources = self._rank_by_relevance(unique_sources, query)
        
        return ranked_sources[:max_sources]
    
    async def _fetch_news_data(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch real news data from RSS feeds and news sites."""
        
        sources = []
        
        # Major news RSS feeds
        news_feeds = [
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://www.reuters.com/rssFeed/topNews',
            'https://feeds.npr.org/1001/rss.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        ]
        
        for feed_url in news_feeds[:3]:  # Limit to avoid overwhelming
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse RSS feed
                        import feedparser
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:max_results]:
                            # Check relevance
                            title_summary = f"{entry.title} {entry.get('summary', '')}"
                            if self._is_relevant_to_query(title_summary, query):
                                
                                # Extract full article content
                                article_content = await self._extract_full_content(entry.link)
                                
                                if article_content:
                                    sources.append({
                                        'title': entry.title,
                                        'url': entry.link,
                                        'content': article_content,
                                        'source_type': 'news',
                                        'published': entry.get('published', ''),
                                        'summary': entry.get('summary', '')[:300],
                                        'source_name': feed.feed.get('title', 'News Source'),
                                        'relevance_score': self._calculate_relevance(title_summary, query)
                                    })
                                    
                                    if len(sources) >= max_results:
                                        break
                        
            except Exception as e:
                print(f"Failed to fetch from {feed_url}: {e}")
                continue
        
        return sources
    
    async def _fetch_academic_data(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch real academic data from research repositories."""
        
        sources = []
        
        # Try arXiv for academic papers
        try:
            arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{quote_plus(query)}&start=0&max_results={max_results}"
            
            async with self.session.get(arxiv_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse arXiv XML response
                    from xml.etree import ElementTree as ET
                    root = ET.fromstring(content)
                    
                    # Extract entries
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
                            
                            sources.append({
                                'title': title,
                                'url': url,
                                'content': summary,
                                'source_type': 'academic',
                                'published': published,
                                'summary': summary[:300],
                                'source_name': 'arXiv',
                                'relevance_score': self._calculate_relevance(f"{title} {summary}", query)
                            })
                            
        except Exception as e:
            print(f"Failed to fetch arXiv data: {e}")
        
        return sources
    
    async def _fetch_wikipedia_data(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch real data from Wikipedia."""
        
        sources = []
        
        try:
            # Wikipedia search API
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'extract' in data and len(data['extract']) > 100:
                        sources.append({
                            'title': data.get('title', query),
                            'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                            'content': data['extract'],
                            'source_type': 'encyclopedia',
                            'published': '',
                            'summary': data['extract'][:300],
                            'source_name': 'Wikipedia',
                            'relevance_score': self._calculate_relevance(data['extract'], query)
                        })
            
            # Also try Wikipedia search for related articles
            search_api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(query)}&format=json&srlimit={max_results}"
            
            async with self.session.get(search_api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for result in data.get('query', {}).get('search', [])[:max_results-1]:
                        page_title = result['title']
                        
                        # Get page summary
                        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(page_title)}"
                        
                        try:
                            async with self.session.get(summary_url) as summary_response:
                                if summary_response.status == 200:
                                    summary_data = await summary_response.json()
                                    
                                    if 'extract' in summary_data and len(summary_data['extract']) > 100:
                                        sources.append({
                                            'title': summary_data.get('title', page_title),
                                            'url': summary_data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                                            'content': summary_data['extract'],
                                            'source_type': 'encyclopedia',
                                            'published': '',
                                            'summary': summary_data['extract'][:300],
                                            'source_name': 'Wikipedia',
                                            'relevance_score': self._calculate_relevance(summary_data['extract'], query)
                                        })
                        except:
                            continue
                            
        except Exception as e:
            print(f"Failed to fetch Wikipedia data: {e}")
        
        return sources
    
    async def _fetch_specialized_sources(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch data from specialized sources based on query topic."""
        
        sources = []
        query_lower = query.lower()
        
        # Define specialized sources for different topics
        specialized_sources = {
            'technology': [
                'https://techcrunch.com/feed/',
                'https://www.theverge.com/rss/index.xml',
                'https://arstechnica.com/feed/',
            ],
            'ai': [
                'https://www.technologyreview.com/feed/',
                'https://venturebeat.com/feed/',
            ],
            'blockchain': [
                'https://cointelegraph.com/rss',
                'https://www.coindesk.com/arc/outboundfeeds/rss/',
            ],
            'climate': [
                'https://www.climatecentral.org/feed',
                'https://insideclimatenews.org/feed/',
            ],
            'health': [
                'https://www.healthline.com/rss',
                'https://www.medicalnewstoday.com/rss',
            ]
        }
        
        # Find relevant specialized sources
        relevant_feeds = []
        for topic, feeds in specialized_sources.items():
            if topic in query_lower or any(word in query_lower for word in topic.split()):
                relevant_feeds.extend(feeds)
        
        # If no specific feeds found, use general tech feeds
        if not relevant_feeds:
            relevant_feeds = specialized_sources['technology']
        
        # Fetch from specialized sources
        for feed_url in relevant_feeds[:2]:  # Limit to avoid overwhelming
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        import feedparser
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:max_results]:
                            title_summary = f"{entry.title} {entry.get('summary', '')}"
                            if self._is_relevant_to_query(title_summary, query):
                                
                                article_content = await self._extract_full_content(entry.link)
                                
                                if article_content:
                                    sources.append({
                                        'title': entry.title,
                                        'url': entry.link,
                                        'content': article_content,
                                        'source_type': 'specialized',
                                        'published': entry.get('published', ''),
                                        'summary': entry.get('summary', '')[:300],
                                        'source_name': feed.feed.get('title', 'Specialized Source'),
                                        'relevance_score': self._calculate_relevance(title_summary, query)
                                    })
                                    
                                    if len(sources) >= max_results:
                                        break
                        
            except Exception as e:
                print(f"Failed to fetch from specialized source {feed_url}: {e}")
                continue
        
        return sources
    
    async def _extract_full_content(self, url: str) -> Optional[str]:
        """Extract full article content from URL."""
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                        element.decompose()
                    
                    # Try multiple content selectors
                    content_selectors = [
                        'article',
                        '[role="main"]',
                        '.article-content',
                        '.post-content',
                        '.entry-content',
                        '.content',
                        'main',
                        '.article-body',
                        '.story-body'
                    ]
                    
                    content = None
                    for selector in content_selectors:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            content = content_elem.get_text(separator=' ', strip=True)
                            if len(content) > 200:  # Only use if substantial content
                                break
                    
                    # Fallback to body content
                    if not content or len(content) < 200:
                        body = soup.find('body')
                        if body:
                            content = body.get_text(separator=' ', strip=True)
                    
                    # Clean and limit content
                    if content:
                        # Remove excessive whitespace
                        content = re.sub(r'\s+', ' ', content)
                        # Remove common boilerplate text
                        content = re.sub(r'(Subscribe|Sign up|Newsletter|Cookie|Privacy Policy|Terms of Service).*?(?=\.|$)', '', content, flags=re.IGNORECASE)
                        # Limit length
                        return content[:8000]  # Increased limit for better content
                    
        except Exception as e:
            print(f"Failed to extract content from {url}: {e}")
        
        return None
    
    def _is_relevant_to_query(self, text: str, query: str) -> bool:
        """Check if text is relevant to the search query."""
        
        text_lower = text.lower()
        query_words = query.lower().split()
        
        # Calculate relevance score
        matches = sum(1 for word in query_words if word in text_lower)
        relevance_ratio = matches / len(query_words)
        
        # Also check for partial matches and synonyms
        partial_matches = sum(1 for word in query_words 
                            if any(word in text_word for text_word in text_lower.split()))
        
        return relevance_ratio >= 0.3 or partial_matches >= len(query_words) * 0.5
    
    def _calculate_relevance(self, text: str, query: str) -> float:
        """Calculate relevance score between text and query."""
        
        text_lower = text.lower()
        query_words = query.lower().split()
        
        # Exact matches
        exact_matches = sum(1 for word in query_words if word in text_lower)
        
        # Partial matches
        partial_matches = sum(1 for word in query_words 
                            if any(word in text_word for text_word in text_lower.split()))
        
        # Calculate score
        exact_score = exact_matches / len(query_words)
        partial_score = partial_matches / len(query_words) * 0.5
        
        return min(exact_score + partial_score, 1.0)
    
    def _remove_duplicates(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on URL and title similarity."""
        
        seen_urls = set()
        seen_titles = set()
        unique_sources = []
        
        for source in sources:
            url = source.get('url', '')
            title = source.get('title', '').lower()
            
            # Check for URL duplicates
            if url and url in seen_urls:
                continue
            
            # Check for title similarity (simple approach)
            title_words = set(title.split())
            is_similar = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                if len(title_words & seen_words) / max(len(title_words), len(seen_words)) > 0.7:
                    is_similar = True
                    break
            
            if not is_similar:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_sources.append(source)
        
        return unique_sources
    
    def _rank_by_relevance(self, sources: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank sources by relevance score."""
        
        # Sort by relevance score (highest first)
        return sorted(sources, key=lambda x: x.get('relevance_score', 0), reverse=True)