from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.assignment import Assignment
from app.models.user import User


class SubmissionStatus(str, Enum):
    SUBMITTED = "submitted"
    GRADED = "graded"


class SubmissionBase(SQLModel):
    """
    作业提交基础模型
    """
    assignment_id: int = Field(foreign_key="assignments.id")
    comments: Optional[str] = None
    file_url: str


class Submission(SubmissionBase, table=True):
    """
    作业提交数据库模型
    """
    __tablename__ = "submissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="users.id")
    submission_time: datetime = Field(default_factory=datetime.utcnow)
    status: SubmissionStatus = Field(default=SubmissionStatus.SUBMITTED)

    # 关系
    assignment: Assignment = Relationship(back_populates="submissions")
    student: User = Relationship(back_populates="submissions")
    grading: Optional["Grading"] = Relationship(back_populates="submission")


class SubmissionCreate(SubmissionBase):
    """
    作业提交创建模型
    """
    pass


class SubmissionUpdate(SQLModel):
    """
    作业提交更新模型
    """
    comments: Optional[str] = None
    file_url: Optional[str] = None


class SubmissionRead(SubmissionBase):
    """
    作业提交读取模型
    """
    id: int
    student_id: int
    submission_time: datetime
    status: SubmissionStatus 