from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class NotificationType(str, Enum):
    ASSIGNMENT = "assignment"  # 新作业发布
    FEEDBACK = "feedback"      # 作业批改反馈
    REMINDER = "reminder"      # 作业截止提醒


class NotificationBase(SQLModel):
    """
    通知基础模型
    """
    user_id: int = Field(foreign_key="users.id")
    title: str
    content: str
    type: NotificationType
    is_read: bool = Field(default=False)


class Notification(NotificationBase, table=True):
    """
    通知数据库模型
    """
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    user: User = Relationship(back_populates="notifications")


class NotificationCreate(NotificationBase):
    """
    通知创建模型
    """
    pass


class NotificationUpdate(SQLModel):
    """
    通知更新模型
    """
    is_read: Optional[bool] = None


class NotificationRead(NotificationBase):
    """
    通知读取模型
    """
    id: int
    created_at: datetime 