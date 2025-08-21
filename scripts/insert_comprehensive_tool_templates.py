#!/usr/bin/env python3
"""
Comprehensive Tool Templates Insertion Script
Inserts all modern GenAI tool templates with complete configurations and code templates
"""

import asyncio
import asyncpg
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Database configuration
DATABASE_URL = "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"

# Comprehensive Tool Templates
TOOL_TEMPLATES = [
    {
        "name": "Advanced RAG Tool Template",
        "type": "rag_pipeline",
        "description": "Advanced Retrieval-Augmented Generation with multiple embedding models, reranking, and hybrid search",
        "version": "2.0.0",
        "schema_definition": {
            "type": "object",
            "properties": {
                "vector_database": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string", 
                            "enum": ["pgvector", "chroma", "pinecone", "weaviate", "qdrant", "milvus"],
                            "default": "pgvector"
                        },
                        "connection_string": {"type": "string"},
                        "collection_name": {"type": "string"},
                        "namespace": {"type": "string", "default": "default"}
                    },
                    "required": ["provider", "connection_string", "collection_name"]
                },
                "embedding_model": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string", 
                            "enum": ["openai", "cohere", "huggingface", "google", "azure_openai"],
                            "default": "openai"
                        },
                        "model_name": {
                            "type": "string",
                            "enum": [
                                "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002",
                                "embed-english-v3.0", "embed-multilingual-v3.0",
                                "sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2",
                                "textembedding-gecko", "text-embedding-004"
                            ],
                            "default": "text-embedding-3-small"
                        },
                        "dimensions": {"type": "integer", "default": 1536},
                        "api_key": {"type": "string", "secret": True}
                    },
                    "required": ["provider", "model_name"]
                },
                "chunking_strategy": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["recursive", "semantic", "fixed_size", "sentence", "markdown", "html"],
                            "default": "recursive"
                        },
                        "chunk_size": {"type": "integer", "default": 1000, "minimum": 100, "maximum": 8000},
                        "chunk_overlap": {"type": "integer", "default": 200, "minimum": 0, "maximum": 1000},
                        "separators": {"type": "array", "items": {"type": "string"}},
                        "metadata_fields": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "retrieval_strategy": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["similarity", "mmr", "similarity_score_threshold", "hybrid", "ensemble"],
                            "default": "similarity"
                        },
                        "k": {"type": "integer", "minimum": 1, "maximum": 50, "default": 5},
                        "score_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.7},
                        "lambda_mult": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5},
                        "rerank": {
                            "type": "object",
                            "properties": {
                                "enabled": {"type": "boolean", "default": False},
                                "model": {"type": "string", "default": "cross-encoder/ms-marco-MiniLM-L-6-v2"},
                                "top_k": {"type": "integer", "default": 10}
                            }
                        }
                    }
                },
                "data_ingestion": {
                    "type": "object",
                    "properties": {
                        "supported_formats": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["pdf", "docx", "txt", "md", "html", "csv", "json", "xml"]
                        },
                        "preprocessing": {
                            "type": "object",
                            "properties": {
                                "clean_text": {"type": "boolean", "default": True},
                                "extract_metadata": {"type": "boolean", "default": True},
                                "remove_headers_footers": {"type": "boolean", "default": True},
                                "normalize_whitespace": {"type": "boolean", "default": True}
                            }
                        },
                        "quality_filters": {
                            "type": "object",
                            "properties": {
                                "min_text_length": {"type": "integer", "default": 50},
                                "max_text_length": {"type": "integer", "default": 50000},
                                "language_detection": {"type": "boolean", "default": False},
                                "duplicate_detection": {"type": "boolean", "default": True}
                            }
                        }
                    }
                }
            },
            "required": ["vector_database", "embedding_model", "chunking_strategy", "retrieval_strategy"]
        },
        "default_config": {
            "vector_database": {
                "provider": "pgvector",
                "collection_name": "documents",
                "namespace": "default"
            },
            "embedding_model": {
                "provider": "openai",
                "model_name": "text-embedding-3-small",
                "dimensions": 1536
            },
            "chunking_strategy": {
                "method": "recursive",
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "retrieval_strategy": {
                "method": "similarity",
                "k": 5,
                "score_threshold": 0.7
            }
        },
        "code_template": """
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter, SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.schema import Document
import logging

class AdvancedRAGTool:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.embeddings = self._setup_embeddings()
        self.vectorstore = self._setup_vectorstore()
        self.text_splitter = self._setup_text_splitter()
        self.logger = logging.getLogger(__name__)
    
    def _setup_embeddings(self):
        embedding_config = self.config['embedding_model']
        provider = embedding_config['provider']
        
        if provider == 'openai':
            return OpenAIEmbeddings(
                model=embedding_config['model_name'],
                openai_api_key=embedding_config.get('api_key')
            )
        # Add other providers
        
    def _setup_vectorstore(self):
        db_config = self.config['vector_database']
        if db_config['provider'] == 'pgvector':
            return PGVector(
                connection_string=db_config['connection_string'],
                embedding_function=self.embeddings,
                collection_name=db_config['collection_name']
            )
    
    def _setup_text_splitter(self):
        chunk_config = self.config['chunking_strategy']
        method = chunk_config['method']
        
        if method == 'recursive':
            return RecursiveCharacterTextSplitter(
                chunk_size=chunk_config['chunk_size'],
                chunk_overlap=chunk_config['chunk_overlap']
            )
        elif method == 'semantic':
            return SemanticChunker(self.embeddings)
    
    async def ingest_documents(self, documents: List[Document]) -> Dict[str, Any]:
        \"\"\"Ingest documents into the vector database\"\"\"
        try:
            # Split documents
            chunks = []
            for doc in documents:
                doc_chunks = self.text_splitter.split_documents([doc])
                chunks.extend(doc_chunks)
            
            # Add to vectorstore
            ids = await self.vectorstore.aadd_documents(chunks)
            
            return {
                "status": "success",
                "documents_processed": len(documents),
                "chunks_created": len(chunks),
                "ids": ids
            }
        except Exception as e:
            self.logger.error(f"Error ingesting documents: {e}")
            return {"status": "error", "message": str(e)}
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        \"\"\"Search for relevant documents\"\"\"
        retrieval_config = self.config['retrieval_strategy']
        method = retrieval_config['method']
        k = kwargs.get('k', retrieval_config['k'])
        
        try:
            if method == 'similarity':
                docs = await self.vectorstore.asimilarity_search(query, k=k)
            elif method == 'mmr':
                docs = await self.vectorstore.amax_marginal_relevance_search(
                    query, k=k, lambda_mult=retrieval_config['lambda_mult']
                )
            elif method == 'similarity_score_threshold':
                docs = await self.vectorstore.asimilarity_search_with_score(
                    query, k=k, score_threshold=retrieval_config['score_threshold']
                )
            
            return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        except Exception as e:
            self.logger.error(f"Error searching: {e}")
            return []
    
    async def update_collection(self, collection_name: str = None) -> Dict[str, Any]:
        \"\"\"Update or rebuild collection\"\"\"
        # Implementation for updating collection
        pass
    
    async def delete_collection(self, collection_name: str = None) -> Dict[str, Any]:
        \"\"\"Delete collection and all documents\"\"\"
        # Implementation for deleting collection
        pass
"""
    },
    {
        "name": "Intelligent SQL Agent Template",
        "type": "sql_agent",
        "description": "Advanced SQL agent with natural language processing, query optimization, and safety controls",
        "version": "2.0.0",
        "schema_definition": {
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string", 
                            "enum": ["postgresql", "mysql", "sqlite", "mssql", "oracle", "snowflake", "bigquery"],
                            "default": "postgresql"
                        },
                        "connection_string": {"type": "string"},
                        "schema": {"type": "string"},
                        "ssl_mode": {"type": "string", "enum": ["disable", "require", "verify-ca", "verify-full"], "default": "require"}
                    },
                    "required": ["type", "connection_string"]
                },
                "llm_config": {
                    "type": "object",
                    "properties": {
                        "provider": {"type": "string", "enum": ["openai", "anthropic", "google", "azure_openai"], "default": "openai"},
                        "model": {"type": "string", "default": "gpt-4"},
                        "temperature": {"type": "number", "minimum": 0, "maximum": 2, "default": 0},
                        "max_tokens": {"type": "integer", "default": 2000},
                        "api_key": {"type": "string", "secret": True}
                    }
                },
                "safety": {
                    "type": "object",
                    "properties": {
                        "read_only": {"type": "boolean", "default": True},
                        "allowed_operations": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "default": ["SELECT", "WITH", "EXPLAIN"]
                        },
                        "restricted_tables": {"type": "array", "items": {"type": "string"}},
                        "restricted_columns": {"type": "array", "items": {"type": "string"}},
                        "max_rows": {"type": "integer", "default": 1000},
                        "query_timeout": {"type": "integer", "default": 30}
                    }
                },
                "optimization": {
                    "type": "object",
                    "properties": {
                        "explain_plans": {"type": "boolean", "default": True},
                        "query_caching": {"type": "boolean", "default": True},
                        "index_suggestions": {"type": "boolean", "default": True},
                        "performance_monitoring": {"type": "boolean", "default": True}
                    }
                },
                "schema_awareness": {
                    "type": "object",
                    "properties": {
                        "auto_discover": {"type": "boolean", "default": True},
                        "include_samples": {"type": "boolean", "default": True},
                        "relationship_mapping": {"type": "boolean", "default": True},
                        "metadata_enrichment": {"type": "boolean", "default": True}
                    }
                }
            },
            "required": ["database", "llm_config", "safety"]
        },
        "default_config": {
            "database": {
                "type": "postgresql",
                "ssl_mode": "require"
            },
            "llm_config": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0
            },
            "safety": {
                "read_only": True,
                "allowed_operations": ["SELECT", "WITH", "EXPLAIN"],
                "max_rows": 1000,
                "query_timeout": 30
            }
        },
        "code_template": """
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text, inspect
from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
import logging
import time

class IntelligentSQLAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = self._setup_database()
        self.llm = self._setup_llm()
        self.db = SQLDatabase(self.engine)
        self.agent = self._setup_agent()
        self.logger = logging.getLogger(__name__)
    
    def _setup_database(self):
        db_config = self.config['database']
        return create_engine(
            db_config['connection_string'],
            connect_args={'sslmode': db_config.get('ssl_mode', 'require')}
        )
    
    def _setup_llm(self):
        llm_config = self.config['llm_config']
        if llm_config['provider'] == 'openai':
            return ChatOpenAI(
                model=llm_config['model'],
                temperature=llm_config['temperature'],
                max_tokens=llm_config['max_tokens'],
                openai_api_key=llm_config.get('api_key')
            )
    
    def _setup_agent(self):
        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        return create_sql_agent(
            llm=self.llm,
            toolkit=toolkit,
            verbose=True,
            agent_type="zero-shot-react-description"
        )
    
    def _validate_query(self, query: str) -> Dict[str, Any]:
        \"\"\"Validate query against safety rules\"\"\"
        safety = self.config['safety']
        
        # Check allowed operations
        query_upper = query.upper().strip()
        allowed_ops = [op.upper() for op in safety['allowed_operations']]
        
        if not any(query_upper.startswith(op) for op in allowed_ops):
            return {"valid": False, "reason": "Operation not allowed"}
        
        # Check restricted tables
        for table in safety.get('restricted_tables', []):
            if table.lower() in query.lower():
                return {"valid": False, "reason": f"Access to table '{table}' is restricted"}
        
        return {"valid": True}
    
    async def execute_natural_language_query(self, question: str) -> Dict[str, Any]:
        \"\"\"Execute natural language query\"\"\"
        try:
            start_time = time.time()
            
            # Use agent to generate and execute SQL
            result = await self.agent.arun(question)
            
            execution_time = time.time() - start_time
            
            return {
                "status": "success",
                "question": question,
                "result": result,
                "execution_time": execution_time
            }
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return {"status": "error", "message": str(e)}
    
    async def execute_sql_query(self, query: str) -> Dict[str, Any]:
        \"\"\"Execute SQL query directly\"\"\"
        # Validate query
        validation = self._validate_query(query)
        if not validation['valid']:
            return {"status": "error", "message": validation['reason']}
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = list(result.keys())
                
                # Apply row limit
                max_rows = self.config['safety']['max_rows']
                if len(rows) > max_rows:
                    rows = rows[:max_rows]
                
                return {
                    "status": "success",
                    "query": query,
                    "columns": columns,
                    "rows": [dict(zip(columns, row)) for row in rows],
                    "row_count": len(rows),
                    "truncated": len(rows) == max_rows
                }
        except Exception as e:
            self.logger.error(f"Error executing SQL: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_schema_info(self) -> Dict[str, Any]:
        \"\"\"Get database schema information\"\"\"
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            schema_info = {}
            for table in tables:
                columns = inspector.get_columns(table)
                schema_info[table] = {
                    "columns": [{"name": col['name'], "type": str(col['type'])} for col in columns],
                    "primary_keys": inspector.get_pk_constraint(table)['constrained_columns'],
                    "foreign_keys": [fk['constrained_columns'] for fk in inspector.get_foreign_keys(table)]
                }
            
            return {"status": "success", "schema": schema_info}
        except Exception as e:
            return {"status": "error", "message": str(e)}
"""
    },
    {
        "name": "Advanced Web Scraper Template",
        "type": "web_scraper",
        "description": "Intelligent web scraping tool with content extraction, rate limiting, and data cleaning",
        "version": "2.0.0",
        "schema_definition": {
            "type": "object",
            "properties": {
                "scraping_config": {
                    "type": "object",
                    "properties": {
                        "user_agent": {"type": "string", "default": "Mozilla/5.0 (compatible; AI-Agent/1.0)"},
                        "headers": {"type": "object"},
                        "timeout": {"type": "integer", "default": 30},
                        "retries": {"type": "integer", "default": 3},
                        "respect_robots_txt": {"type": "boolean", "default": True},
                        "javascript_enabled": {"type": "boolean", "default": False}
                    }
                },
                "rate_limiting": {
                    "type": "object",
                    "properties": {
                        "requests_per_second": {"type": "number", "default": 1.0},
                        "concurrent_requests": {"type": "integer", "default": 1},
                        "delay_between_requests": {"type": "number", "default": 1.0}
                    }
                },
                "content_extraction": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "enum": ["css", "xpath", "readability", "auto"], "default": "auto"},
                        "selectors": {"type": "object"},
                        "include_links": {"type": "boolean", "default": True},
                        "include_images": {"type": "boolean", "default": False},
                        "clean_html": {"type": "boolean", "default": True}
                    }
                },
                "data_processing": {
                    "type": "object",
                    "properties": {
                        "remove_duplicates": {"type": "boolean", "default": True},
                        "text_cleaning": {"type": "boolean", "default": True},
                        "language_detection": {"type": "boolean", "default": False},
                        "content_validation": {"type": "boolean", "default": True}
                    }
                },
                "output_format": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["json", "csv", "xml", "markdown"], "default": "json"},
                        "include_metadata": {"type": "boolean", "default": True},
                        "timestamp": {"type": "boolean", "default": True}
                    }
                }
            },
            "required": ["scraping_config", "rate_limiting", "content_extraction"]
        },
        "default_config": {
            "scraping_config": {
                "timeout": 30,
                "retries": 3,
                "respect_robots_txt": True
            },
            "rate_limiting": {
                "requests_per_second": 1.0,
                "delay_between_requests": 1.0
            },
            "content_extraction": {
                "method": "auto",
                "clean_html": True
            }
        },
        "code_template": """
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from readability import Document
from typing import Dict, Any, List, Optional
import time
import logging
from urllib.robotparser import RobotFileParser
import re

class AdvancedWebScraper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.rate_limiter = self._setup_rate_limiter()
    
    def _setup_rate_limiter(self):
        rate_config = self.config['rate_limiting']
        return {
            'requests_per_second': rate_config['requests_per_second'],
            'last_request_time': 0,
            'delay': rate_config['delay_between_requests']
        }
    
    async def __aenter__(self):
        scraping_config = self.config['scraping_config']
        timeout = aiohttp.ClientTimeout(total=scraping_config['timeout'])
        headers = scraping_config.get('headers', {})
        headers.update({'User-Agent': scraping_config['user_agent']})
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _respect_rate_limit(self):
        \"\"\"Enforce rate limiting\"\"\"
        current_time = time.time()
        time_since_last = current_time - self.rate_limiter['last_request_time']
        
        if time_since_last < self.rate_limiter['delay']:
            await asyncio.sleep(self.rate_limiter['delay'] - time_since_last)
        
        self.rate_limiter['last_request_time'] = time.time()
    
    def _check_robots_txt(self, url: str) -> bool:
        \"\"\"Check if URL is allowed by robots.txt\"\"\"
        if not self.config['scraping_config']['respect_robots_txt']:
            return True
        
        try:
            rp = RobotFileParser()
            robots_url = f"{url.split('/')[0]}//{url.split('/')[2]}/robots.txt"
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch(self.config['scraping_config']['user_agent'], url)
        except:
            return True
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        \"\"\"Scrape content from a single URL\"\"\"
        if not self._check_robots_txt(url):
            return {"status": "error", "message": "Blocked by robots.txt"}
        
        await self._respect_rate_limit()
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"status": "error", "message": f"HTTP {response.status}"}
                
                html = await response.text()
                content = self._extract_content(html, url)
                
                return {
                    "status": "success",
                    "url": url,
                    "content": content,
                    "metadata": {
                        "timestamp": time.time(),
                        "status_code": response.status,
                        "headers": dict(response.headers)
                    }
                }
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _extract_content(self, html: str, url: str) -> Dict[str, Any]:
        \"\"\"Extract content from HTML\"\"\"
        extraction_config = self.config['content_extraction']
        method = extraction_config['method']
        
        soup = BeautifulSoup(html, 'html.parser')
        
        if method == 'readability':
            doc = Document(html)
            content = {
                "title": doc.title(),
                "text": BeautifulSoup(doc.summary(), 'html.parser').get_text(),
                "html": doc.summary()
            }
        elif method == 'css':
            content = self._extract_with_selectors(soup, extraction_config.get('selectors', {}))
        else:  # auto method
            content = {
                "title": soup.title.string if soup.title else "",
                "text": soup.get_text(),
                "headings": [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])],
                "paragraphs": [p.get_text() for p in soup.find_all('p')]
            }
        
        if extraction_config['include_links']:
            content['links'] = [{'text': a.get_text(), 'href': a.get('href')} 
                              for a in soup.find_all('a', href=True)]
        
        if extraction_config['include_images']:
            content['images'] = [{'alt': img.get('alt', ''), 'src': img.get('src')} 
                               for img in soup.find_all('img', src=True)]
        
        if self.config['data_processing']['text_cleaning']:
            content = self._clean_content(content)
        
        return content
    
    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, Any]:
        \"\"\"Extract content using CSS selectors\"\"\"
        content = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            content[key] = [elem.get_text().strip() for elem in elements]
        return content
    
    def _clean_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Clean extracted content\"\"\"
        if 'text' in content:
            # Remove extra whitespace
            content['text'] = re.sub(r'\s+', ' ', content['text']).strip()
        
        return content
    
    async def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        \"\"\"Scrape multiple URLs\"\"\"
        results = []
        for url in urls:
            result = await self.scrape_url(url)
            results.append(result)
        return results
"""
    },
    {
        "name": "Universal API Wrapper Template",
        "type": "api_integration",
        "description": "Universal API integration tool supporting REST, GraphQL, and webhook endpoints",
        "version": "2.0.0",
        "schema_definition": {
            "type": "object",
            "properties": {
                "api_config": {
                    "type": "object",
                    "properties": {
                        "base_url": {"type": "string"},
                        "api_type": {"type": "string", "enum": ["rest", "graphql", "soap", "webhook"], "default": "rest"},
                        "version": {"type": "string"},
                        "timeout": {"type": "integer", "default": 30}
                    },
                    "required": ["base_url", "api_type"]
                },
                "authentication": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["none", "api_key", "bearer_token", "basic_auth", "oauth2", "custom"],
                            "default": "none"
                        },
                        "api_key": {"type": "string", "secret": True},
                        "api_key_header": {"type": "string", "default": "X-API-Key"},
                        "bearer_token": {"type": "string", "secret": True},
                        "username": {"type": "string"},
                        "password": {"type": "string", "secret": True},
                        "oauth2_config": {"type": "object"},
                        "custom_headers": {"type": "object"}
                    }
                },
                "request_config": {
                    "type": "object",
                    "properties": {
                        "default_headers": {"type": "object"},
                        "rate_limit": {"type": "integer", "default": 100},
                        "retry_config": {
                            "type": "object",
                            "properties": {
                                "max_retries": {"type": "integer", "default": 3},
                                "backoff_factor": {"type": "number", "default": 1.0},
                                "retry_on_status": {"type": "array", "items": {"type": "integer"}}
                            }
                        }
                    }
                },
                "response_config": {
                    "type": "object",
                    "properties": {
                        "expected_format": {"type": "string", "enum": ["json", "xml", "text", "binary"], "default": "json"},
                        "success_status_codes": {"type": "array", "items": {"type": "integer"}, "default": [200, 201, 202]},
                        "error_handling": {"type": "string", "enum": ["raise", "return", "log"], "default": "return"},
                        "response_transformation": {"type": "object"}
                    }
                },
                "endpoints": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                                "description": {"type": "string"},
                                "parameters": {"type": "object"},
                                "required_params": {"type": "array", "items": {"type": "string"}},
                                "response_schema": {"type": "object"}
                            }
                        }
                    }
                }
            },
            "required": ["api_config", "authentication"]
        },
        "default_config": {
            "api_config": {
                "api_type": "rest",
                "timeout": 30
            },
            "authentication": {
                "method": "none"
            },
            "request_config": {
                "rate_limit": 100
            },
            "response_config": {
                "expected_format": "json",
                "error_handling": "return"
            }
        },
        "code_template": """
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
import json
import time
import logging
from urllib.parse import urljoin, urlencode

class UniversalAPIWrapper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.rate_limiter = self._setup_rate_limiter()
    
    def _setup_rate_limiter(self):
        return {
            'requests': [],
            'limit': self.config['request_config'].get('rate_limit', 100),
            'window': 60  # 1 minute window
        }
    
    async def __aenter__(self):
        auth_headers = self._get_auth_headers()
        default_headers = self.config['request_config'].get('default_headers', {})
        headers = {**default_headers, **auth_headers}
        
        timeout = aiohttp.ClientTimeout(total=self.config['api_config']['timeout'])
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        \"\"\"Generate authentication headers\"\"\"
        auth_config = self.config['authentication']
        method = auth_config['method']
        
        if method == 'api_key':
            header_name = auth_config.get('api_key_header', 'X-API-Key')
            return {header_name: auth_config['api_key']}
        elif method == 'bearer_token':
            return {'Authorization': f"Bearer {auth_config['bearer_token']}"}
        elif method == 'basic_auth':
            import base64
            credentials = f"{auth_config['username']}:{auth_config['password']}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {'Authorization': f"Basic {encoded}"}
        elif method == 'custom':
            return auth_config.get('custom_headers', {})
        
        return {}
    
    async def _enforce_rate_limit(self):
        \"\"\"Enforce rate limiting\"\"\"
        current_time = time.time()
        window_start = current_time - self.rate_limiter['window']
        
        # Remove old requests
        self.rate_limiter['requests'] = [
            req_time for req_time in self.rate_limiter['requests'] 
            if req_time > window_start
        ]
        
        # Check if we're under the limit
        if len(self.rate_limiter['requests']) >= self.rate_limiter['limit']:
            sleep_time = self.rate_limiter['requests'][0] + self.rate_limiter['window'] - current_time
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.rate_limiter['requests'].append(current_time)
    
    async def call_endpoint(self, endpoint_name: str, **kwargs) -> Dict[str, Any]:
        \"\"\"Call a predefined endpoint\"\"\"
        endpoints = self.config.get('endpoints', {})
        if endpoint_name not in endpoints:
            return {"status": "error", "message": f"Endpoint '{endpoint_name}' not found"}
        
        endpoint_config = endpoints[endpoint_name]
        
        # Validate required parameters
        required_params = endpoint_config.get('required_params', [])
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            return {"status": "error", "message": f"Missing required parameters: {missing_params}"}
        
        # Make request
        return await self.make_request(
            method=endpoint_config['method'],
            path=endpoint_config['path'],
            **kwargs
        )
    
    async def make_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        \"\"\"Make a generic API request\"\"\"
        await self._enforce_rate_limit()
        
        base_url = self.config['api_config']['base_url']
        url = urljoin(base_url, path)
        
        # Prepare request parameters
        params = kwargs.get('params', {})
        data = kwargs.get('data')
        json_data = kwargs.get('json')
        
        retry_config = self.config['request_config'].get('retry_config', {})
        max_retries = retry_config.get('max_retries', 3)
        backoff_factor = retry_config.get('backoff_factor', 1.0)
        
        for attempt in range(max_retries + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data
                ) as response:
                    result = await self._process_response(response)
                    
                    # Check if retry is needed
                    if (attempt < max_retries and 
                        response.status in retry_config.get('retry_on_status', [500, 502, 503, 504])):
                        await asyncio.sleep(backoff_factor * (2 ** attempt))
                        continue
                    
                    return result
                    
            except Exception as e:
                if attempt == max_retries:
                    self.logger.error(f"Request failed after {max_retries + 1} attempts: {e}")
                    return {"status": "error", "message": str(e)}
                
                await asyncio.sleep(backoff_factor * (2 ** attempt))
    
    async def _process_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        \"\"\"Process API response\"\"\"
        response_config = self.config['response_config']
        expected_format = response_config['expected_format']
        success_codes = response_config['success_status_codes']
        
        # Check status code
        if response.status not in success_codes:
            error_text = await response.text()
            return {
                "status": "error",
                "status_code": response.status,
                "message": error_text
            }
        
        # Parse response based on expected format
        try:
            if expected_format == 'json':
                content = await response.json()
            elif expected_format == 'xml':
                import xml.etree.ElementTree as ET
                text = await response.text()
                content = ET.fromstring(text)
            elif expected_format == 'text':
                content = await response.text()
            elif expected_format == 'binary':
                content = await response.read()
            
            return {
                "status": "success",
                "status_code": response.status,
                "content": content,
                "headers": dict(response.headers)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to parse response: {e}"}
    
    async def test_connection(self) -> Dict[str, Any]:
        \"\"\"Test API connection\"\"\"
        try:
            # Try a simple GET request to the base URL
            result = await self.make_request("GET", "/")
            return {"status": "success", "message": "Connection successful", "details": result}
        except Exception as e:
            return {"status": "error", "message": f"Connection failed: {e}"}
"""
    },
    # Add more tool templates...
]

async def insert_tool_templates():
    """Insert all tool templates into the database"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Get admin user ID (create if doesn't exist)
        admin_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", 
            "admin@example.com"
        )
        
        if not admin_user:
            admin_id = await conn.fetchval(
                """INSERT INTO users (email, username, full_name, is_active, role) 
                   VALUES ($1, $2, $3, $4, $5) RETURNING id""",
                "admin@example.com", "admin", "System Administrator", True, "admin"
            )
        else:
            admin_id = admin_user['id']
        
        # Insert tool templates
        for template in TOOL_TEMPLATES:
            try:
                # Check if template already exists
                existing = await conn.fetchrow(
                    "SELECT id FROM tool_templates WHERE name = $1",
                    template['name']
                )
                
                if existing:
                    print(f"Template '{template['name']}' already exists, updating...")
                    await conn.execute(
                        """UPDATE tool_templates 
                           SET description = $2, schema_definition = $3, default_config = $4, 
                               version = $5, updated_at = CURRENT_TIMESTAMP
                           WHERE name = $1""",
                        template['name'], template['description'], 
                        json.dumps(template['schema_definition']),
                        json.dumps(template['default_config']),
                        template['version']
                    )
                else:
                    print(f"Inserting template '{template['name']}'...")
                    await conn.execute(
                        """INSERT INTO tool_templates 
                           (name, type, description, schema_definition, default_config, version, 
                            documentation, created_by)
                           VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                        template['name'], template['type'], template['description'],
                        json.dumps(template['schema_definition']),
                        json.dumps(template['default_config']),
                        template['version'], template.get('code_template', ''), admin_id
                    )
                
                print(f"✓ Processed template: {template['name']}")
                
            except Exception as e:
                print(f"✗ Error processing template {template['name']}: {e}")
                continue
    
    finally:
        await conn.close()

if __name__ == "__main__":
    print("Inserting comprehensive tool templates...")
    asyncio.run(insert_tool_templates())
    print("Tool templates insertion completed!")
