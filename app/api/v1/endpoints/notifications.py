from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user, get_db
from app.models.notification import Notification, NotificationRead
from app.models.user import User
from app.services.notification_service import mark_notifications_as_read

router = APIRouter()


@router.get("/", response_model=List[NotificationRead])
def read_notifications(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取当前用户的通知列表
    """
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    
    query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
    notifications = db.exec(query).all()
    
    return notifications


@router.get("/{notification_id}", response_model=NotificationRead)
def read_notification(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    notification_id: int = Path(..., title="通知ID"),
) -> Any:
    """
    获取通知详情
    """
    notification = db.get(Notification, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在",
        )
    
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此通知",
        )
    
    return notification


@router.put("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    notification_id: int = Path(..., title="通知ID"),
) -> Any:
    """
    标记通知为已读
    """
    notification = db.get(Notification, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在",
        )
    
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此通知",
        )
    
    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


@router.put("/read-all", response_model=dict)
def mark_all_notifications_read(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    标记所有通知为已读
    """
    count = mark_notifications_as_read(db=db, user_id=current_user.id)
    
    return {"message": f"已标记 {count} 条通知为已读"}


@router.delete("/{notification_id}", response_model=dict)
def delete_notification(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    notification_id: int = Path(..., title="通知ID"),
) -> Any:
    """
    删除通知
    """
    notification = db.get(Notification, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在",
        )
    
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此通知",
        )
    
    db.delete(notification)
    db.commit()
    
    return {"message": "通知已删除"} 