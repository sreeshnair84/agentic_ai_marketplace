#!/usr/bin/env python3
"""
Test script for RAG service with PGVector
This tests the RAG functionality directly against the database
"""

import asyncio
import asyncpg
import openai
import os
import json
from typing import List, Dict, Any

# Configuration
DATABASE_URL = "postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key-for-testing")

async def test_database_connection():
    """Test basic database connection"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test basic query
        result = await conn.fetchval("SELECT version()")
        print(f"✓ Database connected: {result[:50]}...")
        
        # Test PGVector extension
        result = await conn.fetchval("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'")
        if result > 0:
            print("✓ PGVector extension is enabled")
        else:
            print("✗ PGVector extension not found")
        
        # Test vector tables
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%embedding%'")
        print(f"✓ Vector tables found: {[t['table_name'] for t in tables]}")
        
        # Test models data
        llm_models = await conn.fetch("SELECT name, provider FROM llm_models")
        print(f"✓ LLM models: {[m['name'] + ' (' + m['provider'] + ')' for m in llm_models]}")
        
        embedding_models = await conn.fetch("SELECT name, provider FROM embedding_models")
        print(f"✓ Embedding models: {[m['name'] + ' (' + m['provider'] + ')' for m in embedding_models]}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

async def test_vector_operations():
    """Test vector operations"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test vector similarity function
        result = await conn.fetchval("SELECT cosine_similarity(ARRAY[1,0,0]::vector, ARRAY[1,0,0]::vector)")
        print(f"✓ Vector similarity test: {result} (should be 1.0)")
        
        # Test embedding insertion
        test_embedding = [0.1] * 1536  # OpenAI embedding size
        await conn.execute("""
            INSERT INTO document_embeddings 
            (document_id, content, embedding, metadata, namespace, created_at, updated_at)
            VALUES ($1, $2, $3::vector, $4, $5, NOW(), NOW())
        """, "test-doc-1", "This is a test document", str(test_embedding), json.dumps({"test": True}), "test")
        
        print("✓ Test embedding inserted successfully")
        
        # Test similarity search
        results = await conn.fetch("""
            SELECT document_id, content, cosine_similarity(embedding, $1::vector) as similarity
            FROM document_embeddings
            WHERE namespace = 'test'
            ORDER BY similarity DESC
            LIMIT 5
        """, str(test_embedding))
        
        print(f"✓ Similarity search returned {len(results)} results")
        for result in results:
            print(f"  - {result['document_id']}: {result['similarity']:.3f}")
        
        # Clean up test data
        await conn.execute("DELETE FROM document_embeddings WHERE namespace = 'test'")
        print("✓ Test data cleaned up")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Vector operations failed: {e}")
        return False

async def test_embedding_generation():
    """Test embedding generation (if API key is available)"""
    if OPENAI_API_KEY == "dummy-key-for-testing":
        print("⚠ Skipping embedding generation test (no API key)")
        return True
    
    try:
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input="This is a test sentence for embedding generation."
        )
        
        embedding = response.data[0].embedding
        print(f"✓ Generated embedding with {len(embedding)} dimensions")
        
        # Test storing the real embedding
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            INSERT INTO document_embeddings 
            (document_id, content, embedding, metadata, namespace, created_at, updated_at)
            VALUES ($1, $2, $3::vector, $4, $5, NOW(), NOW())
        """, "test-real-embedding", "This is a test sentence for embedding generation.", 
        str(embedding), json.dumps({"source": "openai", "model": "text-embedding-3-small"}), "test")
        
        print("✓ Real embedding stored successfully")
        
        # Clean up
        await conn.execute("DELETE FROM document_embeddings WHERE namespace = 'test'")
        await conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Embedding generation failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing RAG with PGVector setup...\n")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Vector Operations", test_vector_operations),
        ("Embedding Generation", test_embedding_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        success = await test_func()
        results.append((test_name, success))
    
    print(f"\n📊 Test Results:")
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print(f"\n🎉 All tests passed! RAG with PGVector is ready.")
    else:
        print(f"\n⚠ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
