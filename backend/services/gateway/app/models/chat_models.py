"""
Database models for enhanced chat functionality
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


class ChatSession(Base):
    """Chat session with A2A capabilities"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    
    # Session metadata
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")  # active, paused, completed, error
    
    # A2A and capabilities
    a2a_enabled = Column(Boolean, default=True)
    push_notifications_enabled = Column(Boolean, default=True)
    streaming_enabled = Column(Boolean, default=True)
    
    # Session configuration
    session_metadata = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_activity_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    agent_communications = relationship("AgentCommunication", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual chat message with enhanced capabilities"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String, default="user")  # user, agent, system, inter_agent
    role = Column(String, default="user")  # user, assistant, system
    
    # Agent information
    agent_name = Column(String, nullable=True)
    agent_id = Column(String, nullable=True)
    
    # Message status
    status = Column(String, default="sent")  # sent, delivered, read, processing, completed, error
    is_streaming = Column(Boolean, default=False)
    is_complete = Column(Boolean, default=True)
    
    # Enhanced content
    attachments = Column(JSON, nullable=True)  # File attachments
    citations = Column(JSON, nullable=True)    # Source citations
    tool_calls = Column(JSON, nullable=True)   # Tool usage information
    scratchpad = Column(Text, nullable=True)   # Agent thinking process
    
    # A2A trace information
    a2a_trace = Column(JSON, nullable=True)
    parent_message_id = Column(String, ForeignKey("chat_messages.id"), nullable=True)
    
    # Metadata
    message_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    parent_message = relationship("ChatMessage", remote_side=[id])
    child_messages = relationship("ChatMessage", remote_side=[parent_message_id])


class AgentCommunication(Base):
    """Agent-to-Agent communication records"""
    __tablename__ = "agent_communications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Communication details
    source_agent = Column(String, nullable=False)
    target_agent = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    communication_type = Column(String, default="request")  # request, response, notification, error
    
    # Status and timing
    status = Column(String, default="sent")  # sent, received, processed, failed
    latency_ms = Column(Integer, nullable=True)
    
    # Correlation
    correlation_id = Column(String, nullable=True)
    parent_communication_id = Column(String, ForeignKey("agent_communications.id"), nullable=True)
    
    # Metadata
    payload = Column(JSON, nullable=True)
    comm_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="agent_communications")
    parent_communication = relationship("AgentCommunication", remote_side=[id])
    child_communications = relationship("AgentCommunication", remote_side=[parent_communication_id])


class FileAttachment(Base):
    """File attachments for chat messages"""
    __tablename__ = "file_attachments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("chat_messages.id"), nullable=False)
    
    # File details
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    
    # Processing status
    upload_status = Column(String, default="uploading")  # uploading, completed, failed
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # File metadata
    file_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    message = relationship("ChatMessage")


class VoiceRecord(Base):
    """Voice recordings for chat messages"""
    __tablename__ = "voice_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("chat_messages.id"), nullable=False)
    
    # Audio details
    audio_path = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    format = Column(String, default="webm")
    
    # Transcription
    transcription = Column(Text, nullable=True)
    transcription_confidence = Column(String, nullable=True)
    transcription_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Metadata
    voice_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    transcribed_at = Column(DateTime, nullable=True)
    
    # Relationships
    message = relationship("ChatMessage")


class WebSocketConnection(Base):
    """WebSocket connection tracking"""
    __tablename__ = "websocket_connections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    connection_id = Column(String, unique=True, nullable=False)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=True)
    
    # Connection details
    user_id = Column(String, nullable=True)
    client_info = Column(JSON, nullable=True)
    
    # Status
    status = Column(String, default="connected")  # connected, disconnected, error
    last_activity_at = Column(DateTime, default=func.now())
    
    # Statistics
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    
    # Timestamps
    connected_at = Column(DateTime, default=func.now())
    disconnected_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("ChatSession")
