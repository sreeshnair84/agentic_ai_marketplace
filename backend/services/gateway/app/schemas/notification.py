from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class NotificationBase(BaseModel):
    user_id: UUID
    message: str
    type: str = "info"
    metadata: Optional[Any] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        orm_mode = True
