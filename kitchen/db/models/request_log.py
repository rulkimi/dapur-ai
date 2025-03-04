from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, JSON, Integer, Text
from sqlalchemy.orm import Mapped
from typing import Optional, Dict, Any
from db.base import Base

class RequestLog(Base):
    """Model for storing request trace information."""
    
    __tablename__ = "request_logs"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    request_id: Mapped[str] = Column(String(36), index=True, nullable=False)
    timestamp: Mapped[datetime] = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(UTC))
    method: Mapped[str] = Column(String(10), nullable=False)
    path: Mapped[str] = Column(String(255), nullable=False)
    status_code: Mapped[int] = Column(Integer, nullable=False)
    duration_ms: Mapped[int] = Column(Integer, nullable=False)
    user_id: Mapped[Optional[str]] = Column(String(36), nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = Column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = Column(String(255), nullable=True)
    request_data: Mapped[Optional[Dict[str, Any]]] = Column(JSON, nullable=True)
    response_data: Mapped[Optional[Dict[str, Any]]] = Column(JSON, nullable=True)
    exception: Mapped[Optional[str]] = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<RequestLog {self.request_id} - {self.path} - {self.status_code}>" 