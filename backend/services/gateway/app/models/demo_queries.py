"""
Simple database service for demo sample queries
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class DemoSampleQuery(Base):
    """Simple demo sample queries for demonstrations"""
    
    __tablename__ = "demo_sample_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_type = Column(String(50), nullable=False)  # agents, tools, workflows
    category = Column(String(100), nullable=False)
    query_text = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    complexity_level = Column(String(20), nullable=False, default="beginner")
    tags = Column(ARRAY(String), default=[])
    is_featured = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
