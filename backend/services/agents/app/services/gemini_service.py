"""
Gemini AI service implementation
"""

import google.generativeai as genai
from typing import Dict, Any, Optional, List, AsyncGenerator
import asyncio
import logging
from datetime import datetime

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.settings = get_settings()
        if self.settings.GOOGLE_API_KEY:
            genai.configure(api_key=self.settings.GOOGLE_API_KEY)
        
        # Default model configurations
        self.model_configs = {
            "gemini-1.5-pro": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
                "safety_settings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            },
            "gemini-1.5-flash": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 4096,
                "safety_settings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            }
        }
    
    def get_model(self, model_name: str = "gemini-1.5-pro", custom_config: Optional[Dict[str, Any]] = None):
        """Get configured Gemini model"""
        
        # Get base configuration
        config = self.model_configs.get(model_name, self.model_configs["gemini-1.5-pro"]).copy()
        
        # Apply custom configuration
        if custom_config:
            config.update(custom_config)
        
        # Create generation config
        generation_config = genai.types.GenerationConfig(
            temperature=config.get("temperature", 0.7),
            top_p=config.get("top_p", 0.9),
            top_k=config.get("top_k", 40),
            max_output_tokens=config.get("max_output_tokens", 8192),
        )
        
        # Create model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=config.get("safety_settings", [])
        )
        
        return model
    
    async def generate_response(
        self,
        prompt: str,
        model_name: str = "gemini-1.5-pro",
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response using Gemini"""
        
        try:
            model = self.get_model(model_name, custom_config)
            
            # Prepare conversation
            chat_messages = []
            
            # Add system prompt if provided
            if system_prompt:
                chat_messages.append({"role": "system", "parts": [system_prompt]})
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    chat_messages.append({
                        "role": msg.get("role", "user"),
                        "parts": [msg.get("content", "")]
                    })
            
            # Add current prompt
            chat_messages.append({"role": "user", "parts": [prompt]})
            
            # Start chat or generate content
            if len(chat_messages) > 1:
                chat = model.start_chat(history=chat_messages[:-1])
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: chat.send_message(prompt)
                )
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: model.generate_content(prompt)
                )
            
            # Extract response data
            result = {
                "content": response.text,
                "model": model_name,
                "usage": {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                },
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add safety ratings if available
            if response.candidates and response.candidates[0].safety_ratings:
                result["safety_ratings"] = [
                    {
                        "category": rating.category.name,
                        "probability": rating.probability.name
                    }
                    for rating in response.candidates[0].safety_ratings
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            raise
    
    async def generate_streaming_response(
        self,
        prompt: str,
        model_name: str = "gemini-1.5-pro",
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming response using Gemini"""
        
        try:
            model = self.get_model(model_name, custom_config)
            
            # Prepare full prompt
            full_prompt = ""
            if system_prompt:
                full_prompt += f"System: {system_prompt}\n\n"
            
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user").title()
                    content = msg.get("content", "")
                    full_prompt += f"{role}: {content}\n"
            
            full_prompt += f"User: {prompt}\nAssistant:"
            
            # Generate streaming response
            def generate_stream():
                return model.generate_content(full_prompt, stream=True)
            
            response_stream = await asyncio.get_event_loop().run_in_executor(
                None, generate_stream
            )
            
            # Yield chunks
            for chunk in response_stream:
                if chunk.text:
                    yield {
                        "content": chunk.text,
                        "model": model_name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "is_complete": False
                    }
            
            # Final chunk
            yield {
                "content": "",
                "model": model_name,
                "timestamp": datetime.utcnow().isoformat(),
                "is_complete": True
            }
            
        except Exception as e:
            logger.error(f"Error generating streaming Gemini response: {e}")
            yield {
                "error": str(e),
                "model": model_name,
                "timestamp": datetime.utcnow().isoformat(),
                "is_complete": True
            }
    
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "general",
        model_name: str = "gemini-1.5-pro"
    ) -> Dict[str, Any]:
        """Analyze content using Gemini"""
        
        analysis_prompts = {
            "general": "Analyze the following content and provide insights:",
            "sentiment": "Analyze the sentiment of the following content:",
            "summarize": "Provide a concise summary of the following content:",
            "extract_entities": "Extract named entities from the following content:",
            "classify": "Classify the topic/category of the following content:"
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        prompt += f"\n\n{content}"
        
        return await self.generate_response(prompt, model_name)
    
    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models"""
        try:
            models = genai.list_models()
            return [model.name for model in models if 'generateContent' in model.supported_generation_methods]
        except Exception as e:
            logger.error(f"Error listing Gemini models: {e}")
            return list(self.model_configs.keys())
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model_name: str = "gemini-1.5-pro") -> float:
        """Estimate cost for Gemini API usage"""
        
        # Gemini pricing (as of 2024 - update as needed)
        pricing = {
            "gemini-1.5-pro": {
                "input_per_1k": 0.000125,  # $0.000125 per 1K input tokens
                "output_per_1k": 0.000375  # $0.000375 per 1K output tokens
            },
            "gemini-1.5-flash": {
                "input_per_1k": 0.000075,   # $0.000075 per 1K input tokens
                "output_per_1k": 0.0003     # $0.0003 per 1K output tokens
            }
        }
        
        model_pricing = pricing.get(model_name, pricing["gemini-1.5-pro"])
        
        input_cost = (input_tokens / 1000) * model_pricing["input_per_1k"]
        output_cost = (output_tokens / 1000) * model_pricing["output_per_1k"]
        
        return input_cost + output_cost


# Global Gemini service instance
gemini_service = GeminiService()
