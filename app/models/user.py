from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class UserBase(SQLModel):
    """
    用户基础模型
    """
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """
    用户数据库模型
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    created_classes: List["Class"] = Relationship(back_populates="creator")
    class_memberships: List["ClassMember"] = Relationship(back_populates="user")
    courses: List["Course"] = Relationship(back_populates="teacher")
    submissions: List["Submission"] = Relationship(back_populates="student")
    gradings: List["Grading"] = Relationship(back_populates="teacher")
    notifications: List["Notification"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str


class UserUpdate(SQLModel):
    """
    用户更新模型
    """
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """
    用户读取模型
    """
    id: int
    created_at: datetime 