"""
导入所有SQLModel模型，供Alembic创建迁移使用
"""

from sqlmodel import SQLModel

from app.models.user import User
from app.models.class_model import Class, ClassMember
from app.models.course import Course
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.grading import Grading
from app.models.notification import Notification 