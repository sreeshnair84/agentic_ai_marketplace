"""
Enhanced Chat Service
Integrates with the enhanced model service to provide default chat functionality
Uses LangGraph-compatible models when no specific agents/workflows are selected
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from datetime import datetime

try:
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.callbacks import AsyncCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseMessage = None
    HumanMessage = None
    AIMessage = None
    SystemMessage = None
    BaseLanguageModel = None
    AsyncCallbackHandler = None

from .enhanced_model_service import EnhancedModelService

logger = logging.getLogger(__name__)

class StreamingCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming responses"""
    
    def __init__(self, on_token_callback):
        self.on_token_callback = on_token_callback
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        if self.on_token_callback:
            await self.on_token_callback(token)

class EnhancedChatService:
    """
    Enhanced chat service that uses the enhanced model service for default chat
    Compatible with existing Tools service architecture
    """
    
    def __init__(self, enhanced_model_service: EnhancedModelService):
        self.model_service = enhanced_model_service
        self.system_prompt = self._get_default_system_prompt()
        
        logger.info("Enhanced Chat Service initialized")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the chat service"""
        return """You are a helpful AI assistant integrated into an enterprise AI platform. 
You can help users with:
- General questions and information
- Code assistance and debugging
- Data analysis and insights
- Document summarization and analysis
- Creative writing and brainstorming
- Problem-solving and decision support

You have access to various AI models and tools through the platform. Be helpful, accurate, and professional in your responses.
If a user needs specialized functionality, suggest they create specific agents or workflows for more advanced capabilities.

Always be concise but thorough, and ask clarifying questions when needed."""

    async def chat(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        stream: bool = False,
        model_id: Optional[str] = None
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Handle a chat message using the enhanced model service
        
        Args:
            message: The user's message
            conversation_history: Previous conversation messages
            user_id: ID of the user sending the message
            session_id: Chat session ID
            stream: Whether to stream the response
            model_id: Specific model ID to use (optional)
            
        Returns:
            Response dict or async generator for streaming
        """
        try:
            # Get the LLM model (default or specific)
            if model_id:
                llm_instance = await self.model_service.get_model_instance(model_id)
                llm_data = await self.model_service.get_model(model_id, "llm")
            else:
                llm_data = await self.model_service.get_default_model("llm")
                if llm_data:
                    llm_instance = await self.model_service.get_model_instance(llm_data["id"])
                else:
                    llm_instance = None
            
            if not llm_instance and not llm_data:
                return await self._handle_no_default_model()
            
            # Prepare conversation messages
            messages = await self._prepare_messages(message, conversation_history)
            
            # Generate response
            if stream:
                return self._stream_response(llm_instance, llm_data, messages, user_id, session_id)
            else:
                return await self._generate_response(llm_instance, llm_data, messages, user_id, session_id)
            
        except Exception as e:
            logger.error(f"Error in enhanced chat: {str(e)}")
            return {
                "success": False,
                "error": f"Chat error: {str(e)}",
                "message": "I apologize, but I encountered an error while processing your request.",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _prepare_messages(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]] = None
    ) -> List[BaseMessage]:
        """Prepare messages for the LLM"""
        messages = []
        
        if LANGCHAIN_AVAILABLE:
            # Add system message
            messages.append(SystemMessage(content=self.system_prompt))
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))
            
            # Add current user message
            messages.append(HumanMessage(content=user_message))
        
        return messages

    async def _generate_response(
        self,
        llm_instance: Union[BaseLanguageModel, None],
        llm_data: Dict[str, Any],
        messages: List[BaseMessage],
        user_id: Optional[str],
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """Generate a non-streaming response"""
        try:
            start_time = datetime.utcnow()
            
            if LANGCHAIN_AVAILABLE and llm_instance:
                # Use actual LangChain model
                response = await llm_instance.ainvoke(messages)
                content = response.content if hasattr(response, 'content') else str(response)
            else:
                # Mock response for testing
                content = await self._generate_mock_response(messages[-1].content if messages else "")
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "message": content,
                "role": "assistant",
                "timestamp": end_time.isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "model_info": self._get_model_info(llm_data),
                "metadata": {
                    "response_time": response_time,
                    "token_count": len(content.split()) * 1.3,  # Rough estimate
                    "streaming": False
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "I apologize, but I'm having trouble generating a response right now.",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _stream_response(
        self,
        llm_instance: Union[BaseLanguageModel, None],
        llm_data: Dict[str, Any],
        messages: List[BaseMessage],
        user_id: Optional[str],
        session_id: Optional[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a streaming response"""
        try:
            start_time = datetime.utcnow()
            token_count = 0
            
            if LANGCHAIN_AVAILABLE and llm_instance:
                # Stream from actual LangChain model
                async for chunk in llm_instance.astream(messages):
                    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    if content:
                        token_count += 1
                        yield {
                            "success": True,
                            "chunk": content,
                            "role": "assistant",
                            "timestamp": datetime.utcnow().isoformat(),
                            "user_id": user_id,
                            "session_id": session_id,
                            "streaming": True,
                            "chunk_index": token_count
                        }
            else:
                # Mock streaming response
                async for chunk in self._generate_mock_stream(messages[-1].content if messages else ""):
                    token_count += 1
                    yield {
                        "success": True,
                        "chunk": chunk,
                        "role": "assistant",
                        "timestamp": datetime.utcnow().isoformat(),
                        "user_id": user_id,
                        "session_id": session_id,
                        "streaming": True,
                        "chunk_index": token_count
                    }
            
            # Final metadata chunk
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            yield {
                "success": True,
                "chunk": "",
                "role": "assistant",
                "timestamp": end_time.isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "streaming": True,
                "final": True,
                "model_info": self._get_model_info(llm_data),
                "metadata": {
                    "response_time": response_time,
                    "token_count": token_count,
                    "streaming": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            yield {
                "success": False,
                "error": str(e),
                "message": "I apologize, but I'm having trouble streaming the response.",
                "timestamp": datetime.utcnow().isoformat(),
                "streaming": True,
                "final": True
            }

    async def _generate_mock_response(self, user_message: str) -> str:
        """Generate a mock response for testing"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        responses = {
            "hello": "Hello! I'm your AI assistant. How can I help you today?",
            "how are you": "I'm doing well, thank you for asking! I'm here and ready to help with any questions or tasks you have.",
            "what can you do": "I can help with a wide variety of tasks including answering questions, helping with code, analyzing data, writing, and problem-solving. What would you like to work on?",
            "test": "This is a test response from the enhanced chat service. The system is working properly!",
        }
        
        user_lower = user_message.lower().strip()
        for key, response in responses.items():
            if key in user_lower:
                return response
        
        return f"I understand you're asking about: '{user_message}'. While I don't have a specific response prepared for this topic, I'm here to help however I can. Could you provide more details or clarify what you'd like to know?"

    async def _generate_mock_stream(self, user_message: str) -> AsyncGenerator[str, None]:
        """Generate a mock streaming response"""
        response = await self._generate_mock_response(user_message)
        words = response.split()
        
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate typing delay
            if i == 0:
                yield word
            else:
                yield f" {word}"

    def _get_model_info(self, llm_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get information about the current model"""
        if llm_data:
            return {
                "model_id": llm_data.get("id"),
                "model_name": llm_data.get("name"),
                "provider": llm_data.get("provider"),
                "display_name": llm_data.get("display_name")
            }
        else:
            return {
                "model_name": "default",
                "provider": "mock",
                "class": "MockModel"
            }

    async def _handle_no_default_model(self) -> Dict[str, Any]:
        """Handle the case when no default model is configured"""
        return {
            "success": False,
            "error": "No default model configured",
            "message": """No default language model has been configured for this system. 
Please ask an administrator to:
1. Go to the Tools section
2. Navigate to LLM Models
3. Create and configure at least one LLM model (OpenAI, Azure OpenAI, Google Gemini, or Ollama)
4. Set it as the default model

Once configured, you'll be able to chat with the AI assistant.""",
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": "configure_default_model"
        }

    async def get_conversation_summary(
        self, 
        conversation_history: List[Dict[str, Any]],
        max_length: int = 200
    ) -> Optional[str]:
        """Generate a summary of the conversation"""
        try:
            if not conversation_history:
                return None
            
            # Get the default LLM model
            default_llm_data = await self.model_service.get_default_model("llm")
            if not default_llm_data:
                return None
            
            default_llm = await self.model_service.get_model_instance(default_llm_data["id"])
            
            # Prepare conversation text
            conversation_text = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in conversation_history
            ])
            
            # Create summarization prompt
            summary_prompt = f"""Please provide a brief summary of this conversation in {max_length} characters or less:

{conversation_text}

Summary:"""
            
            if LANGCHAIN_AVAILABLE and default_llm:
                response = await default_llm.ainvoke([HumanMessage(content=summary_prompt)])
                return response.content if hasattr(response, 'content') else str(response)
            else:
                # Simple mock summary
                return f"Conversation with {len(conversation_history)} messages"
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {str(e)}")
            return None

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the chat service"""
        return {
            "status": "healthy",
            "langchain_available": LANGCHAIN_AVAILABLE,
            "system_prompt_length": len(self.system_prompt),
            "model_service_status": self.model_service.get_health_status(),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global enhanced chat service instance
_enhanced_chat_service: Optional[EnhancedChatService] = None

def get_enhanced_chat_service(enhanced_model_service: EnhancedModelService = None) -> EnhancedChatService:
    """Get enhanced chat service instance"""
    global _enhanced_chat_service
    if _enhanced_chat_service is None:
        from .enhanced_model_service import get_enhanced_model_service
        model_service = enhanced_model_service or get_enhanced_model_service()
        _enhanced_chat_service = EnhancedChatService(model_service)
    return _enhanced_chat_service