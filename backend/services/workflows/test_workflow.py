"""
Test script for the Default Workflow Agent with Plan and Execute
"""

import asyncio
import json
from default_workflow_agent import DefaultWorkflowAgent, WorkflowConfig

async def test_basic_query():
    """Test basic query processing"""
    print("=== Testing Basic Query Processing ===")
    
    # Initialize workflow agent
    config = WorkflowConfig()
    agent = DefaultWorkflowAgent(config)
    
    try:
        await agent.initialize()
        print("✅ Workflow agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize workflow agent: {e}")
        return
    
    # Test queries
    test_queries = [
        "Help me create a report about sales performance",
        "Find the best workflow for data analysis",
        "I need to use tools for image processing",
        "Connect me with an agent that can handle customer support"
    ]
    
    session_id = "test_session_001"
    
    for i, query in enumerate(test_queries):
        print(f"\n--- Test Query {i+1}: '{query}' ---")
        
        try:
            result = await agent.process_query(
                user_query=query,
                session_id=session_id
            )
            
            print(f"✅ Execution ID: {result['execution_id']}")
            print(f"✅ Success: {result['success']}")
            print(f"✅ Response: {result['final_response']}")
            
            if result.get('step_results'):
                print("📋 Step Results:")
                for step_key, step_data in result['step_results'].items():
                    print(f"  - {step_key}: {step_data.get('status', 'unknown')}")
            
            if result.get('errors'):
                print("⚠️ Errors:")
                for error in result['errors']:
                    print(f"  - {error}")
                    
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        print("-" * 50)

async def test_context_aware_processing():
    """Test context-aware query processing"""
    print("\n=== Testing Context-Aware Processing ===")
    
    config = WorkflowConfig()
    agent = DefaultWorkflowAgent(config)
    
    try:
        await agent.initialize()
        print("✅ Workflow agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize workflow agent: {e}")
        return
    
    # Test with different contexts
    contexts = [
        {
            "type": "workflow",
            "workflow": {
                "id": "data-analysis",
                "display_name": "Data Analysis Workflow",
                "description": "Workflow for data analysis tasks"
            }
        },
        {
            "type": "agent", 
            "agent": {
                "id": "customer-support",
                "display_name": "Customer Support Agent",
                "description": "Agent specialized in customer support"
            }
        },
        {
            "type": "tools",
            "tools": [
                {"id": "image-processor", "display_name": "Image Processor"},
                {"id": "text-analyzer", "display_name": "Text Analyzer"}
            ]
        }
    ]
    
    query = "Process this customer request and provide recommendations"
    session_id = "test_session_context"
    
    for i, context in enumerate(contexts):
        print(f"\n--- Context Test {i+1}: {context['type']} ---")
        print(f"Context: {json.dumps(context, indent=2)}")
        
        try:
            result = await agent.process_query(
                user_query=query,
                session_id=f"{session_id}_{i}",
                context=context
            )
            
            print(f"✅ Execution ID: {result['execution_id']}")
            print(f"✅ Success: {result['success']}")
            print(f"✅ Response: {result['final_response']}")
            
        except Exception as e:
            print(f"❌ Context test failed: {e}")
        
        print("-" * 50)

async def test_memory_functionality():
    """Test memory storage and retrieval"""
    print("\n=== Testing Memory Functionality ===")
    
    config = WorkflowConfig()
    agent = DefaultWorkflowAgent(config)
    
    try:
        await agent.initialize()
        print("✅ Workflow agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize workflow agent: {e}")
        return
    
    session_id = "test_session_memory"
    
    # Test memory storage
    try:
        await agent.memory_manager.store_short_term_memory(
            session_id=session_id,
            execution_id="test_exec_001",
            memory_type="test_memory",
            content="This is a test memory item",
            metadata={"test": True, "priority": "high"}
        )
        print("✅ Short-term memory stored successfully")
        
        await agent.memory_manager.store_long_term_memory(
            session_id=session_id,
            memory_type="workflow_completion",
            content="Completed test workflow successfully",
            metadata={"workflow": "test", "success": True}
        )
        print("✅ Long-term memory stored successfully")
        
        # Test memory retrieval
        short_memory = await agent.memory_manager.get_short_term_memory(
            session_id=session_id,
            limit=10
        )
        print(f"✅ Retrieved {len(short_memory)} short-term memory items")
        
        for item in short_memory:
            print(f"  - {item['type']}: {item['content'][:50]}...")
            
    except Exception as e:
        print(f"❌ Memory test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Default Workflow Agent Tests")
    print("=" * 60)
    
    try:
        await test_basic_query()
        await test_context_aware_processing()
        await test_memory_functionality()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        
if __name__ == "__main__":
    asyncio.run(main())