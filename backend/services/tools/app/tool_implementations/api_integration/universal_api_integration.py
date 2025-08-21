"""
Universal API Integration Tool Implementation
Flexible API client with authentication, transformation, and monitoring
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
from urllib.parse import urlencode, urlparse
import jwt

# Data transformation
import jmespath
import jsonpath_ng

# OAuth and authentication
import requests_oauthlib

logger = logging.getLogger(__name__)

class UniversalAPIIntegration:
    """
    Universal API integration tool with support for multiple authentication methods,
    data transformation, rate limiting, and monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize API integration with configuration"""
        self.config = config
        self.base_url = config.get("base_url", "")
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.rate_limit = config.get("rate_limit", 100)  # requests per minute
        self.rate_limit_window = 60  # seconds
        
        # Authentication configuration
        self.auth_config = config.get("authentication", {})
        self.auth_type = self.auth_config.get("type", "none")
        
        # Default headers
        self.default_headers = config.get("headers", {})
        
        # Session for connection pooling
        self.session = None
        
        # Rate limiting tracking
        self.request_times = []
        
        # Cache for responses
        self.response_cache = {}
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes
        
        logger.info(f"Initialized API Integration for {self.base_url}")
    
    async def initialize(self):
        """Initialize API client"""
        try:
            # Create aiohttp session with default configuration
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.default_headers
            )
            
            # Test authentication if configured
            if self.auth_type != "none":
                await self._test_authentication()
            
            logger.info("API integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize API integration: {e}")
            raise
    
    async def make_request(self, 
                          method: str, 
                          endpoint: str, 
                          data: Dict[str, Any] = None,
                          params: Dict[str, Any] = None,
                          headers: Dict[str, str] = None,
                          transform_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an API request with authentication, retries, and transformation
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to base_url)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            transform_config: Data transformation configuration
            
        Returns:
            Dictionary with response data and metadata
        """
        try:
            # Construct full URL
            url = self._build_url(endpoint)
            
            # Apply rate limiting
            await self._apply_rate_limiting()
            
            # Prepare headers with authentication
            request_headers = await self._prepare_headers(headers or {})
            
            # Check cache for GET requests
            if method.upper() == "GET":
                cache_key = self._generate_cache_key(url, params)
                cached_response = self._get_cached_response(cache_key)
                if cached_response:
                    return cached_response
            
            # Make request with retries
            response_data = await self._make_request_with_retries(
                method, url, data, params, request_headers
            )
            
            # Transform response if configured
            if transform_config:
                response_data["data"] = await self._transform_response(
                    response_data["data"], transform_config
                )
            
            # Cache successful GET responses
            if method.upper() == "GET" and response_data["status_code"] == 200:
                cache_key = self._generate_cache_key(url, params)
                self._cache_response(cache_key, response_data)
            
            return {
                "status": "success",
                "method": method,
                "url": url,
                "response": response_data,
                "metadata": {
                    "request_time": datetime.now().isoformat(),
                    "response_time": response_data.get("response_time"),
                    "cached": False
                }
            }
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "method": method,
                "endpoint": endpoint
            }
    
    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple API requests concurrently
        
        Args:
            requests: List of request configurations
            
        Returns:
            List of response results
        """
        try:
            # Limit concurrent requests
            max_concurrent = self.config.get("max_concurrent_requests", 10)
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def make_single_request(request_config):
                async with semaphore:
                    return await self.make_request(**request_config)
            
            # Execute requests concurrently
            tasks = [make_single_request(req) for req in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "status": "error",
                        "error": str(result),
                        "request_index": i
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch requests failed: {e}")
            return [{"status": "error", "error": str(e)}]
    
    async def paginated_request(self, 
                               method: str, 
                               endpoint: str,
                               pagination_config: Dict[str, Any],
                               **kwargs) -> Dict[str, Any]:
        """
        Handle paginated API responses
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            pagination_config: Pagination configuration
            **kwargs: Additional request parameters
            
        Returns:
            Dictionary with all paginated results
        """
        try:
            all_data = []
            pagination_type = pagination_config.get("type", "page")
            max_pages = pagination_config.get("max_pages", 10)
            page_param = pagination_config.get("page_param", "page")
            size_param = pagination_config.get("size_param", "limit")
            page_size = pagination_config.get("page_size", 100)
            
            current_page = pagination_config.get("start_page", 1)
            
            while current_page <= max_pages:
                # Prepare pagination parameters
                params = kwargs.get("params", {}).copy()
                
                if pagination_type == "page":
                    params[page_param] = current_page
                    params[size_param] = page_size
                elif pagination_type == "offset":
                    params["offset"] = (current_page - 1) * page_size
                    params["limit"] = page_size
                
                # Make request
                response = await self.make_request(
                    method, endpoint, params=params, **{k: v for k, v in kwargs.items() if k != "params"}
                )
                
                if response["status"] != "success":
                    break
                
                response_data = response["response"]["data"]
                
                # Extract data based on configuration
                data_path = pagination_config.get("data_path", "data")
                if data_path:
                    page_data = self._extract_nested_value(response_data, data_path)
                else:
                    page_data = response_data
                
                if isinstance(page_data, list):
                    all_data.extend(page_data)
                    
                    # Check if we have more pages
                    if len(page_data) < page_size:
                        break
                else:
                    all_data.append(page_data)
                
                # Check for next page indicators
                has_next = self._check_has_next_page(response_data, pagination_config)
                if not has_next:
                    break
                
                current_page += 1
            
            return {
                "status": "success",
                "data": all_data,
                "metadata": {
                    "total_pages": current_page - 1,
                    "total_items": len(all_data),
                    "pagination_type": pagination_type
                }
            }
            
        except Exception as e:
            logger.error(f"Paginated request failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def webhook_handler(self, webhook_config: Dict[str, Any]) -> Callable:
        """
        Create a webhook handler for receiving API callbacks
        
        Args:
            webhook_config: Webhook configuration
            
        Returns:
            Webhook handler function
        """
        async def handle_webhook(request_data: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Verify webhook signature if configured
                if webhook_config.get("verify_signature"):
                    is_valid = await self._verify_webhook_signature(
                        request_data, webhook_config
                    )
                    if not is_valid:
                        return {"status": "error", "error": "Invalid webhook signature"}
                
                # Transform webhook data if configured
                transform_config = webhook_config.get("transform_config")
                if transform_config:
                    request_data = await self._transform_response(request_data, transform_config)
                
                # Process webhook data
                processed_data = await self._process_webhook_data(request_data, webhook_config)
                
                return {
                    "status": "success",
                    "processed_data": processed_data,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Webhook handling failed: {e}")
                return {
                    "status": "error",
                    "error": str(e)
                }
        
        return handle_webhook
    
    async def monitor_api_health(self) -> Dict[str, Any]:
        """
        Monitor API health and performance
        
        Returns:
            Dictionary with health metrics
        """
        try:
            health_endpoint = self.config.get("health_endpoint", "/health")
            
            start_time = time.time()
            response = await self.make_request("GET", health_endpoint)
            response_time = time.time() - start_time
            
            is_healthy = response["status"] == "success" and response["response"]["status_code"] == 200
            
            # Calculate rate limit usage
            current_time = time.time()
            recent_requests = [t for t in self.request_times if current_time - t < self.rate_limit_window]
            rate_limit_usage = len(recent_requests) / self.rate_limit * 100
            
            return {
                "status": "success",
                "health": {
                    "is_healthy": is_healthy,
                    "response_time": response_time,
                    "api_status": response.get("response", {}).get("status_code"),
                    "rate_limit_usage": rate_limit_usage,
                    "cache_hit_rate": self._calculate_cache_hit_rate(),
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Health monitoring failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "health": {
                    "is_healthy": False,
                    "last_check": datetime.now().isoformat()
                }
            }
    
    # Private methods
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base URL and endpoint"""
        if endpoint.startswith("http"):
            return endpoint
        
        base = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"
    
    async def _prepare_headers(self, additional_headers: Dict[str, str]) -> Dict[str, str]:
        """Prepare headers with authentication"""
        headers = self.default_headers.copy()
        headers.update(additional_headers)
        
        # Add authentication headers
        if self.auth_type == "bearer":
            token = await self._get_bearer_token()
            headers["Authorization"] = f"Bearer {token}"
        elif self.auth_type == "api_key":
            key_header = self.auth_config.get("header_name", "X-API-Key")
            headers[key_header] = self.auth_config.get("api_key")
        elif self.auth_type == "basic":
            username = self.auth_config.get("username")
            password = self.auth_config.get("password")
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
        elif self.auth_type == "custom":
            custom_headers = await self._get_custom_auth_headers()
            headers.update(custom_headers)
        
        return headers
    
    async def _make_request_with_retries(self, 
                                       method: str, 
                                       url: str, 
                                       data: Any, 
                                       params: Dict[str, Any],
                                       headers: Dict[str, str]) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                # Prepare request data
                request_kwargs = {
                    "headers": headers,
                    "params": params
                }
                
                if data is not None:
                    if isinstance(data, (dict, list)):
                        request_kwargs["json"] = data
                    else:
                        request_kwargs["data"] = data
                
                # Make request
                async with self.session.request(method, url, **request_kwargs) as response:
                    response_time = time.time() - start_time
                    
                    # Track request time for rate limiting
                    self.request_times.append(time.time())
                    
                    # Read response content
                    content_type = response.headers.get("Content-Type", "")
                    
                    if "application/json" in content_type:
                        response_data = await response.json()
                    elif "application/xml" in content_type or "text/xml" in content_type:
                        text_content = await response.text()
                        response_data = self._parse_xml(text_content)
                    else:
                        response_data = await response.text()
                    
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "data": response_data,
                        "response_time": response_time
                    }
                    
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    logger.warning(f"Request failed, retrying ({attempt + 1}/{self.max_retries}): {e}")
                else:
                    logger.error(f"Request failed after {self.max_retries} retries: {e}")
        
        raise last_exception or Exception("Request failed")
    
    async def _transform_response(self, data: Any, transform_config: Dict[str, Any]) -> Any:
        """Transform response data based on configuration"""
        try:
            transform_type = transform_config.get("type", "jmespath")
            
            if transform_type == "jmespath":
                expression = transform_config.get("expression")
                if expression:
                    return jmespath.search(expression, data)
            
            elif transform_type == "jsonpath":
                expression = transform_config.get("expression")
                if expression:
                    jsonpath_expr = jsonpath_ng.parse(expression)
                    matches = [match.value for match in jsonpath_expr.find(data)]
                    return matches[0] if len(matches) == 1 else matches
            
            elif transform_type == "custom":
                # Apply custom transformation function
                mapping_rules = transform_config.get("mapping_rules", {})
                return self._apply_custom_mapping(data, mapping_rules)
            
            return data
            
        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            return data
    
    def _apply_custom_mapping(self, data: Any, mapping_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom field mapping rules"""
        if not isinstance(data, dict):
            return data
        
        transformed = {}
        
        for target_field, source_config in mapping_rules.items():
            if isinstance(source_config, str):
                # Simple field mapping
                source_field = source_config
                if source_field in data:
                    transformed[target_field] = data[source_field]
            elif isinstance(source_config, dict):
                # Complex mapping with transformation
                source_field = source_config.get("source")
                default_value = source_config.get("default")
                transform_func = source_config.get("transform")
                
                value = data.get(source_field, default_value)
                
                if transform_func == "uppercase":
                    value = str(value).upper() if value else value
                elif transform_func == "lowercase":
                    value = str(value).lower() if value else value
                elif transform_func == "date_format":
                    # Convert date format
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
                        value = date_obj.strftime(source_config.get("format", "%Y-%m-%d"))
                    except:
                        pass
                
                transformed[target_field] = value
        
        return transformed
    
    async def _apply_rate_limiting(self):
        """Apply rate limiting to requests"""
        current_time = time.time()
        
        # Remove old request times
        self.request_times = [t for t in self.request_times if current_time - t < self.rate_limit_window]
        
        # Check if we're at the rate limit
        if len(self.request_times) >= self.rate_limit:
            sleep_time = self.rate_limit_window - (current_time - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    def _generate_cache_key(self, url: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key for request"""
        cache_string = url
        if params:
            cache_string += "?" + urlencode(sorted(params.items()))
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        if cache_key in self.response_cache:
            cached_data, timestamp = self.response_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                cached_data["metadata"]["cached"] = True
                return cached_data
            else:
                del self.response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response_data: Dict[str, Any]):
        """Cache response data"""
        self.response_cache[cache_key] = (response_data, time.time())
    
    def _extract_nested_value(self, data: Any, path: str) -> Any:
        """Extract nested value using dot notation"""
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return current
    
    def _check_has_next_page(self, response_data: Dict[str, Any], pagination_config: Dict[str, Any]) -> bool:
        """Check if there are more pages available"""
        next_page_indicator = pagination_config.get("next_page_indicator")
        
        if next_page_indicator:
            has_next = self._extract_nested_value(response_data, next_page_indicator)
            return bool(has_next)
        
        return True  # Default to continue if no indicator specified
    
    def _parse_xml(self, xml_content: str) -> Dict[str, Any]:
        """Parse XML content to dictionary"""
        try:
            root = ET.fromstring(xml_content)
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            logger.error(f"XML parsing failed: {e}")
            return {"raw_xml": xml_content}
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result["@attributes"] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result["#text"] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    async def _get_bearer_token(self) -> str:
        """Get bearer token for authentication"""
        # This would implement OAuth2 or other token-based auth
        return self.auth_config.get("token", "")
    
    async def _get_custom_auth_headers(self) -> Dict[str, str]:
        """Get custom authentication headers"""
        # Implement custom authentication logic
        return self.auth_config.get("headers", {})
    
    async def _test_authentication(self):
        """Test authentication configuration"""
        test_endpoint = self.auth_config.get("test_endpoint", "/")
        try:
            response = await self.make_request("GET", test_endpoint)
            if response["status"] != "success":
                raise Exception(f"Authentication test failed: {response.get('error')}")
            logger.info("Authentication test passed")
        except Exception as e:
            logger.warning(f"Authentication test failed: {e}")
    
    async def _verify_webhook_signature(self, request_data: Dict[str, Any], webhook_config: Dict[str, Any]) -> bool:
        """Verify webhook signature"""
        signature_header = webhook_config.get("signature_header", "X-Signature")
        secret = webhook_config.get("secret")
        algorithm = webhook_config.get("algorithm", "sha256")
        
        if not secret:
            return True  # Skip verification if no secret configured
        
        received_signature = request_data.get("headers", {}).get(signature_header)
        if not received_signature:
            return False
        
        # Calculate expected signature
        payload = json.dumps(request_data.get("body", {}), sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            getattr(hashlib, algorithm)
        ).hexdigest()
        
        return hmac.compare_digest(received_signature, expected_signature)
    
    async def _process_webhook_data(self, request_data: Dict[str, Any], webhook_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook data according to configuration"""
        # This would implement webhook-specific processing logic
        return {
            "processed": True,
            "data": request_data,
            "config": webhook_config
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # This would track cache hits/misses for statistics
        return 0.0  # Placeholder
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            logger.info("API integration cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Tool configuration schema
TOOL_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "base_url": {
            "type": "string",
            "description": "Base URL for the API"
        },
        "timeout": {
            "type": "integer",
            "minimum": 1,
            "maximum": 300,
            "default": 30,
            "description": "Request timeout in seconds"
        },
        "max_retries": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10,
            "default": 3,
            "description": "Maximum number of retries"
        },
        "rate_limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10000,
            "default": 100,
            "description": "Rate limit (requests per minute)"
        },
        "authentication": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["none", "bearer", "api_key", "basic", "oauth2", "custom"],
                    "default": "none"
                },
                "token": {"type": "string"},
                "api_key": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string"},
                "header_name": {"type": "string"},
                "headers": {"type": "object"}
            }
        },
        "headers": {
            "type": "object",
            "description": "Default headers for all requests"
        },
        "cache_ttl": {
            "type": "integer",
            "minimum": 0,
            "maximum": 3600,
            "default": 300,
            "description": "Cache TTL in seconds"
        }
    },
    "required": ["base_url"]
}

# Tool input/output schemas
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["request", "batch_requests", "paginated_request", "monitor_health"],
            "description": "Operation to perform"
        },
        "method": {
            "type": "string",
            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "description": "HTTP method"
        },
        "endpoint": {
            "type": "string",
            "description": "API endpoint"
        },
        "data": {
            "type": "object",
            "description": "Request body data"
        },
        "params": {
            "type": "object",
            "description": "Query parameters"
        },
        "headers": {
            "type": "object",
            "description": "Additional headers"
        },
        "transform_config": {
            "type": "object",
            "description": "Data transformation configuration"
        },
        "requests": {
            "type": "array",
            "description": "Batch request configurations"
        },
        "pagination_config": {
            "type": "object",
            "description": "Pagination configuration"
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
        "response": {
            "type": "object",
            "description": "API response data"
        },
        "data": {
            "type": "object",
            "description": "Processed response data"
        },
        "metadata": {
            "type": "object",
            "description": "Request metadata"
        },
        "error": {
            "type": "string",
            "description": "Error message if status is error"
        }
    },
    "required": ["status"]
}
