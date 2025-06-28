from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.submission import Submission
from app.models.user import User


class GradingBase(SQLModel):
    """
    作业批改基础模型
    """
    submission_id: int = Field(foreign_key="submissions.id")
    score: float
    feedback: Optional[str] = None


class Grading(GradingBase, table=True):
    """
    作业批改数据库模型
    """
    __tablename__ = "gradings"

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="users.id")
    graded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    submission: Submission = Relationship(back_populates="grading")
    teacher: User = Relationship(back_populates="gradings")


class GradingCreate(GradingBase):
    """
    作业批改创建模型
    """
    pass


class GradingUpdate(SQLModel):
    """
    作业批改更新模型
    """
    score: Optional[float] = None
    feedback: Optional[str] = None


class GradingRead(GradingBase):
    """
    作业批改读取模型
    """
    id: int
    teacher_id: int
    graded_at: datetime
    updated_at: datetime 