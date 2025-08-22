from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

def db_async_retry():
    return retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(Exception)
    )
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models.db_models import Notification
from ..schemas.notification import NotificationCreate
from datetime import datetime

class NotificationService:
    @staticmethod
    def db_async_retry():
        return db_async_retry()
    @staticmethod
    @db_async_retry()
    async def get_notifications(db: AsyncSession, user_id, skip: int = 0, limit: int = 100) -> List[Notification]:
        try:
            query = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
            result = await db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    @db_async_retry()
    async def create_notification(db: AsyncSession, notification: NotificationCreate) -> Notification:
        db_notification = Notification(**notification.dict())
        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)
        return db_notification

    @staticmethod
    @db_async_retry()
    async def mark_as_read(db: AsyncSession, notification_id: int, user_id) -> Optional[Notification]:
        query = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        result = await db.execute(query)
        db_notification = result.scalar_one_or_none()
        if db_notification:
            setattr(db_notification, 'is_read', True)
            setattr(db_notification, 'read_at', datetime.utcnow())
            await db.commit()
            await db.refresh(db_notification)
        return db_notification

    @staticmethod
    @db_async_retry()
    async def clear_notifications(db: AsyncSession, user_id) -> int:
        from logging import getLogger
        logger = getLogger(__name__)
        try:
            query = delete(Notification).where(Notification.user_id == user_id)
            result = await db.execute(query)
            await db.commit()
            return result.rowcount
        except Exception as e:
            await db.rollback()
            logger.error(f"Error clearing notifications for user {user_id}: {e}")
            raise
