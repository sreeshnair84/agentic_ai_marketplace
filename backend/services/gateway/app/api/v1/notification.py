from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...core.database import get_database
from ...schemas.notification import NotificationRead, NotificationCreate
from ...services.notification_service import NotificationService

router = APIRouter()

@router.get("/notifications", response_model=List[NotificationRead])
async def get_notifications(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_database)
):
    return await NotificationService.get_notifications(db, user_id, skip, limit)

@router.post("/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_database)
):
    return await NotificationService.create_notification(db, notification)

@router.post("/notifications/{notification_id}/read", response_model=NotificationRead)
async def mark_as_read(
    notification_id: int,
    user_id: UUID,
    db: AsyncSession = Depends(get_database)
):
    notif = await NotificationService.mark_as_read(db, notification_id, user_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

@router.post("/notifications/clear", response_model=int)
async def clear_notifications(
    user_id: UUID,
    db: AsyncSession = Depends(get_database)
):
    return await NotificationService.clear_notifications(db, user_id)
