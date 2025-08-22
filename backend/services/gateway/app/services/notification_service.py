from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models.db_models import Notification
from ..schemas.notification import NotificationCreate
from datetime import datetime

class NotificationService:
    @staticmethod
    async def get_notifications(db: AsyncSession, user_id, skip: int = 0, limit: int = 100) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_notification(db: AsyncSession, notification: NotificationCreate) -> Notification:
        db_notification = Notification(**notification.dict())
        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)
        return db_notification

    @staticmethod
    async def mark_as_read(db: AsyncSession, notification_id: int, user_id) -> Optional[Notification]:
        query = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        result = await db.execute(query)
        db_notification = result.scalar_one_or_none()
        if db_notification:
            db_notification.is_read = True
            db_notification.read_at = datetime.utcnow()
            await db.commit()
            await db.refresh(db_notification)
        return db_notification

    @staticmethod
    async def clear_notifications(db: AsyncSession, user_id) -> int:
        query = delete(Notification).where(Notification.user_id == user_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount
