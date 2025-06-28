from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class ClassBase(SQLModel):
    """
    班级基础模型
    """
    name: str = Field(index=True)
    description: Optional[str] = None


class Class(ClassBase, table=True):
    """
    班级数据库模型
    """
    __tablename__ = "classes"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(foreign_key="users.id")

    # 关系
    creator: User = Relationship(back_populates="created_classes")
    members: List["ClassMember"] = Relationship(back_populates="class_")
    courses: List["Course"] = Relationship(back_populates="class_")


class ClassCreate(ClassBase):
    """
    班级创建模型
    """
    pass


class ClassUpdate(SQLModel):
    """
    班级更新模型
    """
    name: Optional[str] = None
    description: Optional[str] = None


class ClassRead(ClassBase):
    """
    班级读取模型
    """
    id: int
    created_at: datetime
    created_by: int


class ClassMemberBase(SQLModel):
    """
    班级成员基础模型
    """
    class_id: int = Field(foreign_key="classes.id")
    user_id: int = Field(foreign_key="users.id")
    role: str = Field(default="student")  # "teacher" 或 "student"


class ClassMember(ClassMemberBase, table=True):
    """
    班级成员数据库模型
    """
    __tablename__ = "class_members"

    id: Optional[int] = Field(default=None, primary_key=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    class_: Class = Relationship(back_populates="members")
    user: User = Relationship(back_populates="class_memberships")


class ClassMemberCreate(ClassMemberBase):
    """
    班级成员创建模型
    """
    pass


class ClassMemberRead(ClassMemberBase):
    """
    班级成员读取模型
    """
    id: int
    joined_at: datetime 