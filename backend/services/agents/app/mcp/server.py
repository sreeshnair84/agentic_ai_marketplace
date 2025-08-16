"""
MCP Server for A2A Agent Cards Registry
Based on https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/a2a_mcp
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

# Mock imports for MCP - replace with actual MCP imports when available
# from mcp.server.fastmcp import FastMCP
# from mcp.server.fastmcp.utilities.logging import get_logger

logger = logging.getLogger(__name__)

# Configuration
AGENT_CARDS_DIR = Path(__file__).parent.parent / "agent_cards"
MODEL = 'models/embedding-001'  # Gemini embedding model


class MockMCP:
    """Mock MCP server for demonstration"""
    
    def __init__(self):
        self.tools = {}
        self.resources = {}
    
    def tool(self, name: str, description: str):
        def decorator(func):
            self.tools[name] = {
                "function": func,
                "description": description
            }
            return func
        return decorator
    
    def resource(self, uri: str, mime_type: str):
        def decorator(func):
            self.resources[uri] = {
                "function": func,
                "mime_type": mime_type
            }
            return func
        return decorator
    
    def run(self, transport: str = "stdio"):
        logger.info(f"Mock MCP server running with transport: {transport}")


def generate_embeddings(text: str) -> Dict[str, Any]:
    """Generate embeddings for text using Gemini embedding model"""
    try:
        # TODO: Replace with actual Gemini embedding API call
        # For now, use a mock embedding
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # Create a mock embedding vector
        embedding = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, min(len(text_hash), 20), 2)]
        # Pad to desired length
        while len(embedding) < 768:
            embedding.append(0.0)
        
        return {
            "embedding": embedding[:768],
            "model": MODEL
        }
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return {"embedding": [0.0] * 768, "model": MODEL}


def load_agent_cards() -> tuple[List[str], List[Dict[str, Any]]]:
    """Load agent cards from the agent_cards directory"""
    
    card_uris = []
    agent_cards = []
    
    if not AGENT_CARDS_DIR.exists():
        logger.warning(f"Agent cards directory not found: {AGENT_CARDS_DIR}")
        return card_uris, agent_cards
    
    logger.info(f"Loading agent cards from: {AGENT_CARDS_DIR}")
    
    for filename in os.listdir(AGENT_CARDS_DIR):
        if filename.endswith('.json'):
            filepath = AGENT_CARDS_DIR / filename
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    card_uris.append(f'resource://agent_cards/{Path(filename).stem}')
                    agent_cards.append(data)
                    logger.info(f"Loaded agent card: {data.get('name', filename)}")
            except json.JSONDecodeError as e:
                logger.error(f'JSON decode error in {filename}: {e}')
            except OSError as e:
                logger.error(f'Error reading file {filename}: {e}')
            except Exception as e:
                logger.error(f'Unexpected error processing {filename}: {e}')
    
    logger.info(f'Finished loading agent cards. Found {len(agent_cards)} cards.')
    return card_uris, agent_cards


def build_agent_card_embeddings() -> pd.DataFrame:
    """Build embeddings for agent cards for semantic search"""
    
    card_uris, agent_cards = load_agent_cards()
    
    if not agent_cards:
        logger.warning("No agent cards found, returning empty DataFrame")
        return pd.DataFrame()
    
    # Prepare data for embeddings
    embeddings_data = []
    
    for i, (uri, card) in enumerate(zip(card_uris, agent_cards)):
        # Create searchable text from card
        searchable_text = f"{card.get('name', '')} {card.get('description', '')}"
        
        # Add skills information
        skills = card.get('skills', [])
        for skill in skills:
            searchable_text += f" {skill.get('name', '')} {skill.get('description', '')}"
            searchable_text += f" {' '.join(skill.get('tags', []))}"
        
        # Add tags
        tags = card.get('tags', [])
        searchable_text += f" {' '.join(tags)}"
        
        # Generate embedding
        embedding_result = generate_embeddings(searchable_text)
        
        embeddings_data.append({
            'card_uri': uri,
            'agent_card': json.dumps(card),
            'card_embeddings': np.array(embedding_result['embedding']),
            'searchable_text': searchable_text
        })
    
    df = pd.DataFrame(embeddings_data)
    logger.info(f"Built embeddings for {len(df)} agent cards")
    
    return df


# Global DataFrame for agent cards
df = build_agent_card_embeddings()


def serve(host: str = "localhost", port: int = 10100, transport: str = "stdio"):
    """Serve the MCP agent cards registry"""
    
    # Initialize mock MCP server
    mcp = MockMCP()
    
    @mcp.tool(
        name='find_agent',
        description='Finds the most relevant agent card based on a natural language query string.'
    )
    def find_agent(query: str) -> str:
        """Find the most relevant agent for a given query"""
        
        if df.empty:
            return json.dumps({"error": "No agent cards available"})
        
        try:
            # Generate embedding for query
            query_embedding = generate_embeddings(query)
            
            # Calculate similarity scores
            query_vector = np.array(query_embedding['embedding'])
            
            # Calculate dot products with all card embeddings
            dot_products = []
            for card_embedding in df['card_embeddings']:
                dot_product = np.dot(query_vector, card_embedding)
                dot_products.append(dot_product)
            
            dot_products = np.array(dot_products)
            
            # Find best match
            best_match_index = np.argmax(dot_products)
            best_score = dot_products[best_match_index]
            
            logger.info(f'Found best match at index {best_match_index} with score {best_score} for query: {query}')
            
            return df.iloc[best_match_index]['agent_card']
            
        except Exception as e:
            logger.error(f"Error finding agent for query '{query}': {e}")
            return json.dumps({"error": str(e)})
    
    @mcp.tool(
        name='search_flights',
        description='Search for flight options based on criteria'
    )
    def search_flights(origin: str, destination: str, date: str) -> Dict[str, Any]:
        """Mock flight search tool"""
        return {
            "flights": [
                {
                    "airline": "Mock Airlines",
                    "flight_number": "MA123",
                    "origin": origin,
                    "destination": destination,
                    "date": date,
                    "price": "$299",
                    "duration": "2h 30m"
                }
            ]
        }
    
    @mcp.tool(
        name='search_hotels',
        description='Search for hotel options based on criteria'
    )
    def search_hotels(location: str, checkin: str, checkout: str) -> Dict[str, Any]:
        """Mock hotel search tool"""
        return {
            "hotels": [
                {
                    "name": "Mock Hotel",
                    "location": location,
                    "checkin": checkin,
                    "checkout": checkout,
                    "price": "$150/night",
                    "rating": "4.2/5"
                }
            ]
        }
    
    @mcp.tool(
        name='query_db',
        description='Query the travel database for information'
    )
    def query_db(query: str) -> Dict[str, Any]:
        """Mock database query tool"""
        return {
            "query": query,
            "results": [
                {"id": 1, "data": f"Mock result for: {query}"}
            ]
        }
    
    @mcp.resource('resource://agent_cards/list', mime_type='application/json')
    def get_agent_cards() -> Dict[str, Any]:
        """Get list of all agent cards"""
        
        if df.empty:
            return {'agent_cards': []}
        
        return {'agent_cards': df['card_uri'].to_list()}
    
    @mcp.resource('resource://agent_cards/{card_name}', mime_type='application/json')
    def get_agent_card(card_name: str) -> Dict[str, Any]:
        """Get specific agent card by name"""
        
        if df.empty:
            return {'agent_card': []}
        
        try:
            resource_uri = f'resource://agent_cards/{card_name}'
            matching_cards = df.loc[df['card_uri'] == resource_uri, 'agent_card'].to_list()
            
            return {'agent_card': matching_cards}
            
        except Exception as e:
            logger.error(f"Error getting agent card {card_name}: {e}")
            return {'agent_card': [], 'error': str(e)}
    
    logger.info(f'Agent cards MCP Server starting at {host}:{port} with transport {transport}')
    mcp.run(transport=transport)
    
    return mcp


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A2A Agent Cards MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=10100, help="Port to bind to")
    parser.add_argument("--transport", default="stdio", help="Transport type")
    
    args = parser.parse_args()
    
    serve(args.host, args.port, args.transport)
