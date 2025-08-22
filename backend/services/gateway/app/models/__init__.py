"""
Models module - imports all SQLAlchemy models to ensure they're registered
"""

# Import all SQLAlchemy models to ensure they're registered
from .db_models import Project
from .sample_queries import SampleQueryCategory, SampleQuery
from .demo_queries import DemoSampleQuery
from .chat_models import (
    ChatSession,
    ChatMessage,
    AgentCommunication,
    FileAttachment,
    VoiceRecord,
    WebSocketConnection
)

__all__ = [
    # Core models
    "Project",
    "SampleQueryCategory",
    "SampleQuery",
    "DemoSampleQuery",
    
    # Chat models
    "ChatSession",
    "ChatMessage",
    "AgentCommunication",
    "FileAttachment",
    "VoiceRecord",
    "WebSocketConnection"
]
