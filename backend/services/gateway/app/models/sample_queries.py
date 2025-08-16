"""
Database models for sample queries system
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, DECIMAL, ARRAY, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class SampleQueryCategory(Base):
    """Sample query categories for organizing queries by service and functionality"""
    
    __tablename__ = "sample_query_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    service_type = Column(String(50), nullable=False)  # agents, tools, workflows
    icon = Column(String(100))
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    queries = relationship("SampleQuery", back_populates="category", cascade="all, delete-orphan")


class SampleQuery(Base):
    """Individual sample queries with metadata and analytics"""
    
    __tablename__ = "sample_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("sample_query_categories.id", ondelete="CASCADE"), nullable=False)
    query_text = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    service_type = Column(String(50), nullable=False)  # agents, tools, workflows
    expected_response_type = Column(String(100))
    complexity_level = Column(String(20), nullable=False, default="beginner")  # beginner, intermediate, advanced
    tags = Column(ARRAY(String), default=[])
    context_info = Column(Text)
    example_input = Column(JSON)
    example_output = Column(JSON)
    usage_count = Column(Integer, nullable=False, default=0)
    success_rate = Column(DECIMAL(3, 2), default=0.0)
    avg_response_time = Column(DECIMAL(8, 3), default=0.0)
    last_used_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Relationships
    category = relationship("SampleQueryCategory", back_populates="queries")
    usage_analytics = relationship("QueryUsageAnalytics", back_populates="query", cascade="all, delete-orphan")
    personalizations = relationship("QueryPersonalization", back_populates="query", cascade="all, delete-orphan")


class UserQueryPreferences(Base):
    """User preferences for sample queries display and filtering"""
    
    __tablename__ = "user_query_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)  # References users table
    service_type = Column(String(50))  # Filter preference for specific service
    preferred_complexity = Column(String(20))  # Preferred complexity level
    favorite_categories = Column(ARRAY(String), default=[])  # User's favorite categories
    hidden_categories = Column(ARRAY(String), default=[])  # Categories user wants to hide
    preferred_tags = Column(ARRAY(String), default=[])  # User's preferred tags
    show_quick_start = Column(Boolean, nullable=False, default=True)
    show_contextual = Column(Boolean, nullable=False, default=True)
    max_suggestions = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class QueryUsageAnalytics(Base):
    """Analytics tracking for sample query usage and performance"""
    
    __tablename__ = "query_usage_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("sample_queries.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True))  # Optional user tracking
    session_id = Column(String(255))  # Session tracking
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
    executed = Column(Boolean, nullable=False, default=False)
    execution_time = Column(DECIMAL(8, 3))  # Time taken if executed
    was_successful = Column(Boolean)  # Whether execution was successful
    error_message = Column(Text)  # Error if execution failed
    user_feedback = Column(Integer)  # 1-5 rating from user
    feedback_comment = Column(Text)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    query = relationship("SampleQuery", back_populates="usage_analytics")


class QueryPersonalization(Base):
    """User-specific customizations for sample queries"""
    
    __tablename__ = "query_personalization"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    query_id = Column(UUID(as_uuid=True), ForeignKey("sample_queries.id", ondelete="CASCADE"), nullable=False)
    is_favorite = Column(Boolean, nullable=False, default=False)
    is_hidden = Column(Boolean, nullable=False, default=False)
    custom_description = Column(Text)  # User's custom description
    custom_tags = Column(ARRAY(String), default=[])  # User's custom tags
    last_used_at = Column(DateTime(timezone=True))
    use_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    query = relationship("SampleQuery", back_populates="personalizations")
    
    # Unique constraint
    __table_args__ = (
        {"schema": None},
    )  # SQLAlchemy will handle the unique constraint from the migration
