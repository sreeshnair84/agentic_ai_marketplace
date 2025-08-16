"""
Standard tools implementation
"""

from typing import Dict, Any, Optional, List
import requests
import json
import logging
import subprocess
import os
from datetime import datetime
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import pandas as pd

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class WebTools:
    """Web-related tools"""
    
    @staticmethod
    async def fetch_url(url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Fetch content from a URL"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers or {}) as response:
                    content = await response.text()
                    
                    return {
                        "url": url,
                        "status_code": response.status,
                        "content": content,
                        "headers": dict(response.headers),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def scrape_webpage(url: str, selector: Optional[str] = None) -> Dict[str, Any]:
        """Scrape content from a webpage"""
        
        try:
            result = await WebTools.fetch_url(url)
            
            if "error" in result:
                return result
            
            soup = BeautifulSoup(result["content"], 'html.parser')
            
            if selector:
                elements = soup.select(selector)
                extracted_text = [elem.get_text(strip=True) for elem in elements]
            else:
                # Extract main text content
                for script in soup(["script", "style"]):
                    script.decompose()
                extracted_text = soup.get_text()
            
            return {
                "url": url,
                "selector": selector,
                "extracted_text": extracted_text,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping webpage {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def web_search(query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform web search (placeholder - integrate with search API)"""
        
        # This is a placeholder implementation
        # In production, integrate with Google Search API, Bing API, etc.
        
        return {
            "query": query,
            "num_results": num_results,
            "results": [
                {
                    "title": f"Sample result for: {query}",
                    "url": f"https://example.com/search?q={query}",
                    "snippet": f"This is a sample search result for the query: {query}"
                }
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "note": "This is a placeholder implementation. Integrate with actual search API."
        }


class FileTools:
    """File manipulation tools"""
    
    @staticmethod
    async def read_file(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read content from a file"""
        
        try:
            if not os.path.exists(file_path):
                return {
                    "file_path": file_path,
                    "error": "File not found",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            async with aiofiles.open(file_path, mode='r', encoding=encoding) as file:
                content = await file.read()
                
            return {
                "file_path": file_path,
                "content": content,
                "size": len(content),
                "encoding": encoding,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {
                "file_path": file_path,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def write_file(
        file_path: str, 
        content: str, 
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """Write content to a file"""
        
        try:
            # Create directories if needed
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with aiofiles.open(file_path, mode='w', encoding=encoding) as file:
                await file.write(content)
            
            return {
                "file_path": file_path,
                "size": len(content),
                "encoding": encoding,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return {
                "file_path": file_path,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def list_directory(directory_path: str) -> Dict[str, Any]:
        """List contents of a directory"""
        
        try:
            if not os.path.exists(directory_path):
                return {
                    "directory_path": directory_path,
                    "error": "Directory not found",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                item_stat = os.stat(item_path)
                
                items.append({
                    "name": item,
                    "path": item_path,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": item_stat.st_size,
                    "modified": datetime.fromtimestamp(item_stat.st_mtime).isoformat()
                })
            
            return {
                "directory_path": directory_path,
                "items": items,
                "count": len(items),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            return {
                "directory_path": directory_path,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class DataTools:
    """Data processing tools"""
    
    @staticmethod
    async def csv_to_json(csv_content: str) -> Dict[str, Any]:
        """Convert CSV content to JSON"""
        
        try:
            import io
            df = pd.read_csv(io.StringIO(csv_content))
            json_data = df.to_dict(orient='records')
            
            return {
                "rows": len(df),
                "columns": list(df.columns),
                "data": json_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error converting CSV to JSON: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def json_to_csv(json_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert JSON data to CSV"""
        
        try:
            df = pd.DataFrame(json_data)
            csv_content = df.to_csv(index=False)
            
            return {
                "rows": len(df),
                "columns": list(df.columns),
                "csv_content": csv_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error converting JSON to CSV: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def data_summary(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for data"""
        
        try:
            df = pd.DataFrame(data)
            
            summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "numeric_summary": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add numeric summary for numeric columns
            numeric_columns = df.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                summary["numeric_summary"] = df[numeric_columns].describe().to_dict()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating data summary: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class SystemTools:
    """System-related tools (use with caution)"""
    
    @staticmethod
    async def execute_command(
        command: str, 
        timeout: int = 30,
        allowed_commands: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute system command (restricted for security)"""
        
        settings = get_settings()
        
        # Security check - only allow if system tools are enabled
        if not settings.ENABLE_SYSTEM_TOOLS:
            return {
                "command": command,
                "error": "System tools are disabled for security",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Check against allowed commands
        if allowed_commands:
            command_name = command.split()[0] if command.split() else ""
            if command_name not in allowed_commands:
                return {
                    "command": command,
                    "error": f"Command '{command_name}' not in allowed list",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "error": f"Command timed out after {timeout} seconds",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return {
                "command": command,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
