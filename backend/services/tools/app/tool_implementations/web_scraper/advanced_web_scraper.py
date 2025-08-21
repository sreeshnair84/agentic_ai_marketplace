"""
Advanced Web Scraper Tool Implementation
Intelligent web scraping with JavaScript rendering, rate limiting, and content extraction
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime, timedelta
import hashlib

# Web scraping libraries
import requests
from bs4 import BeautifulSoup, Comment
import lxml

# Browser automation
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Content processing
from readability import Document

# Data extraction
import pandas as pd

logger = logging.getLogger(__name__)

class AdvancedWebScraper:
    """
    Advanced web scraper with intelligent content extraction,
    JavaScript rendering, and rate limiting
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize web scraper with configuration"""
        self.config = config
        self.user_agent = config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.timeout = config.get("timeout", 30)
        self.delay_between_requests = config.get("delay_between_requests", 1.0)
        self.max_retries = config.get("max_retries", 3)
        self.respect_robots_txt = config.get("respect_robots_txt", True)
        self.javascript_enabled = config.get("javascript_enabled", False)
        self.extract_images = config.get("extract_images", False)
        self.extract_links = config.get("extract_links", True)
        self.follow_redirects = config.get("follow_redirects", True)
        self.max_pages = config.get("max_pages", 10)
        
        # Rate limiting
        self.request_history = {}
        self.domain_delays = {}
        
        # Browser driver for JavaScript rendering
        self.driver = None
        
        # Session for connection pooling
        self.session = None
        
        logger.info("Initialized Advanced Web Scraper")
    
    async def initialize(self):
        """Initialize web scraper components"""
        try:
            # Initialize aiohttp session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"User-Agent": self.user_agent}
            )
            
            # Initialize browser driver if JavaScript enabled
            if self.javascript_enabled:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(f"--user-agent={self.user_agent}")
                
                self.driver = webdriver.Chrome(options=chrome_options)
                
            logger.info("Web scraper initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize web scraper: {e}")
            raise
    
    async def scrape_url(self, url: str, extraction_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Scrape a single URL with intelligent content extraction
        
        Args:
            url: URL to scrape
            extraction_config: Configuration for content extraction
            
        Returns:
            Dictionary with scraped content
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return {
                    "status": "error",
                    "error": "Invalid URL format",
                    "url": url
                }
            
            # Check robots.txt if enabled
            if self.respect_robots_txt and not await self._can_fetch(url):
                return {
                    "status": "error",
                    "error": "Blocked by robots.txt",
                    "url": url
                }
            
            # Apply rate limiting
            await self._apply_rate_limiting(url)
            
            # Fetch content
            if self.javascript_enabled:
                content_data = await self._fetch_with_browser(url)
            else:
                content_data = await self._fetch_with_http(url)
            
            # Extract structured data
            extracted_data = await self._extract_content(content_data, extraction_config or {})
            
            return {
                "status": "success",
                "url": url,
                "content": extracted_data,
                "metadata": {
                    "scrape_time": datetime.now().isoformat(),
                    "content_length": len(content_data.get("html", "")),
                    "method": "browser" if self.javascript_enabled else "http"
                }
            }
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }
    
    async def scrape_multiple_urls(self, urls: List[str], extraction_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently with rate limiting
        
        Args:
            urls: List of URLs to scrape
            extraction_config: Configuration for content extraction
            
        Returns:
            List of scraping results
        """
        try:
            # Limit number of URLs
            if len(urls) > self.max_pages:
                urls = urls[:self.max_pages]
                logger.warning(f"Limited to {self.max_pages} URLs")
            
            # Create semaphore for concurrent requests
            semaphore = asyncio.Semaphore(self.config.get("max_concurrent_requests", 5))
            
            async def scrape_with_semaphore(url):
                async with semaphore:
                    return await self.scrape_url(url, extraction_config)
            
            # Execute concurrent scraping
            tasks = [scrape_with_semaphore(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "status": "error",
                        "error": str(result),
                        "url": urls[i]
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error scraping multiple URLs: {e}")
            return [{"status": "error", "error": str(e)}]
    
    async def crawl_website(self, start_url: str, crawl_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Crawl a website starting from a URL
        
        Args:
            start_url: Starting URL for crawling
            crawl_config: Configuration for crawling behavior
            
        Returns:
            Dictionary with crawl results
        """
        try:
            config = crawl_config or {}
            max_depth = config.get("max_depth", 2)
            same_domain_only = config.get("same_domain_only", True)
            url_patterns = config.get("url_patterns", [])
            exclude_patterns = config.get("exclude_patterns", [])
            
            # Initialize crawling state
            visited_urls = set()
            to_visit = [(start_url, 0)]  # (url, depth)
            crawl_results = []
            
            start_domain = urlparse(start_url).netloc
            
            while to_visit and len(visited_urls) < self.max_pages:
                current_url, depth = to_visit.pop(0)
                
                if current_url in visited_urls or depth > max_depth:
                    continue
                
                # Check domain restriction
                if same_domain_only and urlparse(current_url).netloc != start_domain:
                    continue
                
                # Check URL patterns
                if url_patterns and not any(re.search(pattern, current_url) for pattern in url_patterns):
                    continue
                
                if exclude_patterns and any(re.search(pattern, current_url) for pattern in exclude_patterns):
                    continue
                
                visited_urls.add(current_url)
                
                # Scrape current URL
                result = await self.scrape_url(current_url, config.get("extraction_config"))
                crawl_results.append(result)
                
                # Extract links for next level
                if result["status"] == "success" and depth < max_depth:
                    links = result["content"].get("links", [])
                    for link in links:
                        absolute_url = urljoin(current_url, link.get("href", ""))
                        if absolute_url not in visited_urls:
                            to_visit.append((absolute_url, depth + 1))
            
            return {
                "status": "success",
                "start_url": start_url,
                "crawl_results": crawl_results,
                "metadata": {
                    "pages_crawled": len(crawl_results),
                    "urls_discovered": len(visited_urls),
                    "crawl_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error crawling website: {e}")
            return {
                "status": "error",
                "error": str(e),
                "start_url": start_url
            }
    
    async def extract_structured_data(self, url: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data based on a custom schema
        
        Args:
            url: URL to scrape
            schema: Schema defining what data to extract
            
        Returns:
            Dictionary with extracted structured data
        """
        try:
            # Scrape the URL first
            scrape_result = await self.scrape_url(url)
            
            if scrape_result["status"] != "success":
                return scrape_result
            
            html_content = scrape_result["content"].get("raw_html", "")
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract data based on schema
            extracted_data = {}
            
            for field_name, field_config in schema.items():
                try:
                    value = await self._extract_field_value(soup, field_config)
                    extracted_data[field_name] = value
                except Exception as e:
                    logger.warning(f"Failed to extract field {field_name}: {e}")
                    extracted_data[field_name] = None
            
            return {
                "status": "success",
                "url": url,
                "structured_data": extracted_data,
                "metadata": scrape_result["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }
    
    async def scrape_table_data(self, url: str, table_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract table data from a webpage
        
        Args:
            url: URL containing tables
            table_config: Configuration for table extraction
            
        Returns:
            Dictionary with extracted table data
        """
        try:
            # Scrape the URL
            scrape_result = await self.scrape_url(url)
            
            if scrape_result["status"] != "success":
                return scrape_result
            
            html_content = scrape_result["content"].get("raw_html", "")
            
            # Extract tables using pandas
            try:
                tables = pd.read_html(html_content)
                
                # Convert tables to list of dictionaries
                table_data = []
                for i, table in enumerate(tables):
                    table_dict = {
                        "table_index": i,
                        "columns": table.columns.tolist(),
                        "data": table.to_dict('records'),
                        "shape": table.shape
                    }
                    table_data.append(table_dict)
                
                return {
                    "status": "success",
                    "url": url,
                    "tables": table_data,
                    "metadata": {
                        "table_count": len(table_data),
                        "total_rows": sum(table["shape"][0] for table in table_data)
                    }
                }
                
            except ValueError as e:
                return {
                    "status": "error",
                    "error": f"No tables found or parsing error: {str(e)}",
                    "url": url
                }
            
        except Exception as e:
            logger.error(f"Error scraping table data: {e}")
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }
    
    # Private methods
    
    async def _fetch_with_http(self, url: str) -> Dict[str, Any]:
        """Fetch content using HTTP client"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return {
                        "html": html_content,
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "url": str(response.url)
                    }
                else:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                    
        except Exception as e:
            logger.error(f"HTTP fetch failed for {url}: {e}")
            raise
    
    async def _fetch_with_browser(self, url: str) -> Dict[str, Any]:
        """Fetch content using browser automation"""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source
            html_content = self.driver.page_source
            
            return {
                "html": html_content,
                "status_code": 200,
                "url": self.driver.current_url,
                "title": self.driver.title
            }
            
        except Exception as e:
            logger.error(f"Browser fetch failed for {url}: {e}")
            raise
    
    async def _extract_content(self, content_data: Dict[str, Any], extraction_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured content from HTML"""
        try:
            html_content = content_data["html"]
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            extracted_data = {
                "raw_html": html_content,
                "title": self._extract_title(soup),
                "text": self._extract_text(soup),
                "meta_description": self._extract_meta_description(soup),
                "headings": self._extract_headings(soup),
            }
            
            # Optional extractions based on config
            if self.extract_links or extraction_config.get("extract_links", False):
                extracted_data["links"] = self._extract_links(soup, content_data.get("url", ""))
            
            if self.extract_images or extraction_config.get("extract_images", False):
                extracted_data["images"] = self._extract_images(soup, content_data.get("url", ""))
            
            # Extract main content using readability
            if extraction_config.get("extract_main_content", True):
                extracted_data["main_content"] = self._extract_main_content(html_content)
            
            # Extract structured data (JSON-LD, microdata)
            if extraction_config.get("extract_structured_data", False):
                extracted_data["structured_data"] = self._extract_structured_data(soup)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headings"""
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                "level": heading.name,
                "text": heading.get_text().strip()
            })
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append({
                "text": link.get_text().strip(),
                "href": href,
                "absolute_url": absolute_url
            })
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                absolute_url = urljoin(base_url, src)
                images.append({
                    "src": src,
                    "absolute_url": absolute_url,
                    "alt": img.get('alt', ''),
                    "title": img.get('title', '')
                })
        return images
    
    def _extract_main_content(self, html_content: str) -> str:
        """Extract main content using readability"""
        try:
            doc = Document(html_content)
            return doc.summary()
        except Exception as e:
            logger.warning(f"Readability extraction failed: {e}")
            return ""
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract JSON-LD and microdata"""
        structured_data = []
        
        # Extract JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append({
                    "type": "json-ld",
                    "data": data
                })
            except json.JSONDecodeError:
                continue
        
        return structured_data
    
    async def _extract_field_value(self, soup: BeautifulSoup, field_config: Dict[str, Any]) -> Any:
        """Extract field value based on configuration"""
        selector = field_config.get("selector")
        attribute = field_config.get("attribute", "text")
        data_type = field_config.get("type", "string")
        multiple = field_config.get("multiple", False)
        
        if not selector:
            return None
        
        # Find elements
        if multiple:
            elements = soup.select(selector)
        else:
            element = soup.select_one(selector)
            elements = [element] if element else []
        
        # Extract values
        values = []
        for element in elements:
            if not element:
                continue
                
            if attribute == "text":
                value = element.get_text().strip()
            else:
                value = element.get(attribute, "")
            
            # Type conversion
            if data_type == "integer":
                try:
                    value = int(re.search(r'\d+', value).group())
                except:
                    value = None
            elif data_type == "float":
                try:
                    value = float(re.search(r'\d+\.?\d*', value).group())
                except:
                    value = None
            
            values.append(value)
        
        return values if multiple else (values[0] if values else None)
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    async def _can_fetch(self, url: str) -> bool:
        """Check robots.txt permissions"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    # Simplified robots.txt parsing
                    return "Disallow: /" not in robots_content
                
            return True  # Allow if robots.txt not found
            
        except Exception:
            return True  # Allow on error
    
    async def _apply_rate_limiting(self, url: str):
        """Apply rate limiting based on domain"""
        domain = urlparse(url).netloc
        current_time = time.time()
        
        if domain in self.request_history:
            last_request_time = self.request_history[domain]
            time_since_last = current_time - last_request_time
            
            if time_since_last < self.delay_between_requests:
                sleep_time = self.delay_between_requests - time_since_last
                await asyncio.sleep(sleep_time)
        
        self.request_history[domain] = current_time
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            
            if self.driver:
                self.driver.quit()
                
            logger.info("Web scraper cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Tool configuration schema
TOOL_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "user_agent": {
            "type": "string",
            "default": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "description": "User agent string for requests"
        },
        "timeout": {
            "type": "integer",
            "minimum": 5,
            "maximum": 120,
            "default": 30,
            "description": "Request timeout in seconds"
        },
        "delay_between_requests": {
            "type": "number",
            "minimum": 0.1,
            "maximum": 10.0,
            "default": 1.0,
            "description": "Delay between requests in seconds"
        },
        "max_retries": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10,
            "default": 3,
            "description": "Maximum number of retries"
        },
        "respect_robots_txt": {
            "type": "boolean",
            "default": True,
            "description": "Whether to respect robots.txt"
        },
        "javascript_enabled": {
            "type": "boolean",
            "default": False,
            "description": "Enable JavaScript rendering with browser"
        },
        "extract_images": {
            "type": "boolean",
            "default": False,
            "description": "Extract image information"
        },
        "extract_links": {
            "type": "boolean",
            "default": True,
            "description": "Extract link information"
        },
        "max_pages": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 10,
            "description": "Maximum number of pages to scrape"
        },
        "max_concurrent_requests": {
            "type": "integer",
            "minimum": 1,
            "maximum": 20,
            "default": 5,
            "description": "Maximum concurrent requests"
        }
    }
}

# Tool input/output schemas
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["scrape_url", "scrape_multiple", "crawl_website", "extract_structured", "scrape_tables"],
            "description": "Operation to perform"
        },
        "url": {
            "type": "string",
            "description": "URL to scrape (for single URL operations)"
        },
        "urls": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of URLs to scrape (for multiple URL operations)"
        },
        "extraction_config": {
            "type": "object",
            "description": "Configuration for content extraction"
        },
        "crawl_config": {
            "type": "object",
            "description": "Configuration for website crawling"
        },
        "schema": {
            "type": "object",
            "description": "Schema for structured data extraction"
        },
        "table_config": {
            "type": "object",
            "description": "Configuration for table extraction"
        }
    },
    "required": ["operation"]
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["success", "error"]
        },
        "content": {
            "type": "object",
            "description": "Extracted content"
        },
        "results": {
            "type": "array",
            "description": "Results for multiple operations"
        },
        "metadata": {
            "type": "object",
            "description": "Scraping metadata"
        },
        "error": {
            "type": "string",
            "description": "Error message if status is error"
        }
    },
    "required": ["status"]
}
