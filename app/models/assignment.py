from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.course import Course


class AssignmentBase(SQLModel):
    """
    作业基础模型
    """
    title: str = Field(index=True)
    description: Optional[str] = None
    course_id: int = Field(foreign_key="courses.id")
    due_date: datetime
    total_points: int = Field(default=100)
    attachment_url: Optional[str] = None


class Assignment(AssignmentBase, table=True):
    """
    作业数据库模型
    """
    __tablename__ = "assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    course: Course = Relationship(back_populates="assignments")
    submissions: List["Submission"] = Relationship(back_populates="assignment")


class AssignmentCreate(AssignmentBase):
    """
    作业创建模型
    """
    pass


class AssignmentUpdate(SQLModel):
    """
    作业更新模型
    """
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    total_points: Optional[int] = None
    attachment_url: Optional[str] = None


class AssignmentRead(AssignmentBase):
    """
    作业读取模型
    """
    id: int
    created_at: datetime
    updated_at: datetime 