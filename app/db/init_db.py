import logging

from sqlmodel import Session

from app.core.security import get_password_hash
from app.db.session import get_session
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    初始化数据库，创建默认管理员账户
    """
    with get_session() as db:
        # 创建默认管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            logger.info("创建默认管理员用户成功")


def init_test_data(db: Session) -> None:
    """
    初始化测试数据，仅用于开发环境
    """
    # 创建测试教师用户
    teacher_user = db.query(User).filter(User.username == "teacher").first()
    if not teacher_user:
        teacher_user = User(
            username="teacher",
            email="teacher@example.com",
            hashed_password=get_password_hash("teacher123"),
            role=UserRole.TEACHER,
            is_active=True,
        )
        db.add(teacher_user)
        db.commit()
        db.refresh(teacher_user)
        logger.info("创建测试教师用户成功")

    # 创建测试学生用户
    student_user = db.query(User).filter(User.username == "student").first()
    if not student_user:
        student_user = User(
            username="student",
            email="student@example.com",
            hashed_password=get_password_hash("student123"),
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)
        logger.info("创建测试学生用户成功") 