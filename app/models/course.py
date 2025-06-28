from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.class_model import Class
from app.models.user import User


class CourseStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class CourseBase(SQLModel):
    """
    课程基础模型
    """
    name: str = Field(index=True)
    description: Optional[str] = None
    class_id: int = Field(foreign_key="classes.id")
    status: CourseStatus = Field(default=CourseStatus.ACTIVE)


class Course(CourseBase, table=True):
    """
    课程数据库模型
    """
    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    class_: Class = Relationship(back_populates="courses")
    teacher: User = Relationship(back_populates="courses")
    assignments: List["Assignment"] = Relationship(back_populates="course")


class CourseCreate(CourseBase):
    """
    课程创建模型
    """
    pass


class CourseUpdate(SQLModel):
    """
    课程更新模型
    """
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CourseStatus] = None


class CourseRead(CourseBase):
    """
    课程读取模型
    """
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime 